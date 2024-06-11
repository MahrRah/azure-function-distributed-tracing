import azure.functions as func
import logging

test_bp = func.Blueprint()

@test_bp.route(route="startOrchestrator")
def my_azure_func(req: func.HttpRequest,):
    logging.info("test log")
