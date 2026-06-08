# 檔案路徑: collaboration/providers.py
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str):
        pass

class GrokProvider(AIProvider):
    async def generate(self, prompt: str):
        # 實作 Grok 呼叫邏輯
        return f"Grok response to: {prompt}"

class GeminiProvider(AIProvider):
    async def generate(self, prompt: str):
        # 實作 Gemini 呼叫邏輯
        return f"Gemini response to: {prompt}"

# 擴展性：只需新增類別即可
