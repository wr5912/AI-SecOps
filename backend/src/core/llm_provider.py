"""
LLM Provider 抽象层

支持多种LLM提供商:
- Kimi (Moonshot AI)
- MiniMax
- OpenAI (可用于Azure OpenAI)
- vLLM (本地私有化模型)
- Ollama (本地模型)
"""

import os
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional
from dataclasses import dataclass
from enum import Enum

from openai import AsyncOpenAI, OpenAI


class LLMProviderType(Enum):
    """LLM提供商类型"""
    KIMI = "kimi"
    MINIMAX = "minimax"
    OPENAI = "openai"
    AZURE_OPENAI = "azure"
    VLLM = "vllm"
    OLLAMA = "ollama"


@dataclass
class LLMResponse:
    """LLM响应结构"""
    content: str
    model: str
    usage: dict
    finish_reason: str


class BaseLLMProvider(ABC):
    """LLM Provider基类"""
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """同步调用LLM"""
        pass
    
    @abstractmethod
    async def stream_complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式调用LLM"""
        pass
    
    @abstractmethod
    async def chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """聊天格式调用LLM"""
        pass
    
    @abstractmethod
    async def stream_chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天格式调用LLM"""
        pass


class KimiProvider(BaseLLMProvider):
    """Kimi (Moonshot AI) Provider"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "kimi-k2.5",
        base_url: str = "https://api.moonshot.cn/v1"
    ):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        response = await self.client.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return LLMResponse(
            content=response.choices[0].text,
            model=response.model,
            usage=response.usage.model_dump(),
            finish_reason=response.choices[0].finish_reason
        )
    
    async def stream_complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        response = await self.client.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].text:
                yield chunk.choices[0].text
    
    async def chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump(),
            finish_reason=response.choices[0].finish_reason
        )
    
    async def stream_chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class MiniMaxProvider(BaseLLMProvider):
    """MiniMax Provider"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "abab6.5s-chat",
        base_url: str = "https://api.minimax.chat/v1"
    ):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
    
    async def complete(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs) -> LLMResponse:
        # MiniMax使用chat completion格式
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_complete(messages, temperature, max_tokens, **kwargs)
    
    async def stream_complete(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs) -> AsyncIterator[str]:
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self.stream_chat_complete(messages, temperature, max_tokens, **kwargs):
            yield chunk
    
    async def chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump(),
            finish_reason=response.choices[0].finish_reason
        )
    
    async def stream_chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class VLLMProvider(BaseLLMProvider):
    """vLLM 本地模型 Provider"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        model: str = "Qwen/Qwen2.5-14B-Instruct",
        api_key: str = "dummy"
    ):
        self.base_url = base_url or os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
        self.model = model or os.getenv("LLM_MODEL_NAME", "Qwen/Qwen2.5-14B-Instruct")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url
        )
    
    async def complete(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_complete(messages, temperature, max_tokens, **kwargs)
    
    async def stream_complete(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs) -> AsyncIterator[str]:
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self.stream_chat_complete(messages, temperature, max_tokens, **kwargs):
            yield chunk
    
    async def chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump(),
            finish_reason=response.choices[0].finish_reason
        )
    
    async def stream_chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OllamaProvider(BaseLLMProvider):
    """Ollama 本地模型 Provider"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2"
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL_NAME", "llama2")
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "options": {"num_predict": max_tokens},
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()
            return LLMResponse(
                content=data.get("response", ""),
                model=self.model,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                finish_reason="stop"
            )
    
    async def stream_complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        import httpx
        
        async with httpx.AsyncClient() as client:
            async with client.stream_post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "options": {"num_predict": max_tokens},
                    "stream": True,
                    **kwargs
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
    
    async def chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "options": {"num_predict": max_tokens},
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()
            return LLMResponse(
                content=data.get("message", {}).get("content", ""),
                model=self.model,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                finish_reason=data.get("done", True) and "stop" or "length"
            )
    
    async def stream_chat_complete(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        import httpx
        
        async with httpx.AsyncClient() as client:
            async with client.stream_post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "options": {"num_predict": max_tokens},
                    "stream": True,
                    **kwargs
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]


class LLMProviderFactory:
    """LLM Provider工厂类"""
    
    _providers: dict[LLMProviderType, type[BaseLLMProvider]] = {
        LLMProviderType.KIMI: KimiProvider,
        LLMProviderType.MINIMAX: MiniMaxProvider,
        LLMProviderType.VLLM: VLLMProvider,
        LLMProviderType.OLLAMA: OllamaProvider,
    }
    
    @classmethod
    def create(cls, provider_type: Optional[LLMProviderType] = None, **kwargs) -> BaseLLMProvider:
        """创建LLM Provider实例"""
        if provider_type is None:
            provider_name = os.getenv("LLM_PROVIDER", "kimi").lower()
            provider_type = LLMProviderType(provider_name)
        
        provider_class = cls._providers.get(provider_type)
        if provider_class is None:
            raise ValueError(f"不支持的LLM提供商: {provider_type}")
        
        return provider_class(**kwargs)


# 全局单例
_llm_provider: Optional[BaseLLMProvider] = None


def get_llm_provider() -> BaseLLMProvider:
    """获取全局LLM Provider实例"""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProviderFactory.create()
    return _llm_provider


def set_llm_provider(provider: BaseLLMProvider):
    """设置全局LLM Provider"""
    global _llm_provider
    _llm_provider = provider
