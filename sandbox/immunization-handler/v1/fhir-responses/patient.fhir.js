exports.patientFhir = () => ({
  fullUrl: 'urn:uuid:124fcb63-669c-4a3c-af2b-caf55de167ec',
  resource: {
    resourceType: 'Patient',
    identifier: [
      {
        system: 'https://fhir.nhs.uk/Id/nhs-number',
        value: '9000000009'
      }
    ],
    birthDate: '1965-02-28'
  },
  search: {
    mode: 'include'
  }
});
