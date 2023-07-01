from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def root(id: int, name: str, place: str):
    return {"message": id, "name": name, "place": place}
