exports.emptyImmunizationFhir = () => ({
  resourceType: 'Bundle',
  type: 'searchset',
  total: 0,
  entry: []
});
