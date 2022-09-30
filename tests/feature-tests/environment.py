from utils.utils import make_correlation_id


def before_scenario(context, scenario):
    context.correlation_id = make_correlation_id(scenario.name)
    context.request_config = {"headers": {}}
