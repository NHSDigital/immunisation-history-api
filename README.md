# Immunisation History

![Build](https://github.com/NHSDigital/immunisation-history/workflows/Build/badge.svg?branch=master)

This is a RESTful HL7® FHIR® API specification for the *Immunisation-History* API.

* `specification/` This [Open API Specification](https://swagger.io/docs/specification/about/) describes the endpoints, methods and messages exchanged by the API. Use it to generate interactive documentation; the contract between the API and its consumers.
* `sandbox/` This NodeJS application implements a mock implementation of the service. Use it as a back-end service to the interactive documentation to illustrate interactions and concepts. It is not intended to provide an exhaustive/faithful environment suitable for full development and testing.
* `scripts/` Utilities helpful to developers of this specification.
* `proxies/` Live (connecting to another service) and sandbox (using the sandbox container) Apigee API Proxy definitions.

Consumers of the API will find developer documentation on the [NHS Digital Developer Hub](https://digital.nhs.uk/developer).

### Pre-requisites
You will need the following packages installing: 
    - [Poetry](https://python-poetry.org/docs/)
    - [get_token](https://docs.apigee.com/api-platform/system-administration/auth-tools#install)
And you will need to be granted access to the APIGEE    


### Testing
To test this locally you will need a local environment set up, please contact a developer managing this repo for local environment setup for testing.

#### Authorising immunisation targets in production

Successful deployment of consumer apps in production requires a custom attribute key-value pair with name `authorised_targets` and a value set to a comma-delimited list of target immunisations, e.g.

```yaml
authorised_targets: COVID19,HPV
```

or for a single immunisation target, e.g.:

```yaml
authorised_targets: COVID19
```

Invalid values of `authorised_targets` in production (in APIGEE validation) are:

* an empty value (indicated in testing by `""`)
* "`*`" (unless in non-production environments)

Additionally, requests with will be rejected if `authorised_targets` contains a value which is not one of the pre-defined target immunisation keywords. Contact the maintainers for the up-to-date set of target immunisation keywords.

:bulb: For non-production ("self-serve") environments: the custom attribute `authorised_targets` is not required to exist; if it doesn't exist it will automatically be set to "`*`" (i.e. valid for any target).

## Contributing
Contributions to this project are welcome from anyone, providing that they conform to the [guidelines for contribution](https://github.com/NHSDigital/immunisation-history/blob/master/CONTRIBUTING.md) and the [community code of conduct](https://github.com/NHSDigital/immunisation-history/blob/master/CODE_OF_CONDUCT.md).

### Licensing
This code is dual licensed under the MIT license and the OGL (Open Government License). Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.

The contents of this repository are protected by Crown Copyright (C).



