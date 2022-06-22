
const { HTTP_STATUS } = require('./constants');
const { operationOutcomeFhir } = require('../fhir-responses/operation-outcome.fhir')

function badRequest(errorMessage) {
  return {
    status: HTTP_STATUS.BAD_REQUEST,
    response: operationOutcomeFhir(errorMessage)
  };
}

exports.badRequest = badRequest;
