import sys
import re
import datetime

# apache's "combined" format
#
# this script's gosal for output:
# date-time, visitor-day-id, http-verb, uri, proto, resp-code, resp-size, referrer-domain, search-engine, search-engine-keywords, platform

regex = '^([^ ]+) [^ ]+ [^ ]+ \[([^:]+):([^ ]+) ([^\]]+)\] "([^ ]+) ([^ ]+) ([^ ]+)" ([^ ]+) ([^ ]+) "([^"]+)" "([^"]+)"$'

lines = 0

with open(sys.argv[1], 'r') as f:
	for line in f:
		if not line:
			continue

		match = re.search(regex, line)

		if not match:
			continue

		ip = match.group(1)
		date = match.group(2)
		time = match.group(3)
		time_zone = match.group(4)
		verb = match.group(5)
		uri = match.group(6)
		proto = match.group(7)
		resp_code = match.group(8)
		resp_size = match.group(9)
		referrer = match.group(10)
		useragent = match.group(11)

		date_time = datetime.datetime.strptime("%s %s" % (date, time), "%d/%b/%Y %H:%M:%S")

		# manually add/subtract hours and minutes offset for timezone, since python is too stupid to do this
		tz_hours = time_zone[1:3]
		tz_mins = time_zone[3:5]

		tz_timedelta = datetime.timedelta(hours=int(float(tz_hours)))
		tz_timedelta += datetime.timedelta(minutes=int(float(tz_mins)))

		# do +/- opposite of timezone offset to regain UTC time
		if time_zone[0:1] == "+":
			date_time -= tz_timedelta
		else:
			date_time += tz_timedelta

		print("-----")
		print("ip: %s, date: %s, time: %s, time_zone: %s, iso_date: %s, verb: %s, uri: %s, proto: %s, resp_code: %s, resp_size: %s, referrer: %s, useragent: %s" % (ip, date, time, time_zone, date_time.isoformat(), verb, uri, proto, resp_code, resp_size, referrer, useragent))
		print("%sZ %s %s %s %s %s" % (date_time.isoformat(), verb, uri, proto, resp_code, resp_size))
		print("orig: %s" % (line))
		print("-----")
		lines += 1
		if lines > 5:
			sys.exit(0)