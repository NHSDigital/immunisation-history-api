const { emptyImmunizationFhir } = require('./fhir-responses/empty-immunization.fhir');
const { SNOMED_PROCEDURE_CODES, IMMUNIZATION_TARGETS } = require('./constants');
const { covidImmunizationFhir } = require('./fhir-responses/covid-immunization.fhir');
const { hpvImmunizationFhir } = require('./fhir-responses/hpv-immunization.fhir');
const { parseDateRange, validateDateRange } = require('./date-range');
const { writeLog } = require('../../logging');
const { HTTP_STATUS, API_VERSIONS } = require('../constants');
const { badRequest } = require('../api-response');

const VERSION = API_VERSIONS.V2;

function getImmunizationResponse(
  patientIdentifier,
  procedureCodeBelow,
  immunizationTarget,
  dateFrom,
  dateTo
) {
  if (patientIdentifier !== '9000000009') {
    return emptyImmunizationFhir();
  }

  if (
    procedureCodeBelow === SNOMED_PROCEDURE_CODES.CORONAVIRUS_VACCINATION ||
    immunizationTarget === IMMUNIZATION_TARGETS.COVID19
  ) {
    return covidImmunizationFhir(dateFrom, dateTo);
  }

  if (immunizationTarget === IMMUNIZATION_TARGETS.HPV) {
    return hpvImmunizationFhir(dateFrom, dateTo);
  }
}

function getFhirResponse(
  patientIdentifier,
  procedureCodeBelow,
  immunizationTarget,
  rawDateFrom,
  rawDateTo
) {
  if (!patientIdentifier) {
    return badRequest('Missing required request parameters: [patient.identifier]', VERSION);
  }

  if ((!procedureCodeBelow && !immunizationTarget) || (procedureCodeBelow && immunizationTarget)) {
    return badRequest(
      'Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target]',
      VERSION
    );
  }

  if (immunizationTarget && !Object.values(IMMUNIZATION_TARGETS).includes(immunizationTarget)) {
    return badRequest(
      'Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target]',
      VERSION
    );
  }

  if (procedureCodeBelow && procedureCodeBelow !== SNOMED_PROCEDURE_CODES.CORONAVIRUS_VACCINATION) {
    return badRequest(
      'Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target]',
      VERSION
    );
  }
  const { dateFrom, dateTo } = parseDateRange(rawDateFrom, rawDateTo);
  const errorMessage = validateDateRange(dateFrom, dateTo);
  if (errorMessage) {
    return badRequest(errorMessage, VERSION);
  }

  return {
    status: HTTP_STATUS.OK,
    response: getImmunizationResponse(
      patientIdentifier,
      procedureCodeBelow,
      immunizationTarget,
      dateFrom,
      dateTo
    ),
    headers: {
      version: VERSION
    }
  };
}

function immunisationGetHandler(req, res) {
  const patientIdentifier = req.query['patient.identifier'].split('|')[1];
  const procedureCodeBelow = req.query['procedure-code:below'];
  const immunizationTarget = req.query['immunization.target'];
  const rawDateFrom = req.query['date.from'];
  const rawDateTo = req.query['date.to'];

  writeLog(res, 'info', {
    message: 'immunization',
    req: {
      path: req.path,
      query: req.query,
      headers: req.rawHeaders,
      patientIdentifier: patientIdentifier,
      procedureCodeBelow: procedureCodeBelow,
      immunizationTarget: immunizationTarget,
      rawDateFrom: rawDateFrom,
      rawDateTo: rawDateTo,
      version: VERSION,
      accept: req.headers['accept']
    }
  });

  return getFhirResponse(
    patientIdentifier,
    procedureCodeBelow,
    immunizationTarget,
    rawDateFrom,
    rawDateTo
  );
}

module.exports = immunisationGetHandler;
