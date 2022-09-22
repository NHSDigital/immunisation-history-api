Feature: API does a thing

    Scenario Outline: basic happy path
        Given <app_type> restricted app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | p5                                                            |
        And it has the api products application-restricted,user-restricted
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 200
        And the correlation id returned matches the request

        Examples:
            | app_type |
#            | user     |
            | app      |

    Scenario Outline: no oauth sad path
        Given <app_type> restricted app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | p5                                                            |
        And it has the api products application-restricted,user-restricted
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization with no oauth token
        Then the http response code is 401
        And the correlation id returned matches the request
        And the OperationOutcome error message is Provided access token is invalid

        Examples:
            | app_type |
#            | user     |
            | app      |

    Scenario Outline: api product happy path
        Given <app_type> restricted app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products <api_products>
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 200
        And the correlation id returned matches the request

        Examples:
            | api_products                           | app_type |
            | application-restricted                 | app      |
            | application-restricted,user-restricted | app      |
#            | user-restricted                        | user     |
#            | application-restricted,user-restricted | user     |

    Scenario Outline: api product sad path invalid product
        Given <app_type> restricted app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products <api_products>
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is <status_code>
        And the error message is <error_message>

        Examples:
            | api_products           | app_type | status_code | error_message                                                                                                        |
#            | application-restricted | user     | 400         | authorization_code is invalid                                                                                        |
            | user-restricted        | app      | 401         | you have tried to requests authorization but your application is not configured to use this authorization grant type |

    Scenario Outline: api product sad path no products
        Given <app_type> restricted app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is <status_code>
        And the error message is <error_message>

        Examples:
            | app_type | status_code | error_message                                                                                                        |
#            | user     | 400         | authorization_code is invalid                                                                                        |
            | app      | 401         | you have tried to requests authorization but your application is not configured to use this authorization grant type |


    Scenario Outline: authorised targets happy path
        Given <app_type> restricted app with attributes
            | key                              | value                                                                    |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": [<authorised_targets>]}} |
            | nhs-login-allowed-proofing-level | P9                                                                       |
        And it has the api products application-restricted,user-restricted
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | <immunisation_target>                         |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 200
        And the correlation id returned matches the request

        Examples:
            | authorised_targets | app_type | immunisation_target |
            | "COVID19"          | app      | COVID19             |
            | "COVID19","HPV"    | app      | COVID19             |
            | "HPV"              | app      | HPV                 |
            | "COVID19","HPV"    | app      | HPV                 |
#            | "COVID19"          | user     | COVID19             |
#            | "COVID19","HPV"    | user     | COVID19             |
#            | "HPV"              | user     | HPV                 |
#            | "COVID19","HPV"    | user     | HPV                 |

    Scenario Outline: authorised targets sad path
        Given <app_type> restricted app with attributes
            | key                              | value                                                                    |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": [<authorised_targets>]}} |
            | nhs-login-allowed-proofing-level | P9                                                                       |
        And it has the api products application-restricted,user-restricted
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | <immunisation_target>                         |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 401
        And the correlation id returned matches the request
        And the OperationOutcome error message is You do not have permission to access this resource

        Examples:
            | authorised_targets | app_type | immunisation_target |
            | "COVID19"          | app      | HPV                 |
            | "HPV"              | app      | COVID19             |
#            | "COVID19"          | user     | HPV                 |
#            | "HPV"              | user     | COVID19             |
            | "RANDOM"           | app      | COVID19             |
#            | "RANDOM"           | user     | COVID19             |
