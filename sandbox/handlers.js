'use strict';
const { immunization } = require('./immunization-handler');
const { writeLog } = require('./logging');

async function status(req, res, next) {
  res.json({
    status: 'pass',
    ping: 'pong',
    service: req.app.locals.app_name,
    version: req.app.locals.version_info
  });
  res.end();
  next();
}

async function hello(req, res, next) {
  writeLog(res, 'warn', {
    message: 'hello world',
    req: {
      path: req.path,
      query: req.query,
      headers: req.rawHeaders
    }
  });

  res.json({ message: 'hello world' });
  res.end();
  next();
}

exports.status = status;
exports.hello = hello;
exports.immunization = immunization;
