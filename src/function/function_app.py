import logging

import azure.functions as func
from durable_function import bp
from health import health_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(bp)
app.register_functions(health_bp)


@app.route(route="root")
def handler_one(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
    else:
        name = req_body.get("name")

    if name:
        return HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully."
        )
    else:
        return HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
        )
