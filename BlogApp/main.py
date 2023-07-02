from fastapi import FastAPI, Depends, status, HTTPException
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


@app.post("/blog", status_code=status.HTTP_201_CREATED)
def create_blog(blog: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=blog.title, body=blog.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get("/blog", status_code=status.HTTP_200_OK)
def get_blogs(db: Session = Depends(get_db)):
    new_blogs = db.query(models.Blog).all()
    return new_blogs


@app.get("/blog/{id}", status_code=status.HTTP_200_OK)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"no blog found with id {id}.")
    return blog
