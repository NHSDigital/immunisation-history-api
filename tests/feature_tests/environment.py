def before_scenario(context, scenario):
    context.api_products = []
    context.app_restricted = False
    context.request_params = {}
    context.request_headers = {}
