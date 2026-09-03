"""Unit tests for the herbal corpus RAG retrieval tool."""

from unittest.mock import MagicMock, patch
from app.tools.herbal_corpus import consult_herbal_corpus


def test_consult_herbal_corpus_success():
    mock_resp = MagicMock()
    mock_ctx1 = MagicMock()
    mock_ctx1.text = "Rosemary is a solar plant, strengthening the memory and comforting the brain."
    mock_ctx2 = MagicMock()
    mock_ctx2.text = "The decoction of rosemary made with white wine helps digestion."
    mock_resp.contexts.contexts = [mock_ctx1, mock_ctx2]

    with patch("vertexai.preview.rag.retrieval_query", return_value=mock_resp):
        result = consult_herbal_corpus("rosemary virtues")

        assert "Rosemary is a solar plant" in result
        assert "decoction of rosemary" in result
        assert "---" in result


def test_consult_herbal_corpus_empty():
    mock_resp = MagicMock()
    mock_resp.contexts.contexts = []

    with patch("vertexai.preview.rag.retrieval_query", return_value=mock_resp):
        result = consult_herbal_corpus("unknown alien plant")
        assert "No relevant passages found" in result


def test_consult_herbal_corpus_exception():
    with patch("vertexai.preview.rag.retrieval_query", side_effect=RuntimeError("Connection timeout")):
        result = consult_herbal_corpus("mint")
        assert "Retrieval failed: Connection timeout" in result
