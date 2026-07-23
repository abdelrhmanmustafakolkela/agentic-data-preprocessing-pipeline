from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import OllamaLLM as ChatOllama
from app.config import settings
from typing import Literal

def get_llm(role: Literal["descriptive", "planning"]):
    if role == "descriptive":
        return ChatOllama(model=settings.local_llm_model, base_url=settings.ollama_base_url, temperature=0.3)
    elif role == "planning":
        if settings.planning_llm_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
            return ChatOpenAI(model=settings.planning_llm_model, api_key=settings.openai_api_key, temperature=0.1)
        elif settings.planning_llm_provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
            return ChatAnthropic(model=settings.planning_llm_model, api_key=settings.anthropic_api_key, temperature=0.1)
        else:
            raise ValueError(f"Unknown planning LLM provider: {settings.planning_llm_provider}")
    else:
        raise ValueError(f"Unknown LLM role: {role}")
