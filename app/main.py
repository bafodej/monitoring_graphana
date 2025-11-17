from fastapi import FastAPI

app = FastAPI(
    title=" API Estimation Immobilière",
    description="""
    API REST pour l'estimation automatisée des prix immobiliers.
    """,
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Hello World"}