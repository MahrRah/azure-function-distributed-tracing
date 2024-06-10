import logging
import os

import requests
from fastapi import FastAPI

app = FastAPI()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post(
    "/invoke_api",
    status_code=201,
)
@app.post("/invoke_api", status_code=201)
async def invoke():
    domain = os.environ.get("FUNCTION_URL")
    url = f"{domain}/api/handlers"
    logger.info(f"endpoint URL {url}")
    response = requests.post(url)
    logger.info(f"response: {response}")
    return {"message": "API invoked successfully"}
