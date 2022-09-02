var requestHeadersRaw = context.getVariable("request.headers.names");

// Convert to string and split by comma
var requestHeaders = (requestHeadersRaw + '').slice(1, -1).split(', ');

const requestUrlAlreadyInHeader = requestHeaders.some((element, _index, _array) => element.toLowerCase() === "x-request-url");
context.setVariable('apigee.REQUEST_URL_ALREADY_IN_HEADER', requestUrlAlreadyInHeader);
