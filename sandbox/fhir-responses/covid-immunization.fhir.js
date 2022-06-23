const { isEntryWithinDateRange } = require('./response-helper');
const { patientFhir } = require('./patient.fhir');

const entries = [
  {
    fullUrl: 'urn:uuid:d11c69d8-7a50-4a54-a848-7648121e995f',
    resource: {
      resourceType: 'Immunization',
      extension: [
        {
          url: 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure',
          valueCodeableConcept: {
            coding: [
              {
                system: 'http://snomed.info/sct',
                code: '1324681000000101',
                display:
                  'Administration of first dose of severe acute respiratory syndrome coronavirus 2 vaccine (procedure)'
              }
            ]
          }
        }
      ],
      identifier: [
        {
          use: 'secondary',
          system: 'https://supplierABC/identifiers/vacc',
          value: '1324761000000100'
        }
      ],
      status: 'completed',
      vaccineCode: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '39114911000001105',
            display:
              'COVID-19 Vaccine AstraZeneca (ChAdOx1 S [recombinant]) 5x10,000,000,000 viral particles/0.5ml dose solution for injection multidose vials (AstraZeneca UK Ltd) (product)'
          }
        ]
      },
      patient: {
        reference: 'urn:uuid:124fcb63-669c-4a3c-af2b-caf55de167ec',
        type: 'Patient',
        identifier: {
          system: 'https://fhir.nhs.uk/Id/nhs-number',
          value: '9000000009'
        }
      },
      occurrenceDateTime: '2020-12-10T13:00:08.476+00:00',
      recorded: '2020-12-10',
      primarySource: true,
      manufacturer: {
        display: 'AstraZeneca Ltd'
      },
      lotNumber: 'R04X',
      expirationDate: '2021-04-29',
      site: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '368208006',
            display: 'Left upper arm structure (body structure)'
          }
        ]
      },
      route: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '78421000',
            display: 'Intramuscular route (qualifier value)'
          }
        ]
      },
      doseQuantity: {
        system: 'http://snomed.info/sct',
        value: 1,
        unit: 'pre-filled disposable injection',
        code: '3318611000001103'
      },
      reportOrigin: {},
      performer: [
        {
          actor: {
            type: 'Organization',
            identifier: {
              system: 'https://fhir.nhs.uk/Id/ods-organization-code',
              value: 'RX809'
            },
            display: 'TEST-SITE'
          }
        }
      ],
      reasonCode: [
        {
          coding: [
            {
              system: 'http://snomed.info/sct',
              code: '443684005',
              display: 'Disease outbreak (event)'
            }
          ]
        }
      ],
      protocolApplied: [
        {
          doseNumberPositiveInt: 1
        }
      ]
    },
    search: {
      mode: 'match'
    }
  },
  {
    fullUrl: 'urn:uuid:8da02505-db94-40b6-a8ed-d5af5628e28c',
    resource: {
      resourceType: 'Immunization',
      extension: [
        {
          url: 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure',
          valueCodeableConcept: {
            coding: [
              {
                system: 'http://snomed.info/sct',
                code: '1324681000000102',
                display:
                  'Administration of first dose of severe acute respiratory syndrome coronavirus 2 vaccine (procedure)'
              }
            ]
          }
        }
      ],
      identifier: [
        {
          use: 'secondary',
          system: 'https://supplierABC/identifiers/vacc',
          value: '1324761000000102'
        }
      ],
      status: 'completed',
      vaccineCode: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '39114911000001105',
            display:
              'COVID-19 Vaccine AstraZeneca (ChAdOx1 S [recombinant]) 5x10,000,000,000 viral particles/0.5ml dose solution for injection multidose vials (AstraZeneca UK Ltd) (product)'
          }
        ]
      },
      patient: {
        reference: 'urn:uuid:124fcb63-669c-4a3c-af2b-caf55de167ec',
        type: 'Patient',
        identifier: {
          system: 'https://fhir.nhs.uk/Id/nhs-number',
          value: '9000000009'
        }
      },
      occurrenceDateTime: '2020-12-31T13:00:08.476+00:00',
      recorded: '2020-12-31',
      primarySource: true,
      manufacturer: {
        display: 'AstraZeneca Ltd'
      },
      lotNumber: 'R04X',
      expirationDate: '2021-04-29',
      site: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '368208006',
            display: 'Left upper arm structure (body structure)'
          }
        ]
      },
      route: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '78421000',
            display: 'Intramuscular route (qualifier value)'
          }
        ]
      },
      doseQuantity: {
        system: 'http://snomed.info/sct',
        value: 1,
        unit: 'pre-filled disposable injection',
        code: '3318611000001103'
      },
      reportOrigin: {},
      performer: [
        {
          actor: {
            type: 'Organization',
            identifier: {
              system: 'https://fhir.nhs.uk/Id/ods-organization-code',
              value: 'RX809'
            },
            display: 'TEST-SITE'
          }
        }
      ],
      reasonCode: [
        {
          coding: [
            {
              system: 'http://snomed.info/sct',
              code: '443684005',
              display: 'Disease outbreak (event)'
            }
          ]
        }
      ],
      protocolApplied: [
        {
          doseNumberPositiveInt: 1
        }
      ]
    },
    search: {
      mode: 'match'
    }
  }
];

exports.covidImmunizationFhir = (dateFrom, dateTo) => {
  const filteredEntries = entries.filter(entry => isEntryWithinDateRange(entry, dateFrom, dateTo));
  const vaccineLength = filteredEntries.length;
  filteredEntries.push(patientFhir());
  return {
    resourceType: 'Bundle',
    type: 'searchset',
    total: vaccineLength,
    entry: filteredEntries
  };
};
