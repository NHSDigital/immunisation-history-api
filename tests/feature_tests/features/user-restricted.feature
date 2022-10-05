Feature: User restricted tests

    Scenario: user restricted basic happy path
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
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

    Scenario Outline: user restricted valid api product
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products <api_products>
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
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
            | api_products                           |
            | user-restricted                        |
            | application-restricted,user-restricted |

    Scenario: user restricted invalid api product
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products application-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 401
        And the error message is you have tried to requests authorization but your application is not configured to use this authorization grant type

    Scenario: user restricted no api product
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 401
        And the error message is you have tried to requests authorization but your application is not configured to use this authorization grant type

    Scenario Outline: user restricted authorised targets happy path
        Given apigee app with attributes
            | key                              | value                                                                    |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": [<authorised_targets>]}} |
            | nhs-login-allowed-proofing-level | P9                                                                       |
            | use_strict_authorised_targets    | False                                                                    |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
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
            | authorised_targets | immunisation_target |
            | "COVID19"          | COVID19             |
            | "COVID19","HPV"    | COVID19             |
            | "HPV"              | HPV                 |
            | "COVID19","HPV"    | HPV                 |
            | "*"                | HPV                 |
            | "*"                | COVID19             |

    Scenario Outline: user restricted authorised targets sad path
        Given apigee app with attributes
            | key                              | value                                                                    |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": [<authorised_targets>]}} |
            | nhs-login-allowed-proofing-level | P9                                                                       |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | <immunisation_target>                         |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is <status_code>
        And the correlation id returned matches the request
        And the OperationOutcome error message is <error_message>

        Examples:
            | authorised_targets | immunisation_target | status_code | error_message                                                                                   |
            | "COVID19"          | HPV                 | 401         | You do not have permission to access this resource                                              |
            | "HPV"              | COVID19             | 401         | You do not have permission to access this resource                                              |
            | "RANDOM"           | COVID19             | 401         | You do not have permission to access this resource                                              |
            | "*"                | hPv                 | 400         | Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target] |
            | "*"                | COViD19             | 400         | Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target] |
            | "*"                | RANDOM              | 400         | Missing or invalid required request parameters: [procedure-code:below] OR [immunization.target] |

    Scenario Outline: user restricted authorised targets strict mode sad path
        Given apigee app with attributes
            | key                              | value                                                                    |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": [<authorised_targets>]}} |
            | nhs-login-allowed-proofing-level | P9                                                                       |
            | use_strict_authorised_targets    | True                                                                     |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | <immunisation_target>                         |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 403
        And the correlation id returned matches the request

        Examples:
            | authorised_targets | immunisation_target |
            | "*"                | HPV                 |
            | "*"                | COVID19             |

    Scenario Outline: user restricted authorised targets in header
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | COVID19                                       |
        And the following headers
            | key          | value     |
            | accept       | version=2 |
            | <header_key> | COVID19   |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 404
        And the correlation id returned matches the request
        And the error message is AUTHORISED_TARGETS cannot be provided in headers

        Examples:
            | header_key         |
            | AUTHORISED_TARGETS |
            | authorised_targets |
            | autHORised_TArgets |

    Scenario: user restricted no oauth provided
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
        And the following request params
            | key                  | value                                         |
            | patient.identifier   | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | procedure-code:below | 90640007                                      |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        And no oauth token is provided
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 401
        And the correlation id returned matches the request
        And the OperationOutcome error message is Provided access token is invalid

    Scenario Outline: user restricted proofing level happy path
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | <requested_proofing_level>                                    |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level <identity_proofing_level>
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | COVID19                                       |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 200
        And the correlation id returned matches the request

        Examples:
            | requested_proofing_level | identity_proofing_level |
            | P9                       | P9                      |
            | P5                       | P9                      |
            | P5                       | P5                      |

    Scenario Outline: user restricted proofing level sad path
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | <requested_proofing_level>                                    |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level <identity_proofing_level>
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | COVID19                                       |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 401
        And the correlation id returned matches the request
        And the OperationOutcome error message is Unauthorized

        Examples:
            | requested_proofing_level | identity_proofing_level |
            | P9                       | P5                      |
            | P3                       | P5                      |

    Scenario Outline: user restricted proofing level out of scope
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | <requested_proofing_level>                                    |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level <identity_proofing_level>
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | COVID19                                       |
        And the following headers
            | key    | value     |
            | accept | version=2 |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 401
        And the error message is you have tried to requests authorization but your application is not configured to use this authorization grant type

        Examples:
            | requested_proofing_level | identity_proofing_level |
            | P5                       | P3                      |
            | P5                       | FOO                     |
            | P9                       | P3                      |
            | P9                       | FOO                     |

    Scenario Outline: user restricted x-request-url in header
        Given apigee app with attributes
            | key                              | value                                                         |
            | apim-app-flow-vars               | {"immunisation-history": {"authorised_targets": ["COVID19"]}} |
            | nhs-login-allowed-proofing-level | P9                                                            |
        And it has the api products user-restricted
        And the user is authenticated on nhs login with nhs number 9912003888 and proofing level P9
        And the following request params
            | key                 | value                                         |
            | patient.identifier  | https://fhir.nhs.uk/Id/nhs-number\|9912003888 |
            | immunization.target | COVID19                                       |
        And the following headers
            | key          | value           |
            | accept       | version=2       |
            | <header_key> | http://test.com |
        When I make a request to the endpoint FHIR/R4/Immunization
        Then the http response code is 404
        And the correlation id returned matches the request
        And the error message is X-Request-Url cannot be provided in headers

        Examples:
            | header_key    |
            | X-Request-Url |
            | X-REQUEST-URL |
            | x-request-url |



