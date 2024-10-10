from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
from movies.db.model import Movie

BASE_DIR = Path(__file__).resolve().parent
DeclarativeBase = declarative_base()

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

engine = create_engine(url=DATABASE_URL, echo=True)

DeclarativeBase.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_main(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.post("/")
async def add_movies():
    url = 'https://lifehacker.ru/luchshiye-filmy-21-veka/'
    request = requests.get(url)
    html = BeautifulSoup(request.text, features="html.parser")
    titles = html.find_all("h2", class_="wp-block-heading")
    lists = html.find_all("ul")
    images = []
    normalized_titles = []
    descriptions = []
    normalized_ratings = []
    for title in titles:
        normalized_title = title.text.split('.')
        normalized_titles.append(normalized_title[1].strip())
    for list in lists:
        descriptions.append(list.find_next_sibling("p").text)
        rating = list.contents[6].text.split(':')[1].strip()[:-1]
        normalized_rating = rating.replace(',', '.')
        normalized_ratings.append(float(normalized_rating))
        if list.find_next_sibling().name == 'figure':
            images.append(
                list.find_next_sibling("figure").find("img").attrs['src'])
        else:
            images.append('https://placehold.co/600x400.jpeg')
    for id, url in enumerate(images):
        if len(os.listdir(f"{os.getcwd()}/img/")) == 0:
            data = requests.get(url)
            with open(f"{os.getcwd()}/img/{id}.jpeg", "wb") as output_file:
                output_file.write(data.content)
    data = []
    for title, description, rating in zip(
            normalized_titles, descriptions, normalized_ratings):
        data.append({
            'title': title, 'description': description, 'rating': rating
            })
        new_movie = Movie(title=title, description=description, rating=rating)
        session.add(new_movie)
        session.commit()
    sorted_movies = sorted(data, key=lambda x: x.get('rating'), reverse=True)
    return JSONResponse(content=sorted_movies)


@app.get("/get-movies")
async def get_movies():
    result = session.query(
        Movie.id, Movie.title, Movie.description, Movie.rating
        ).all()
    json_data = [u._asdict() for u in result]
    json_output = json.dumps(json_data)
    return json_output
