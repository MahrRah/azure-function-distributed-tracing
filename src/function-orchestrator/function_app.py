import azure.functions as func
import logging

from durable_function import bp
from test_blueprint import test_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
# app.register_functions(bp) # register the DF functions
app.register_functions(test_bp) 

# # Define a simple HTTP trigger function, to show that you can also
# # register functions via the `app` object
# @app.route(route="HttpTrigger")
# def HttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )