"""
NFM-X AI Provider Adapters

Provides adapter layer for various AI model providers:
- LocalLLM (llama.cpp)
- Ollama
- Transformers
- ONNX Runtime
- OpenAI-compatible endpoint
- Custom provider

NFM-X remains independent from provider-specific APIs.
"""

from .local_llm import LocalLLMProvider
from .ollama import OllamaProvider
from .transformers import TransformersProvider
from .onnx import ONNXProvider
from .openai_compatible import OpenAICompatibleProvider
from .custom import CustomProvider

__all__ = [
    'LocalLLMProvider',
    'OllamaProvider',
    'TransformersProvider',
    'ONNXProvider',
    'OpenAICompatibleProvider',
    'CustomProvider',
]