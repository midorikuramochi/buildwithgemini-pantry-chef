"""Retrieval tool for searching Nicholas Culpeper's 'The Complete Herbal' via Vertex AI RAG Engine."""

import vertexai
from vertexai.preview import rag

PROJECT_ID = "qwiklabs-gcp-03-894441c8585c"
LOCATION = "us-central1"
CORPUS_NAME = "projects/629547557339/locations/us-central1/ragCorpora/8194888860233105408"


def consult_herbal_corpus(query: str) -> str:
    """Search Nicholas Culpeper's 'The Complete Herbal' for traditional culinary herbs, plants, medicinal virtues, and historical remedies.

    Args:
        query: Botanical, herbal, culinary, or medicinal query (e.g. 'rosemary virtues', 'thyme culinary use', 'herbal remedy for cough', 'sage benefits').

    Returns:
        Matched excerpts and passages from Culpeper's Complete Herbal.
    """
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=4),
        )
    except Exception as e:
        return f"Retrieval failed: {e}"

    contexts = getattr(resp.contexts, "contexts", [])
    passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
    if not passages:
        return "No relevant passages found in Culpeper's Complete Herbal."

    return "\n\n---\n\n".join(passages)
