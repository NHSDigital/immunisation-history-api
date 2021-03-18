# Immunisation History

![Build](https://github.com/NHSDigital/immunisation-history/workflows/Build/badge.svg?branch=master)

This is a RESTful HL7® FHIR® API specification for the *Immunisation-History* API.

* `specification/` This [Open API Specification](https://swagger.io/docs/specification/about/) describes the endpoints, methods and messages exchanged by the API. Use it to generate interactive documentation; the contract between the API and its consumers.
* `sandbox/` This NodeJS application implements a mock implementation of the service. Use it as a back-end service to the interactive documentation to illustrate interactions and concepts. It is not intended to provide an exhaustive/faithful environment suitable for full development and testing.
* `scripts/` Utilities helpful to developers of this specification.
* `proxies/` Live (connecting to another service) and sandbox (using the sandbox container) Apigee API Proxy definitions.

Consumers of the API will find developer documentation on the [NHS Digital Developer Hub](https://developer.digital.nhs.uk/).

## Contributing
Contributions to this project are welcome from anyone, providing that they conform to the [guidelines for contribution](https://github.com/NHSDigital/immunisation-history/blob/master/CONTRIBUTING.md) and the [community code of conduct](https://github.com/NHSDigital/immunisation-history/blob/master/CODE_OF_CONDUCT.md).

### Licensing
This code is dual licensed under the MIT license and the OGL (Open Government License). Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.

The contents of this repository are protected by Crown Copyright (C).

