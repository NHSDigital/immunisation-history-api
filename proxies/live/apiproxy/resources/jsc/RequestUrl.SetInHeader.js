var req_verb = context.getVariable('request.verb');
var req_scheme = context.getVariable('client.scheme');
var req_host = context.getVariable('request.header.host');
var req_request_uri = context.getVariable('request.uri');
var req_url = req_scheme + "://" + req_host + req_request_uri;

context.setVariable('apigee.X_REQUEST_URL', req_url);
