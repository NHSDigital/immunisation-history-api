const { DEFAULT_VERSION } = require('./constants');
const VERSION_ARGUMENT = 'version';

function extractVersionFromAcceptHeader(accept) {
  if (accept === null || typeof accept === 'undefined') return DEFAULT_VERSION;
  if (typeof accept !== 'string') throw new Error('Accept header must be a string');
  const parts = accept
    .toLowerCase()
    .split(';')
    .map(s => s.trim())
    .map(s => s.split('=').map(x => x.trim()));
  const versionHeaderPart = parts.find(([k]) => k === VERSION_ARGUMENT);
  const version =
    versionHeaderPart && typeof versionHeaderPart[1] !== 'undefined'
      ? versionHeaderPart[1]
      : DEFAULT_VERSION;
  if (isNaN(Number(version))) throw new Error('Accept header version must be a number');
  return version;
}

function getMajorVersion(version) {
  return version.split('.')[0];
}

exports.extractVersionFromAcceptHeader = extractVersionFromAcceptHeader;
exports.getMajorVersion = getMajorVersion;
