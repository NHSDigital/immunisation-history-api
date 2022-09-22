Feature: API does a thing

#Scenario: User restricted app
#    Given A user restricted app with attributes
#        | key                              | value                                                         |
#        | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
#        | nhs-login-allowed-proofing-level | P9                                                            |
#    And it has the api products application-restricted,user-restricted
#    And it has the following request params
#        | key                  | value                                         |
#        | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
#        | procedure-code:below | 90640007                                      |
#    And the following headers
#        | key    | value     |
#        | accept | version=2 |
#    When I make a request to the endpoint FHIR/R4/Immunization
#    Then the http response code is 200
#
#Scenario: Application restricted app
#    Given An app restricted app with attributes
#        | key | value |
#        | apim-app-flow-vars | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
#        | nhs-login-allowed-proofing-level | p5 |
#    And it has the following request params
#        | key | value |
#        | patient.identifier | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
#        | procedure-code:below | 90640007 |
#    And the following headers
#        | key | value |
#        | accept | version=2 |
#    When I make a request to the endpoint FHIR/R4/Immunization
#    Then the http response code is 200


    Scenario Outline: app restricted request - <api_products>
        Given An app restricted app with attributes
            | key | value |
            | apim-app-flow-vars | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | p5 |
        And it has the api products <api_products>
        And it has the following request params
            | key | value |
            | patient.identifier | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007 |
        And the following headers
            | key | value |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 200

        Examples:
            | api_products                           |
            | application-restricted                 |
            | application-restricted,user-restricted |
