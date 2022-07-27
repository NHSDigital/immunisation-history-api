const { isEntryWithinDateRange } = require('./response-helper');
const { patientFhir } = require('./patient.fhir');

const entries = [
  {
    fullUrl: 'urn:uuid:2131f1bd-bc3d-4351-a3a4-8e062255dc75',
    resource: {
      doseQuantity: {
        code: '3318611000001103',
        system: 'http://snomed.info/sct',
        unit: 'pre-filled disposable injection',
        value: 1
      },
      expirationDate: '2021-04-29',
      extension: [
        {
          url: 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure',
          valueCodeableConcept: {
            coding: [
              {
                code: '149481000000105',
                display:
                  'Administration of vaccine product containing only Human papillomavirus 6, 11, 16, 18, 31, 33, 45, 52 and 58 antigens (procedure)',
                system: 'http://snomed.info/sct'
              }
            ]
          }
        }
      ],
      identifier: [
        {
          system: 'https://supplierABC/identifiers/vacc',
          use: 'secondary',
          value: '149481000000105'
        }
      ],
      location: {
        identifier: {
          system: 'urn:iso:std:iso:3166',
          value: 'GB'
        }
      },
      lotNumber: 'R04X',
      manufacturer: {
        display: 'GlaxoSmithKline UK Ltd'
      },
      occurrenceDateTime: '2020-12-23T13:00:08.476+00:00',
      patient: {
        identifier: {
          system: 'https://fhir.nhs.uk/Id/nhs-number',
          value: '9912003993'
        },
        reference: 'urn:uuid:e9414f7c-cd29-4228-875a-3fa6b098b616',
        type: 'Patient'
      },
      performer: [
        {
          actor: {
            display: 'TEST-SITE',
            identifier: {
              value: 'X99999'
            },
            type: 'Organization'
          }
        }
      ],
      primarySource: true,
      protocolApplied: [
        {
          doseNumberPositiveInt: 1
        }
      ],
      reasonCode: [
        {
          coding: [
            {
              code: '443684005',
              display: 'Disease outbreak (event)',
              system: 'http://snomed.info/sct'
            }
          ]
        }
      ],
      recorded: '2020-12-23',
      reportOrigin: {},
      resourceType: 'Immunization',
      route: {
        coding: [
          {
            code: '78421000',
            display: 'Intramuscular route (qualifier value)',
            system: 'http://snomed.info/sct'
          }
        ]
      },
      site: {
        coding: [
          {
            code: '368208006',
            display: 'Left upper arm structure (body structure)',
            system: 'http://snomed.info/sct'
          }
        ]
      },
      status: 'completed',
      vaccineCode: {
        coding: [
          {
            code: '12238911000001100',
            display:
              'Cervarix vaccine suspension for injection 0.5ml pre-filled syringes (GlaxoSmithKline) (product)',
            system: 'http://snomed.info/sct'
          }
        ]
      }
    },
    search: {
      mode: 'match'
    }
  },
  {
    fullUrl: 'urn:uuid:9c92fd94-c26e-4095-a28c-d43e9b14fa26',
    resource: {
      doseQuantity: {
        code: '3318611000001103',
        system: 'http://snomed.info/sct',
        unit: 'pre-filled disposable injection',
        value: 1
      },
      expirationDate: '2021-04-29',
      extension: [
        {
          url: 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure',
          valueCodeableConcept: {
            coding: [
              {
                code: '149481000000105',
                display:
                  'Administration of vaccine product containing only Human papillomavirus 6, 11, 16, 18, 31, 33, 45, 52 and 58 antigens (procedure)',
                system: 'http://snomed.info/sct'
              }
            ]
          }
        }
      ],
      identifier: [
        {
          system: 'https://supplierABC/identifiers/vacc',
          use: 'secondary',
          value: '1324761000000100'
        }
      ],
      location: {
        identifier: {
          system: 'urn:iso:std:iso:3166',
          value: 'GB'
        }
      },
      lotNumber: 'R04X',
      manufacturer: {
        display: 'GlaxoSmithKline UK Ltd'
      },
      occurrenceDateTime: '2020-12-24T13:00:08.476+00:00',
      patient: {
        identifier: {
          system: 'https://fhir.nhs.uk/Id/nhs-number',
          value: '9912003993'
        },
        reference: 'urn:uuid:e9414f7c-cd29-4228-875a-3fa6b098b616',
        type: 'Patient'
      },
      performer: [
        {
          actor: {
            display: 'TEST-SITE',
            identifier: {
              value: 'X99999'
            },
            type: 'Organization'
          }
        }
      ],
      primarySource: true,
      protocolApplied: [
        {
          doseNumberPositiveInt: 1
        }
      ],
      reasonCode: [
        {
          coding: [
            {
              code: '443684005',
              display: 'Disease outbreak (event)',
              system: 'http://snomed.info/sct'
            }
          ]
        }
      ],
      recorded: '2020-12-23',
      reportOrigin: {},
      resourceType: 'Immunization',
      route: {
        coding: [
          {
            code: '78421000',
            display: 'Intramuscular route (qualifier value)',
            system: 'http://snomed.info/sct'
          }
        ]
      },
      site: {
        coding: [
          {
            code: '368208006',
            display: 'Left upper arm structure (body structure)',
            system: 'http://snomed.info/sct'
          }
        ]
      },
      status: 'completed',
      vaccineCode: {
        coding: [
          {
            code: '12238911000001100',
            display:
              'Cervarix vaccine suspension for injection 0.5ml pre-filled syringes (GlaxoSmithKline) (product)',

            system: 'http://snomed.info/sct'
          }
        ]
      }
    },
    search: {
      mode: 'match'
    }
  },
  {
    fullUrl: 'urn:uuid:2fda3056-fcd4-4a1f-98f3-4acb117843e8',
    resource: {
      doseQuantity: {
        code: '3318611000001103',
        system: 'http://snomed.info/sct',
        unit: 'pre-filled disposable injection',
        value: 1
      },
      expirationDate: '2021-04-29',
      extension: [
        {
          url: 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure',
          valueCodeableConcept: {
            coding: [
              {
                code: '149481000000105',
                display:
                  'Administration of vaccine product containing only Human papillomavirus 6, 11, 16, 18, 31, 33, 45, 52 and 58 antigens (procedure)',
                system: 'http://snomed.info/sct'
              }
            ]
          }
        }
      ],
      identifier: [
        {
          system: 'https://supplierABC/identifiers/vacc',
          use: 'secondary',
          value: '1324761000000100'
        }
      ],
      location: {
        identifier: {
          system: 'urn:iso:std:iso:3166',
          value: 'GB'
        }
      },
      lotNumber: 'R04X',
      manufacturer: {
        display: 'GlaxoSmithKline UK Ltd'
      },
      occurrenceDateTime: '2020-12-25T13:00:08.476+00:00',
      patient: {
        identifier: {
          system: 'https://fhir.nhs.uk/Id/nhs-number',
          value: '9912003993'
        },
        reference: 'urn:uuid:e9414f7c-cd29-4228-875a-3fa6b098b616',
        type: 'Patient'
      },
      performer: [
        {
          actor: {
            display: 'TEST-SITE',
            identifier: {
              value: 'X99999'
            },
            type: 'Organization'
          }
        }
      ],
      primarySource: true,
      protocolApplied: [
        {
          doseNumberPositiveInt: 1
        }
      ],
      reasonCode: [
        {
          coding: [
            {
              code: '443684005',
              display: 'Disease outbreak (event)',
              system: 'http://snomed.info/sct'
            }
          ]
        }
      ],
      recorded: '2020-12-23',
      reportOrigin: {},
      resourceType: 'Immunization',
      route: {
        coding: [
          {
            code: '78421000',
            display: 'Intramuscular route (qualifier value)',
            system: 'http://snomed.info/sct'
          }
        ]
      },
      site: {
        coding: [
          {
            code: '368208006',
            display: 'Left upper arm structure (body structure)',
            system: 'http://snomed.info/sct'
          }
        ]
      },
      status: 'not-done',
      statusReason: [
        {
          coding: [
            {
              system: 'http://snomed.info/sct',
              code: '310376006',
              display: 'Immunization consent not given'
            }
          ]
        }
      ],
      vaccineCode: {
        coding: [
          {
            code: '12238911000001100',
            display:
              'Cervarix vaccine suspension for injection 0.5ml pre-filled syringes (GlaxoSmithKline) (product)',

            system: 'http://snomed.info/sct'
          }
        ]
      }
    },
    search: {
      mode: 'match'
    }
  }
];

exports.hpvImmunizationFhir = (dateFrom, dateTo) => {
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
