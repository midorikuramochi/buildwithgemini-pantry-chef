"""Unit tests for A2UI integration and a2ui_callback."""

import json
from google.genai import types
from google.adk.models.llm_response import LlmResponse
from app.agent import root_agent, instruction
from app.a2ui_utils import a2ui_callback, _FALLBACK_TEXT


def test_root_agent_has_a2ui_configured():
    assert root_agent.after_model_callback == a2ui_callback
    assert "A2UI JSON SCHEMA" in instruction or "a2ui" in instruction.lower()


def test_a2ui_callback_ignores_regular_text():
    llm_response = LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text="Hello! Here is a simple plain text recipe.")],
        )
    )
    result = a2ui_callback(None, llm_response)
    assert result is None


def test_a2ui_callback_wraps_valid_a2ui_json():
    a2ui_payload = [
        {"beginRendering": {"surfaceId": "test_surf", "root": "card1"}},
        {
            "surfaceUpdate": {
                "surfaceId": "test_surf",
                "components": [
                    {
                        "id": "card1",
                        "component": {
                            "Card": {
                                "child": "text1"
                            }
                        }
                    },
                    {
                        "id": "text1",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Hello A2UI"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    raw_text = json.dumps(a2ui_payload)
    llm_response = LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=raw_text)],
        )
    )
    result = a2ui_callback(None, llm_response)
    assert result is not None
    assert result.custom_metadata == {"a2a:response": "true"}
    assert len(result.content.parts) == 2
    assert b"<a2a_datapart_json>" in result.content.parts[0].inline_data.data
    assert b"beginRendering" in result.content.parts[0].inline_data.data


def test_a2ui_callback_returns_fallback_on_malformed_surface():
    malformed_text = '{"beginRendering": {"surfaceId": "s", "root": "missing"}}'
    llm_response = LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=malformed_text)],
        )
    )
    result = a2ui_callback(None, llm_response)
    assert result is not None
    assert result.content.parts[0].text == _FALLBACK_TEXT
