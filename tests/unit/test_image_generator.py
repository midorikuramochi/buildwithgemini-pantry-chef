"""Unit tests for the dish image generation tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.tools.image_generator import generate_dish_image, BUCKET_NAME


@pytest.mark.asyncio
async def test_generate_dish_image_success():
    # Mock genai Client
    mock_genai_client = MagicMock()
    mock_response = MagicMock()
    mock_candidate = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data.data = b"fake-jpeg-image-bytes"
    mock_part.inline_data.mime_type = "image/jpeg"
    mock_candidate.content.parts = [mock_part]
    mock_response.candidates = [mock_candidate]
    mock_genai_client.models.generate_content.return_value = mock_response

    # Mock storage Client
    mock_storage_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Mock tool_context
    mock_tool_context = AsyncMock()

    with patch("google.genai.Client", return_value=mock_genai_client), \
         patch("google.cloud.storage.Client", return_value=mock_storage_client):

        url = await generate_dish_image(
            tool_context=mock_tool_context,
            dish_name="Lemon Herb Salmon",
            description="Pan-seared with crispy skin and asparagus",
        )

        # Verify genai call
        mock_genai_client.models.generate_content.assert_called_once()
        call_kwargs = mock_genai_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-3.1-flash-lite-image"
        assert "IMAGE" in call_kwargs["config"].response_modalities

        # Verify tool_context.save_artifact was called
        mock_tool_context.save_artifact.assert_awaited_once()
        artifact_call = mock_tool_context.save_artifact.call_args.kwargs
        assert artifact_call["filename"].startswith("lemon_herb_salmon_")
        assert artifact_call["artifact"].inline_data.data == b"fake-jpeg-image-bytes"

        # Verify Cloud Storage upload
        mock_storage_client.bucket.assert_called_with(BUCKET_NAME)
        mock_blob.upload_from_string.assert_called_once_with(
            b"fake-jpeg-image-bytes", content_type="image/jpeg"
        )

        # Verify returned public URL
        expected_prefix = f"https://storage.googleapis.com/{BUCKET_NAME}/dishes/lemon_herb_salmon_"
        assert url.startswith(expected_prefix)
        assert url.endswith(".jpg")


@pytest.mark.asyncio
async def test_generate_dish_image_no_image_returned():
    mock_genai_client = MagicMock()
    mock_response = MagicMock()
    mock_response.candidates = []
    mock_genai_client.models.generate_content.return_value = mock_response

    mock_tool_context = AsyncMock()

    with patch("google.genai.Client", return_value=mock_genai_client):
        with pytest.raises(RuntimeError, match="Failed to generate image"):
            await generate_dish_image(
                tool_context=mock_tool_context,
                dish_name="Invisible Soup",
            )
