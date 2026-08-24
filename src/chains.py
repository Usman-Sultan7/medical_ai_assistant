from langchain_openai import ChatOpenAI
from src.prompts import assessment_prompt, narrative_prompt

def get_llm(api_key: str):
    # Using a low temperature for more predictable, structured output
    return ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0.1)

def generate_assessment(llm, inputs: dict) -> str:
    """Runs the main assessment chain to get the JSON string."""
    chain = assessment_prompt | llm
    response = chain.invoke(inputs)
    return response.content

def stream_narrative(llm, inputs: dict):
    """Yields chunks of text for the live streaming effect."""
    chain = narrative_prompt | llm
    for chunk in chain.stream(inputs):
        yield chunk.content