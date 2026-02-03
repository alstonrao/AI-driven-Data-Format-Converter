import os
import json
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src import config

def call_llm(prompt):
    """
    Call the LLM with the provided prompt.
    Uses OpenAI API if key is present, otherwise falls back to a deterministic mock.
    
    Args:
        prompt (str): The prompt text.
        
    Returns:
        dict: The parsed JSON response from the LLM (or mock).
    """
    api_key = config.get_api_key()
    base_url = config.get_base_url()
    model_name = config.get_model_name()
    
    if not api_key or "sk-..." in api_key:
        logger.warning("No valid API key found. Using FALLBACK mode.")
        return get_fallback_strategy()
        
    # Initialize client with optional custom base_url
    client = OpenAI(
        api_key=api_key,
        base_url=base_url if base_url else None
    )
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"LLM Call failed: {e}")
        return get_fallback_strategy()

def get_fallback_strategy():
    """
    Returns a safe, minimal valid response when LLM fails or is unavailable.
    """
    return {
        "detected_shape": "Approximation (Fallback)",
        "assumptions": ["LLM unavailable, using bounding box approximation."],
        "entities": [
            # Minimal fallback: Just a ground plane or simpler
             {
                "type": "PLANE",
                "params": {"origin": [0,0,0], "normal": [0,0,1]},
                "comment": "Default ground plane"
            }
        ]
    }
