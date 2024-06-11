import logging
import os

from fastapi import APIRouter

router = APIRouter()

import requests

logger = logging.getLogger(__name__)


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/health")
async def root():
    return {"Status": "OK"}


@router.post("/invoke_api", status_code=201)
async def invoke():
    url = os.environ.get("FUNCTION_URL")
    logger.info(f"Enter invocation method to call {url}")
    response = requests.post(url)
    logger.info(f"Called function and received response: {response}")
    return response.json()
