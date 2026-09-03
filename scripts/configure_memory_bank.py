"""Configure Vertex AI Memory Bank for user allergies and dietary restrictions.

This script updates the Vertex AI Memory Bank instance on Agent Platform
with custom memory topics and few-shot examples ensuring user allergies,
dietary restrictions, and food intolerances are permanently captured and
remembered across conversations.
"""

import os
import vertexai
from google.genai import types as genai_types
from vertexai._genai import types

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-894441c8585c")
LOCATION = os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_LOCATION", "us-east1")
MEMORY_BANK_ID = os.environ.get("MEMORY_BANK_ID", "739628277865381888")


def configure_memory_bank():
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

    custom_topic = types.MemoryBankCustomizationConfigMemoryTopic(
        custom_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic(
            label="allergies_and_dietary_restrictions",
            description=(
                "Specific user allergies, dietary restrictions, food intolerances, "
                "and medical or lifestyle dietary needs (e.g. peanut allergy, celiac/gluten-free, "
                "shellfish allergy, lactose intolerance, vegan, vegetarian, halal, kosher, low sodium, keto)."
            ),
        )
    )

    managed_topics = [
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.USER_PERSONAL_INFO
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.USER_PREFERENCES
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.EXPLICIT_INSTRUCTIONS
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.KEY_CONVERSATION_DETAILS
            )
        ),
    ]

    all_topics = managed_topics + [custom_topic]

    # Few-shot examples demonstrating memory extraction for dietary restrictions
    ex1 = types.MemoryBankCustomizationConfigGenerateMemoriesExample(
        conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
            events=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                    content=genai_types.Content(
                        role="user",
                        parts=[
                            genai_types.Part(
                                text="I'm planning dinner. Just so you know, I have a severe peanut allergy and I am lactose intolerant."
                            )
                        ],
                    )
                ),
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                    content=genai_types.Content(
                        role="model",
                        parts=[
                            genai_types.Part(
                                text="Understood! I will strictly avoid peanuts and dairy in all recipe recommendations."
                            )
                        ],
                    )
                ),
            ]
        ),
        generated_memories=[
            types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                fact="The user has a severe peanut allergy and is lactose intolerant."
            )
        ],
    )

    ex2 = types.MemoryBankCustomizationConfigGenerateMemoriesExample(
        conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
            events=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                    content=genai_types.Content(
                        role="user",
                        parts=[
                            genai_types.Part(
                                text="Can you suggest a pasta dish? I am strictly gluten-free and vegetarian."
                            )
                        ],
                    )
                ),
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                    content=genai_types.Content(
                        role="model",
                        parts=[
                            genai_types.Part(
                                text="Here is a delicious gluten-free vegetarian pasta recipe!"
                            )
                        ],
                    )
                ),
            ]
        ),
        generated_memories=[
            types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                fact="The user follows a strictly gluten-free and vegetarian diet."
            )
        ],
    )

    ex3 = types.MemoryBankCustomizationConfigGenerateMemoriesExample(
        conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
            events=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                    content=genai_types.Content(
                        role="user",
                        parts=[
                            genai_types.Part(
                                text="What is the weather like today in Seattle?"
                            )
                        ],
                    )
                ),
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                    content=genai_types.Content(
                        role="model",
                        parts=[
                            genai_types.Part(
                                text="It's 90 degrees and sunny in Seattle."
                            )
                        ],
                    )
                ),
            ]
        ),
        generated_memories=[],
    )

    customization_config = types.MemoryBankCustomizationConfig(
        memory_topics=all_topics,
        generate_memories_examples=[ex1, ex2, ex3],
    )

    memory_bank_config = types.ReasoningEngineContextSpecMemoryBankConfig(
        customization_configs=[customization_config]
    )

    memory_bank_resource_name = f"projects/629547557339/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"
    print(f"Updating Memory Bank instance: {memory_bank_resource_name}")

    updated_mb = client.agent_engines.update(
        name=memory_bank_resource_name,
        config={"context_spec": {"memory_bank_config": memory_bank_config}},
    )
    print("Memory Bank instance updated successfully with allergy and dietary restriction topics!")
    return updated_mb


if __name__ == "__main__":
    configure_memory_bank()
