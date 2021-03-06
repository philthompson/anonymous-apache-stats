#!/bin/bash
#
# forwards all arguments beyond the first argument, and possibly the second
#   argument if it's "backup-existing", to the python script that does the
#   combined apache log file parsing and anonymization
#
# example:
#   ./getLogFileStats.sh <log_file> backup-existing ips_to_drop=a.b.c.d,e.f.g.h useragent_json_file_to_drop=crawler-user-agents-47a1419.json

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
		echo "    \"zcat '${OUT_FILE}' | python analyzeAnonymizedLogFile.py\""
		exit 1
	fi
fi

# pass all remaining arguments to the parse script
if [[ "$(echo "${1}" | rev | cut -c 1-3 | rev)" == ".gz" ]]
then
	python parseLogFile.py <(zcat "${1}") "$@"
else
	python parseLogFile.py "${1}" "$@"
fi | gzip > "${OUT_FILE}"


zcat "${OUT_FILE}" | python analyzeAnonymizedLogFile.py
