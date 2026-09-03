"""Seed script for PantryChef recipes collection in Google Cloud Firestore.

Hardcoded GCP project ID: "qwiklabs-gcp-03-894441c8585c"
Per deployment requirements, do not read from google.auth.default() or GOOGLE_CLOUD_PROJECT
because on Agent Platform those return the numeric project number, which breaks Firestore.
"""

from datetime import datetime, timezone
from google.cloud import firestore

# Literal project ID string hardcoded as required
PROJECT_ID = "qwiklabs-gcp-03-894441c8585c"
COLLECTION_NAME = "recipes"

SEEDED_RECIPES = [
    {
        "id": "chicken-broccoli-stir-fry",
        "title": "Quick Chicken and Broccoli Stir-Fry",
        "description": "A savory 15-minute weeknight stir-fry with tender chicken bites, crisp broccoli florets, and a flavorful garlic-soy glaze.",
        "ingredients": [
            "chicken breast",
            "broccoli",
            "garlic",
            "soy sauce",
            "olive oil",
            "black pepper",
        ],
        "instructions": [
            "Slice chicken breast into bite-sized strips and season lightly with black pepper.",
            "Heat 1 tablespoon olive oil in a skillet or wok over medium-high heat.",
            "Add minced garlic and chicken strips; sauté for 4-5 minutes until chicken is browned and cooked through.",
            "Add fresh broccoli florets and 2 tablespoons of water; cover and steam for 3 minutes until tender-crisp.",
            "Pour in soy sauce, toss well to coat, and simmer for 1-2 minutes until glossy. Serve hot.",
        ],
        "prep_time_minutes": 5,
        "cook_time_minutes": 10,
        "servings": 2,
        "difficulty": "Easy",
        "dietary_tags": ["dairy-free", "nut-free", "high-protein"],
        "is_favorite": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "mediterranean-chickpea-salad",
        "title": "Mediterranean Chickpea Salad",
        "description": "A crisp, zesty 10-minute plant-based salad loaded with chickpeas, cucumbers, and a bright lemon-herb dressing.",
        "ingredients": [
            "chickpeas",
            "cucumber",
            "cherry tomatoes",
            "olive oil",
            "lemon juice",
            "garlic",
            "oregano",
            "salt",
        ],
        "instructions": [
            "Rinse and drain canned chickpeas thoroughly.",
            "Dice cucumber and halve cherry tomatoes.",
            "In a large bowl, whisk together olive oil, fresh lemon juice, minced garlic, oregano, and salt.",
            "Toss chickpeas, cucumbers, and cherry tomatoes into the dressing.",
            "Serve immediately or chill for 15 minutes to let flavors meld.",
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 0,
        "servings": 2,
        "difficulty": "Easy",
        "dietary_tags": ["vegetarian", "vegan", "dairy-free", "gluten-free", "nut-free"],
        "is_favorite": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "lemon-herb-baked-salmon",
        "title": "Lemon Herb Baked Salmon with Asparagus",
        "description": "Tender, flaky salmon baked with fresh lemon slices, minced garlic, and tender asparagus spears.",
        "ingredients": [
            "salmon fillets",
            "asparagus",
            "lemon",
            "olive oil",
            "garlic",
            "salt",
            "black pepper",
        ],
        "instructions": [
            "Preheat oven to 400°F (200°C) and line a baking sheet with parchment paper.",
            "Arrange salmon fillets and trimmed asparagus on the baking sheet.",
            "Drizzle both with olive oil, minced garlic, fresh lemon juice, salt, and black pepper.",
            "Place thin lemon slices on top of each salmon fillet.",
            "Bake for 12-15 minutes until salmon flakes easily with a fork and asparagus is tender.",
        ],
        "prep_time_minutes": 5,
        "cook_time_minutes": 15,
        "servings": 2,
        "difficulty": "Easy",
        "dietary_tags": ["dairy-free", "nut-free", "gluten-free", "low-carb", "pescatarian"],
        "is_favorite": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "crispy-black-bean-tacos",
        "title": "15-Minute Black Bean Tacos",
        "description": "Flavorful seasoned black beans served in warm corn tortillas with creamy avocado and fresh cilantro.",
        "ingredients": [
            "black beans",
            "corn tortillas",
            "avocado",
            "garlic",
            "cumin",
            "chili powder",
            "lime",
            "salsa",
        ],
        "instructions": [
            "Heat a skillet over medium heat with a splash of olive oil. Add minced garlic, cumin, and chili powder.",
            "Add drained black beans and mash slightly with the back of a fork. Cook for 5 minutes until hot and fragrant.",
            "Warm corn tortillas in a dry skillet or microwave for 20 seconds.",
            "Fill each tortilla with seasoned black beans, sliced fresh avocado, and a spoonful of salsa.",
            "Squeeze fresh lime juice on top and serve.",
        ],
        "prep_time_minutes": 5,
        "cook_time_minutes": 10,
        "servings": 2,
        "difficulty": "Easy",
        "dietary_tags": ["vegetarian", "vegan", "dairy-free", "gluten-free", "nut-free"],
        "is_favorite": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
]


def seed_database():
    print(f"Connecting to Firestore for project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEEDED_RECIPES:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"  [+] Seeded recipe: '{item['title']}' (ID: {doc_id})")

    print(f"Successfully seeded {len(SEEDED_RECIPES)} recipes into collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed_database()
