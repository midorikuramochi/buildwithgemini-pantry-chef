"""Firestore backend tools for PantryChef recipes and favorites.

PROJECT_ID is strictly hardcoded to "qwiklabs-gcp-03-894441c8585c".
Do not read it from google.auth.default() or GOOGLE_CLOUD_PROJECT because
on Agent Platform those return the numeric project number, which breaks Firestore.
"""

from datetime import datetime, timezone
import re
from typing import Any
from google.cloud import firestore
from google.cloud.firestore import FieldFilter

PROJECT_ID = "qwiklabs-gcp-03-894441c8585c"
COLLECTION_NAME = "recipes"

_db_client: firestore.Client | None = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client with the hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", cleaned).strip("-_")


def search_recipes(
    ingredients: list[str] | None = None, query: str = ""
) -> list[dict[str, Any]]:
    """Searches recipes in the catalog matching specific ingredients or keywords.

    Args:
        ingredients: Optional list of available ingredients to match (e.g. ['chicken', 'broccoli']).
        query: Optional keyword query to match against recipe titles or descriptions (e.g. 'pasta', 'tacos').

    Returns:
        A list of matching recipe summaries.
    """
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).stream()

    results = []
    norm_ingredients = (
        [ing.strip().lower() for ing in ingredients] if ingredients else []
    )
    norm_query = query.strip().lower() if query else ""

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        recipe_ingredients = [str(i).lower() for i in data.get("ingredients", [])]
        title = data.get("title", "").lower()
        desc = data.get("description", "").lower()

        matched = False
        match_score = 0

        if norm_ingredients:
            ing_matches = sum(
                1
                for req in norm_ingredients
                if any(req in item or item in req for item in recipe_ingredients)
            )
            if ing_matches > 0:
                matched = True
                match_score += ing_matches

        if norm_query:
            if (
                norm_query in title
                or norm_query in desc
                or any(norm_query in item for item in recipe_ingredients)
            ):
                matched = True
                match_score += 2

        if not norm_ingredients and not norm_query:
            matched = True

        if matched:
            results.append(
                (
                    match_score,
                    {
                        "id": data["id"],
                        "title": data.get("title"),
                        "description": data.get("description"),
                        "prep_time_minutes": data.get("prep_time_minutes"),
                        "cook_time_minutes": data.get("cook_time_minutes"),
                        "difficulty": data.get("difficulty"),
                        "dietary_tags": data.get("dietary_tags", []),
                        "ingredients": data.get("ingredients", []),
                        "is_favorite": data.get("is_favorite", False),
                    },
                )
            )

    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]


def get_recipe_details(recipe_id: str) -> dict[str, Any]:
    """Retrieves the complete recipe details, including step-by-step instructions.

    Args:
        recipe_id: The unique identifier of the recipe (e.g. 'chicken-broccoli-stir-fry').

    Returns:
        The full recipe dictionary with ingredients and instructions, or an error dict if not found.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(recipe_id).get()
    if not doc.exists:
        return {"error": f"Recipe with id '{recipe_id}' not found."}

    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_favorite_recipe(
    title: str,
    ingredients: list[str],
    instructions: list[str],
    prep_time_minutes: int = 15,
    cook_time_minutes: int = 15,
    servings: int = 2,
    difficulty: str = "Easy",
    dietary_tags: list[str] | None = None,
) -> dict[str, Any]:
    """Saves a recipe to the catalog as a favorite dish.

    Args:
        title: The recipe title (e.g. 'Avocado Toast with Poached Egg').
        ingredients: The list of ingredients with quantities or descriptions.
        instructions: Step-by-step cooking instructions.
        prep_time_minutes: Preparation time in minutes.
        cook_time_minutes: Cooking time in minutes.
        servings: Number of servings.
        difficulty: 'Easy', 'Medium', or 'Hard'.
        dietary_tags: Optional list of dietary tags (e.g. ['dairy-free', 'vegetarian']).

    Returns:
        Confirmation dict with the saved recipe ID and title.
    """
    db = get_firestore_client()
    recipe_id = _slugify(title)
    if not recipe_id:
        recipe_id = f"recipe-{int(datetime.now(timezone.utc).timestamp())}"

    recipe_data = {
        "id": recipe_id,
        "title": title,
        "description": f"Custom favorite recipe for {title}.",
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time_minutes": prep_time_minutes,
        "cook_time_minutes": cook_time_minutes,
        "servings": servings,
        "difficulty": difficulty,
        "dietary_tags": dietary_tags or [],
        "is_favorite": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    db.collection(COLLECTION_NAME).document(recipe_id).set(recipe_data)
    return {
        "status": "success",
        "message": f"Recipe '{title}' saved successfully as favorite.",
        "recipe_id": recipe_id,
    }


def list_favorite_recipes() -> list[dict[str, Any]]:
    """Lists all recipes currently marked as favorites in the catalog.

    Returns:
        A list of favorite recipe summaries.
    """
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).where(filter=FieldFilter("is_favorite", "==", True)).stream()

    favorites = []
    for doc in docs:
        data = doc.to_dict()
        favorites.append(
            {
                "id": doc.id,
                "title": data.get("title"),
                "description": data.get("description"),
                "prep_time_minutes": data.get("prep_time_minutes"),
                "cook_time_minutes": data.get("cook_time_minutes"),
                "difficulty": data.get("difficulty"),
                "dietary_tags": data.get("dietary_tags", []),
            }
        )
    return favorites
