"""Script to create a serverless Vertex AI RAG corpus and import pg49513.txt."""

import sys
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-03-894441c8585c"
LOCATION = "us-central1"
GCS_PATH = "gs://pantry-chef-dishes-qwiklabs-gcp-03-894441c8585c/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, herbs, plants, remedies, and preparations described in this text. "
    "Ignore and omit all metadata, boilerplate, and transcriber notes. "
    "Output clean, self-contained prose."
)

print(f"Initializing Vertex AI (project={PROJECT_ID}, location={LOCATION})...")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 1. Switch the region's RAG managed DB to serverless mode (project-level, once).
cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
print("Updating RAG engine config to Serverless mode...")
try:
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )
    print("Serverless mode enabled.")
except Exception as e:
    print(f"Note on update_rag_engine_config: {e}")

# 2. Create the corpus
print("Creating RAG corpus...")
corpus = rag.create_corpus(
    display_name="culpeper-herbal-corpus",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    ),
)
print("Corpus created:", corpus.name)

# 3. Import + chunk + embed
print(f"Importing and indexing {GCS_PATH}...")
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
    llm_parser=rag.LlmParserConfig(
        model_name="gemini-2.5-flash",
        custom_parsing_prompt=PARSING_PROMPT,
    ),
)
print("Import completed. Files count:", getattr(resp, "imported_rag_files_count", resp))
