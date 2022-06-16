exports.operationOutcomeFhir = diagnostic => ({
  resourceType: 'OperationOutcome',
  issue: [
    {
      severity: 'error',
      code: 'processing',
      diagnostics: diagnostic
    }
  ]
});
