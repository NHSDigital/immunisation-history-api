var requestHeadersRaw = context.getVariable("request.headers.names");

// Convert to string and split by comma
var requestHeaders = (requestHeadersRaw + '').slice(1, -1).split(', ');

const authorisedTargetsAlreadyInHeader = requestHeaders.some((element, _index, _array) => element.toLowerCase() === "authorised_targets");
context.setVariable('apigee.AUTHORISED_TARGETS_ALREADY_IN_HEADER', authorisedTargetsAlreadyInHeader);
