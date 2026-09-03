# My agent: PantryChef

One-liner: A conversational agent that helps home cooks create delicious meals from ingredients on hand with a catalog of customizable recipes.

Tool coverage:
- Memory: Dietary restrictions, allergies, skill level, pantry staples on hand, and saved favorite recipes.
- Tools: Search recipes by available ingredients (`search_recipes_by_ingredients`), save recipe to favorites (`save_favorite_recipe`), get detailed recipe steps (`get_recipe_details`).
- Catalog/UI: Recipe cards displaying cooking time, difficulty, ingredient lists, and instructions.
- Image gen: Photorealistic, appetizing images of plated dishes based on recipe name and styling.
- Sandbox: Scaling ingredient quantities and cook times for different serving sizes.

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI recipe cards, Imagen 3 dish generation, code sandbox for ingredient scaling
First eval question: Given the user prompt "I have chicken breast, garlic, soy sauce, and broccoli. Suggest a quick dinner under 20 minutes.", the agent responds with a relevant stir-fry recipe detailing ingredients and prep steps, while checking saved dietary preferences if present.
