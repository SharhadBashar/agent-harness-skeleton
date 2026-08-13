from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.api import api_router


app = FastAPI(
    docs_url = '/docs',
    redoc_url = '/redoc',
    openapi_url = '/openapi.json'
)
add_pagination(app)


app.include_router(api_router)


@app.get('/')
async def root():
    return {'message': 'Welcome to Agentic Harness Skeleton Project'}


@app.get('/status')
async def status():
    return {'message': 'Agentic Harness Skeleton Project is up and running 😊'}
