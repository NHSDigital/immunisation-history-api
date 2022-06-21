const { IMMUNIZATION_TARGETS, SNOMED_PROCEDURE_CODES, HTTP_STATUS } = require('./constants');
const { badRequest } = require('./api-response');
const { parseDateRange, validateDateRange } = require('./date-range');
const { emptyImmunizationFhir } = require('../fhir-responses/empty-immunization.fhir');
const { covidImmunizationFhir } = require('../fhir-responses/covid-immunization.fhir');
const { hpvImmunizationFhir } = require('../fhir-responses/hpv-immunization.fhir');
const { writeLog } = require('../logging');

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
    return badRequest('Missing required request parameters: [patient.identifier]');
  }

  if ((!procedureCodeBelow && !immunizationTarget) || (procedureCodeBelow && immunizationTarget)) {
    return badRequest(
      'Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target]'
    );
  }

  if (immunizationTarget && !Object.values(IMMUNIZATION_TARGETS).includes(immunizationTarget)) {
    return badRequest(
      'Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target]'
    );
  }

  if (procedureCodeBelow && procedureCodeBelow !== SNOMED_PROCEDURE_CODES.CORONAVIRUS_VACCINATION) {
    return badRequest(
      'Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target]'
    );
  }
  const { dateFrom, dateTo } = parseDateRange(rawDateFrom, rawDateTo);
  const errorMessage = validateDateRange(dateFrom, dateTo);
  if (errorMessage) {
    return badRequest(errorMessage);
  }

  return {
    status: HTTP_STATUS.OK,
    response: getImmunizationResponse(
      patientIdentifier,
      procedureCodeBelow,
      immunizationTarget,
      dateFrom,
      dateTo
    )
  };
}

async function immunization(req, res, next) {
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
      rawDateTo: rawDateTo
    }
  });

  const { status, response } = getFhirResponse(
    patientIdentifier,
    procedureCodeBelow,
    immunizationTarget,
    rawDateFrom,
    rawDateTo
  );

  res.status(status).json(response);
  res.end();
  next();
}

exports.immunization = immunization;
