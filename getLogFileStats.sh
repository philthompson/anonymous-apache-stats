#!/bin/bash

if [[ ! -s "${1}" ]]
then
	echo "must provide apache log file in combined format"
	exit 1
fi

OUT_FILE="anonymized-$(basename "${1}")-$(date +%s)".gz

python3 parseLogFile.py "${1}" | python3 analyzeAnonymizedLogFile.py

exit

python3 parseLogFile.py "${1}" | gzip > "${OUT_FILE}"

echo "anonymized log file written to ${OUT_FILE}"

echo -n "number of users: "
zcat "${OUT_FILE}" | grep "^..........................GET " | cut -d ' ' -f 2 | sort -u | wc -l
echo ""

echo -n ""