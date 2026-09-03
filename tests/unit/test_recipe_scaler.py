"""Unit tests for the recipe scaler tool."""

from app.tools.recipe_scaler import scale_recipe_servings


def test_scale_recipe_double():
    ingredients = [
        "1 lb chicken breast",
        "2 cups broccoli florets",
        "1/2 tsp black pepper",
        "1 1/2 tbsp olive oil",
        "Salt to taste",
    ]
    result = scale_recipe_servings(
        ingredients=ingredients,
        original_servings=2,
        target_servings=4,
        cook_time_minutes=15,
    )

    assert result["scale_factor"] == 2.0
    assert result["original_servings"] == 2
    assert result["target_servings"] == 4
    assert result["original_cook_time_minutes"] == 15
    assert result["adjusted_cook_time_minutes"] > 15

    scaled = result["scaled_ingredients"]
    assert "2 lb chicken breast" in scaled
    assert "4 cups broccoli florets" in scaled
    assert "1 tsp black pepper" in scaled
    assert "3 tbsp olive oil" in scaled
    assert "Salt to taste" in scaled


def test_scale_recipe_halve():
    ingredients = [
        "4 cups vegetable broth",
        "2 cans chickpeas",
        "1 tsp salt",
    ]
    result = scale_recipe_servings(
        ingredients=ingredients,
        original_servings=4,
        target_servings=2,
        cook_time_minutes=20,
    )

    assert result["scale_factor"] == 0.5
    assert result["original_servings"] == 4
    assert result["target_servings"] == 2
    assert result["adjusted_cook_time_minutes"] < 20

    scaled = result["scaled_ingredients"]
    assert "2 cups vegetable broth" in scaled
    assert "1 cans chickpeas" in scaled
    assert "1/2 tsp salt" in scaled


def test_scale_recipe_fractional():
    ingredients = [
        "1 cup quinoa",
    ]
    result = scale_recipe_servings(
        ingredients=ingredients,
        original_servings=2,
        target_servings=3,
    )
    assert result["scale_factor"] == 1.5
    assert "1 1/2 cup quinoa" in result["scaled_ingredients"]


def test_scale_recipe_invalid_servings():
    result = scale_recipe_servings(
        ingredients=["1 cup flour"],
        original_servings=0,
        target_servings=4,
    )
    assert "error" in result

    result_neg = scale_recipe_servings(
        ingredients=["1 cup flour"],
        original_servings=2,
        target_servings=-1,
    )
    assert "error" in result_neg
