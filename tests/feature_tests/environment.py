def before_scenario(context, scenario):
    context.app_attributes = {}
    context.api_products = []
    context.request_params = {}
    context.request_headers = {}
    context.nhs_login_id_token = None
    context.include_trace = False
    context.include_oauth = True
