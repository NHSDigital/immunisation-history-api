const { getMajorVersion, extractVersionFromAcceptHeader } = require('./versioning');
const { API_VERSIONS } = require('./constants');
const { badRequest } = require('./api-response');

function getHandler(req) {
  try {
    const handlers = {
      [getMajorVersion(API_VERSIONS.V1)]: require('./v1/handler'),
      [getMajorVersion(API_VERSIONS.V2)]: require('./v2/handler')
    };

    const version = extractVersionFromAcceptHeader(req.headers['accept']);
    return handlers[getMajorVersion(version)];
  } catch {
    return null;
  }
}

async function immunization(req, res, next) {
  const handler = getHandler(req);
  if (!handler) {
    const { status, response } = badRequest('Invalid version', null);
    res.status(status).json(response);
  } else {
    const { status, response, headers } = handler(req, res);
    res.set(headers).status(status).json(response);
  }
  res.end();
  next();
}

exports.immunization = immunization;
