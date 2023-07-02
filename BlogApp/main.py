from fastapi import FastAPI, Depends
import models
import schemas
import database
from sqlalchemy.orm import Session


async def get_db():
    db = database.LocalSession
    try:
        yield db
    finally:
        db.close_all()


app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)


@app.post("/blog")
def create_blog(blog: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=blog.title, body=blog.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get("/blog")
def get_blogs(db: Session = Depends(get_db)):
    new_blogs = db.query(models.Blog).all()
    return new_blogs
