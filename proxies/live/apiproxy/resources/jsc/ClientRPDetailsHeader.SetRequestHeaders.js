var developerAppName = context.getVariable('developer.app.name');
var developerAppId = context.getVariable('developer.app.id');
var clientIP = context.getVariable('client.ip');

var clientRpDetailsHeader = {
    "developer.app.name": developerAppName,
    "developer.app.id": developerAppId,
    "client.ip": clientIP
};

context.targetRequest.headers['NHSD-Client-RP-Details'] = clientRpDetailsHeader;
