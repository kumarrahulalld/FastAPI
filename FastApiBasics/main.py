from fastapi import FastAPI


app = FastAPI()


class User(BaseModel):
    first_name: str
    last_name: str
    age: int
    salary: float


@app.post("/users")
async def root(user: User):
    return {"name": user}
