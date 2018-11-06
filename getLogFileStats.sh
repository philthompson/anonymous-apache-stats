#!/bin/bash

if [[ ! -s "${1}" ]]
then
	echo "must provide apache log file in combined format, optionally gzipped and ending with .gz extension"
	exit 1
fi

OUT_FILE="anonymized-$(basename "${1}")".gz

if [[ -s "${OUT_FILE}" ]]
then
	if [[ "${2}" == "backup-existing" ]]
	then
		mv "${OUT_FILE}" "anonymized-$(basename "${1}")-$(date +%s)".gz
	else
		echo "Anonymized log file [${OUT_FILE}] already exists"
		echo "Add a 'backup-existing' arg and try again, or delete/rename it, or just run:"
		echo "    \"zcat '${OUT_FILE}' | python3 analyzeAnonymizedLogFile.py\""
		exit 1
	fi
fi

if [[ "$(echo "${1}" | rev | cut -c 1-3 | rev)" == ".gz" ]]
then
	python3 parseLogFile.py <(zcat "${1}")
else
	python3 parseLogFile.py "${1}"
fi | gzip > "${OUT_FILE}"

zcat "${OUT_FILE}" | python3 analyzeAnonymizedLogFile.py
