const moment = require('moment');

const { SK_DATE_FORMAT, EXTREME_DATES } = require('./constants');

function parseDate(dateString, defaultDate) {
  if (dateString) {
    return moment(dateString, SK_DATE_FORMAT, true);
  }
  return defaultDate;
}

function parseDateRange(rawDateFrom, rawDateTo) {
  return {
    dateFrom: parseDate(rawDateFrom, EXTREME_DATES.START),
    dateTo: parseDate(rawDateTo, EXTREME_DATES.END)
  };
}

function isValidDate(date) {
  return (
    date.isValid() &&
    date.isSameOrAfter(EXTREME_DATES.START) &&
    date.isSameOrBefore(EXTREME_DATES.END)
  );
}

function validateDateRange(dateFrom, dateTo) {
  if (!isValidDate(dateFrom)) {
    return 'Invalid request parameters: [date.from]';
  }

  if (!isValidDate(dateTo)) {
    return 'Invalid request parameters: [date.to]';
  }

  if (dateFrom > dateTo) {
    return 'Invalid request parameters: [date.from] is greater than [date.to]';
  }

  return null;
}

exports.validateDateRange = validateDateRange;
exports.parseDateRange = parseDateRange;
