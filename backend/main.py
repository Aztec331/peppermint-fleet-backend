from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Peppermint Fleet Backend is running"}