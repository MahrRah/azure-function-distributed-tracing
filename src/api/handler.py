import logging

from fastapi import APIRouter

router = APIRouter()

import requests
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/health")
async def root():
    with tracer.start_as_current_span("health") as span:
        logger.info("Health endpoint called.")
        span.set_attribute("health", "healthy")
        with tracer.start_as_current_span("health-2") as spantwo:
            logger.info("Health endpoint called again.")
            spantwo.set_attribute("health", "healthier")
    return {"Status": "OK"}


@router.post("/invoke_api", status_code=201)
async def invoke():
    url = "http://localhost:7071/api/handlers"
    logger.info(f"Enter invocation method to call {url}")
    response = requests.post(url)
    logger.info(f"Called function and received response: {response}")
    return response.json()
