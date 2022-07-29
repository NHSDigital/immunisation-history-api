const { operationOutcomeFhir } = require('./operation-outcome.fhir');
const { HTTP_STATUS } = require('./constants');

function badRequest(errorMessage, version) {
  return {
    status: HTTP_STATUS.BAD_REQUEST,
    response: operationOutcomeFhir(errorMessage),
    headers: {
      version: version
    }
  };
}

exports.badRequest = badRequest;
