const moment = require('moment');

function isEntryWithinDateRange(entry, dateFrom, dateTo) {
  const parseOccurrenceDateTime = moment(entry.resource.occurrenceDateTime);
  return parseOccurrenceDateTime.isSameOrAfter(dateFrom) && parseOccurrenceDateTime.isSameOrBefore(dateTo);
}

exports.isEntryWithinDateRange = isEntryWithinDateRange;
