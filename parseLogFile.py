import sys
import re
import datetime
import hashlib
import base64
import urllib.parse

# this is intended to be run with python 3

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

		# random salt generated with "tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32"
		visitor_day_id = hashlib.pbkdf2_hmac('sha256', ("%s %s %s" % (date, ip, useragent)).encode('utf8'), '3PXVwTKdgYvlko38Z5BameWSut2FKINm'.encode('utf8'), 100000)
		# convert to base64, and truncate to 4 characters:
		# 4 base64 characters has a space of 16 million possibilities, which is
		#   large enough to avoid collisions for our purposes yet should be
		#   small enough to add uncertainty when brute-forcing the ip+useragent
		visitor_day_id = base64.b64encode(visitor_day_id).decode('utf8')[0:4]

		# use tld and one domain label to the left of that for referrer domain
		# drop port from the hostname if one is present... probably won't be
		referrer_parse = urllib.parse.urlparse(referrer)
		referrer_domain = '.'.join(referrer_parse.netloc.split(':')[0].split(".")[-2:]).lower()

		search_engine = 'unk'
		search_engine_keywords = '-'
		if referrer_domain == '':
			search_engine = 'None'
		elif referrer_domain == 'google.com':
			search_engine = 'google'
			# same keywords parsing as Bing
			if referrer_parse.path.lower() == '/search' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'bing.com':
			search_engine = 'bing'
			# same keywords parsing as Google
			if referrer_parse.path.lower() == '/search' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'yahoo.com':
			search_engine = 'yahoo'
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/search' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('p='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'duckduckgo.com':
			search_engine = 'duckduckgo'
			print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'ask.com':
			search_engine = 'ask'
			print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/web' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'aol.com':
			search_engine = 'aol'
			print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/aol/search' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'baidu.com':
			search_engine = 'baidu'
			print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/s' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('wd='):
						search_engine_keywords = param[3:].replace('%20', '+')
						break

		# since the output is space-delimited, the simplest option for now is
		#   to not URL-decode the search engine keywords
		#search_engine_keywords = urllib.parse.unquote(search_engine_keywords)


		print("-----")
		#print("ip: %s, date: %s, time: %s, time_zone: %s, iso_date: %s, verb: %s, uri: %s, proto: %s, resp_code: %s, resp_size: %s, referrer: %s, useragent: %s" % (ip, date, time, time_zone, date_time.isoformat(), verb, uri, proto, resp_code, resp_size, referrer, useragent))
		print("%sZ %s %s %s %s %s %s %s %s %s" % (date_time.isoformat(), visitor_day_id, verb, uri, proto, resp_code, resp_size, referrer_domain, search_engine, search_engine_keywords))
		print("orig: %s" % (line.strip()))
		print("-----")
		lines += 1
		if lines > 5:
			sys.exit(0)