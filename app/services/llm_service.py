"""
Serviço de LLM simplificado para uso direto (sem A2A).
Usado quando não há necessidade de agentes A2A.
"""
import os
from typing import Optional, List, Dict, Any, Generator
from openai import OpenAI


def get_llm_response(
    messages: List[Dict[str, str]],
    api_key: str,
    model: str = "openai/gpt-4o-mini"
) -> Optional[Generator]:
    """
    Chama OpenRouter com streaming.
    
    Args:
        messages: Lista de mensagens no formato OpenAI
        api_key: API Key do OpenRouter
        model: Modelo a usar
    
    Returns:
        Generator com chunks de resposta ou None em caso de erro
    """
    if not api_key or len(api_key) < 20:
        return None
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        return stream
    except Exception:
        return None
