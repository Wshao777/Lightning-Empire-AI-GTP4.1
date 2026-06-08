# 檔案路徑: public/router.py
from fastapi import APIRouter
from collaboration.providers import GrokProvider, GeminiProvider

router = APIRouter()

providers = {
    "grok": GrokProvider(),
    "gemini": GeminiProvider()
}

@router.post("/query/{model_name}")
async def route_query(model_name: str, prompt: str):
    provider = providers.get(model_name)
    if not provider:
        return {"error": "Model not found"}
    return await provider.generate(prompt)

