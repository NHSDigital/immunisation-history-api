Feature: Vanilla API call

    Scenario: Vanilla API call
        Given I will make a request with an app with attributes
            | key                | value                                                         |
            | apim-app-flow-vars | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
        And the app is authorised according to method "app-restricted"
        And the request is to be made to path "FHIR/R4/Immunization"
        And the request will have parameters
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the request will have headers
            | key    | value     |
            | accept | version=2 |
        When I execute the request via the "GET" method
        Then I get a response with status code "200"
        And the response is valid JSON
