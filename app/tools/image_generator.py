"""Tool for generating appetizing dish images using Gemini and saving to Artifacts + Cloud Storage."""

import logging
import re
import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

# Hardcoded project ID and public bucket name as required
PROJECT_ID = "qwiklabs-gcp-03-894441c8585c"
LOCATION = "global"
BUCKET_NAME = "pantry-chef-dishes-qwiklabs-gcp-03-894441c8585c"


async def generate_dish_image(
    tool_context: ToolContext,
    dish_name: str,
    description: str = "",
) -> str:
    """Generate an appetizing, high-quality image of a dish or recipe using the gemini-3.1-flash-lite-image model.

    The image is saved to the session's artifacts (so it displays in the Playground Artifacts panel)
    and uploaded to a public Cloud Storage bucket.

    Args:
        dish_name: The name of the dish or meal (e.g., 'Lemon Herb Roast Chicken', 'Chocolate Lava Cake').
        description: Optional details, ingredients, cooking style, or visual presentation notes.

    Returns:
        The public HTTPS URL of the image stored in Cloud Storage (e.g. https://storage.googleapis.com/<bucket>/<object>).
    """
    prompt = f"A professional, appetizing culinary photo of {dish_name}."
    if description:
        prompt += f" Details: {description}."
    prompt += " Plated beautifully on a clean dining table, gourmet presentation, bright natural lighting."

    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates or []:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    if part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    break
        if image_bytes:
            break

    if not image_bytes:
        raise RuntimeError(f"Failed to generate image for '{dish_name}'.")

    ext = "png" if "png" in mime_type else "jpg"
    clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", dish_name.strip().lower())
    clean_name = re.sub(r"_+", "_", clean_name).strip("_") or "dish"
    filename = f"{clean_name}_{uuid.uuid4().hex[:8]}.{ext}"

    # 1. Save with tool_context.save_artifact so it appears in the Playground Artifacts panel
    if tool_context is not None:
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        except Exception as e:
            logger.warning("Failed to save artifact in tool_context: %s", e)

    # 2. Upload the same in-memory image bytes to public Cloud Storage bucket without writing to local file
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    object_name = f"dishes/{filename}"
    blob = bucket.blob(object_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
    return public_url
