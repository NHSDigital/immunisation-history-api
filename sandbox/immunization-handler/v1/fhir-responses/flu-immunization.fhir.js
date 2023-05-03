const { isEntryWithinDateRange } = require('./response-helper');
const { patientFhir } = require('./patient.fhir');

const entries = [
  {
    fullUrl: 'urn:uuid:f1f61af6-4a6f-4487-8579-70ce5c6abce4',
    resource: {
      resourceType: 'Immunization',
      extension: [
        {
          url: 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure',
          valueCodeableConcept: {
            coding: [
              {
                system: 'http://snomed.info/sct',
                code: '884861000000100',
                display:
                  'null'
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
            code: '22704311000001108',
            display:
              'Fluarix Tetra vaccine suspension for injection 0.5ml pre-filled syringes (GlaxoSmithKline UK Ltd) (product)'
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
      occurrenceDateTime: '2021-08-02T12:46:16.019+00:00',
      recorded: '2021-02-14',
      primarySource: true,
      manufacturer: {
        display: 'GlaxoSmithKline UK Ltd'
      },
      lotNumber: 'XDKOPHGTENHOIOVCTBFI',
      expirationDate: '2021-04-29',
      site: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '368209003',
            display: 'Right upper arm structure (body structure)'
          }
        ]
      },
      route: {
        coding: [
          {
            system: 'http://snomed.info/sct',
            code: '2164884015',
            display: 'Intracutaneous use'
          }
        ]
      },
      doseQuantity: {
        system: 'http://snomed.info/sct',
        value: 1,
        unit: 'Ampoule',
        code: '2535128013'
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
];

exports.fluImmunizationFhir = (dateFrom, dateTo) => {
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
