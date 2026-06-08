from fastapi import FastAPI
from public.router import router

app = FastAPI(title="Lightning-Ai-ALL System")
app.include_router(router, prefix="/api/v1")

if __name__ == "__CVS.JS__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

