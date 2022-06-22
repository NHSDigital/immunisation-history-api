const log = require('loglevel');

const writeLog = (res, log_level, options = {}) => {
  if (log.getLevel() > log.levels[log_level.toUpperCase()]) {
    return;
  }
  if (typeof options === 'function') {
    options = options();
  }
  let log_line = {
    timestamp: Date.now(),
    level: log_level,
    correlation_id: res.locals.correlation_id
  };
  if (typeof options === 'object') {
    options = Object.keys(options).reduce(function (obj, x) {
      let val = options[x];
      if (typeof val === 'function') {
        val = val();
      }
      obj[x] = val;
      return obj;
    }, {});
    log_line = Object.assign(log_line, options);
  }
  if (Array.isArray(options)) {
    log_line['log'] = {
      log: options.map(x => {
        return typeof x === 'function' ? x() : x;
      })
    };
  }

  log[log_level](JSON.stringify(log_line));
};

exports.writeLog = writeLog;
