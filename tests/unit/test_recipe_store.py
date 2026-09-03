"""Unit tests for Firestore recipe store tools."""

import pytest
from app.tools.recipe_store import (
    get_recipe_details,
    list_favorite_recipes,
    save_favorite_recipe,
    search_recipes,
)


def test_search_recipes():
    # Should find seeded chicken broccoli stir fry
    results = search_recipes(ingredients=["chicken", "broccoli"])
    assert len(results) > 0
    titles = [r["title"] for r in results]
    assert any("Chicken and Broccoli" in t for t in titles)


def test_get_recipe_details_found():
    recipe = get_recipe_details("chicken-broccoli-stir-fry")
    assert "error" not in recipe
    assert recipe["title"] == "Quick Chicken and Broccoli Stir-Fry"
    assert "instructions" in recipe
    assert len(recipe["instructions"]) > 0
    assert "chicken breast" in recipe["ingredients"]


def test_get_recipe_details_not_found():
    recipe = get_recipe_details("non-existent-recipe-id-99999")
    assert "error" in recipe


def test_save_and_list_favorite_recipe():
    test_title = "Unit Test Avocado Toast"
    result = save_favorite_recipe(
        title=test_title,
        ingredients=["1 slice sourdough bread", "1/2 ripe avocado", "red pepper flakes"],
        instructions=["Toast the bread.", "Mash avocado and spread on toast.", "Sprinkle with red pepper flakes."],
        prep_time_minutes=3,
        cook_time_minutes=2,
        servings=1,
        difficulty="Easy",
        dietary_tags=["vegetarian", "vegan", "dairy-free"],
    )
    assert result["status"] == "success"
    recipe_id = result["recipe_id"]

    # Verify retrieval
    details = get_recipe_details(recipe_id)
    assert details["title"] == test_title
    assert "sourdough" in details["ingredients"][0]

    # Verify presence in list_favorite_recipes
    favorites = list_favorite_recipes()
    assert any(f["title"] == test_title for f in favorites)
