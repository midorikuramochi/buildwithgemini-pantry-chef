# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from app.a2ui_utils import a2ui_callback
from app.tools.herbal_corpus import consult_herbal_corpus
from app.tools.image_generator import generate_dish_image
from app.tools.recipe_scaler import scale_recipe_servings
from app.tools.recipe_store import (
    get_recipe_details,
    list_favorite_recipes,
    save_favorite_recipe,
    search_recipes,
)


MODEL = "gemini-3.6-flash"

SANDBOX_RESOURCE_NAME = os.getenv(
    "AGENT_ENGINE_SANDBOX_RESOURCE_NAME",
    "projects/629547557339/locations/us-east1/reasoningEngines/2198794557133422592/sandboxEnvironments/217738486671736832",
)


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        # Gracefully handle when memory service is not attached (e.g. unit test runner)
        pass
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"





schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are PantryChef, a knowledgeable and attentive culinary and recipe assistant.\n\n"
        "Memory & Personalization Guidelines:\n"
        "- All user food allergies, dietary restrictions, intolerances, and preferences are automatically remembered across conversations.\n"
        "- Diligently acknowledge any allergies or dietary restrictions the user shares (e.g. nut allergies, celiac/gluten-free, lactose intolerance, vegan, vegetarian, kosher, halal, low sodium).\n"
        "- STRICT SAFETY RULE: NEVER recommend recipes, ingredients, or meal options that violate the user's remembered or stated allergies and dietary restrictions. Always provide safe substitutes when adapting dishes.\n"
        "- When suggesting recipes, actively take into account the user's remembered dietary restrictions, pantry ingredients, and preferred cuisines to provide tailored, delicious recommendations.\n\n"
        "Recipe Catalog & Storage Guidelines:\n"
        "- You have access to a Firestore recipe database containing vetted recipes and saved favorites.\n"
        "- Use `search_recipes` when the user provides ingredients on hand or asks for recipe recommendations.\n"
        "- Use `get_recipe_details` when the user asks for full cooking steps, instructions, or ingredients for a recipe.\n"
        "- Use `save_favorite_recipe` when the user asks to save a recipe, bookmark a favorite, or store a custom dish.\n"
        "- Use `list_favorite_recipes` when the user asks to see their saved recipes or favorites.\n"
        "- Use `scale_recipe_servings` when the user asks to scale, multiply, divide, or adjust ingredient quantities and cook times for different serving sizes.\n"
        "- Use `generate_dish_image` when the user asks to see what a dish looks like, generate a photo or picture of a meal, or visualize a recipe. The tool saves an artifact and uploads to Cloud Storage; set the public image URL as the url of an A2UI Image component.\n\n"
        "Herbal & Botanical Knowledge (RAG Engine):\n"
        "- You have access to Nicholas Culpeper's historic text 'The Complete Herbal' indexed in a Vertex AI RAG corpus via `consult_herbal_corpus`.\n"
        "- Use `consult_herbal_corpus` whenever the user asks about traditional herbs, botanical virtues, historical remedies, or medicinal and culinary properties of plants.\n"
        "- Ground your response on the retrieved passages and cite Culpeper's Herbal when referencing historical virtues.\n\n"
        "Python Sandbox Code Execution (AgentEngineSandboxCodeExecutor):\n"
        "- You have access to a secure, isolated Python execution sandbox hosted on Agent Platform.\n"
        "- Use Python code execution whenever you need to perform calculations, compute nutrition or macronutrient breakdowns, calculate recipe cost or proportions, convert complex measurements, or analyze culinary data.\n"
        "- Write clean Python in standard code blocks (`python ... `), and always print outputs so results are visible."
    ),
    workflow_description=(
        "Analyze the user's request and call tools as needed. "
        "For general conversation, greetings, culinary questions, and quick answers, respond in clear conversational text. "
        "When presenting recipes, recipe cards, dish summaries, ingredients, or menus, return structured UI using an A2UI JSON surface."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    ),
    tools=[
        PreloadMemoryTool(),
        search_recipes,
        get_recipe_details,
        save_favorite_recipe,
        list_favorite_recipes,
        scale_recipe_servings,
        generate_dish_image,
        consult_herbal_corpus,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
