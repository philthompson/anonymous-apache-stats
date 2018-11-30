import sys
import re
import datetime
import hashlib
import binascii
import urlparse
import random

# this is intended to be run with python 2.7

# apache's "combined" format
#
# this script's gosal for output:
# date-time, visitor-day-id, http-verb, uri, proto, resp-code, resp-size, referrer-domain, search-engine, search-engine-keywords, platform-os, platform-form-factor

ips_to_drop = []
useragent_contains_to_drop = []
for arg_val in sys.argv[2:]:
	if arg_val.startswith("ips_to_drop="):
		ips_to_drop = [x.lower() for x in arg_val[12:].split(',')]
	elif arg_val.startswith("useragent_contains_to_drop="):
		useragent_contains_to_drop = arg_val[27:].split(',')

regex = '^([^ ]+) [^ ]+ [^ ]+ \[([^:]+):([^ ]+) ([^\]]+)\] "([^ ]+) ([^ ]+) ([^ ]+)" ([^ ]+) ([^ ]+) "([^"]+)" "([^"]+)"$'

lines = 0

srand = random.SystemRandom()

# create random salt for today's random visitor day ID lookup table
daily_pbkdf_salt = hex(srand.getrandbits(128))[2:-1]

# start randomness generator using SHA256 for visitor day ID lookup table
sha256 = hashlib.sha256(daily_pbkdf_salt)

visitor_day_id_table = dict()

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

		if ip.lower() in ips_to_drop:
			continue

		found_ua_to_drop = False
		for ua_to_drop in useragent_contains_to_drop:
			if ua_to_drop in useragent:
				found_ua_to_drop = True
				break
		if found_ua_to_drop:
			continue

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


		visitor_day_id = hashlib.pbkdf2_hmac('sha256', ("%s %s %s" % (date, ip, useragent)).encode('utf8'), daily_pbkdf_salt, 10000)
		# convert to hex, and truncate to 6 characters:
		# 6 hex characters has a space of 16 million possibilities, which is
		#   large enough to avoid collisions for our purposes yet should be
		#   small enough to add uncertainty when brute-forcing the ip+useragent
		visitor_day_id = binascii.hexlify(visitor_day_id)[-6:]

		# create a random 6-digit hex value for the ID if it doesn't already
		#   exist by providing the SHA-256 hash with more random data
		if not visitor_day_id in visitor_day_id_table:
			sha256.update(visitor_day_id)
			sha256.update(str(srand.getrandbits(32)))
			visitor_day_id_table[visitor_day_id] = sha256.hexdigest()[0:6]

		# set the ID to the random one
		visitor_day_id = visitor_day_id_table[visitor_day_id]

		# use tld and one domain label to the left of that for referrer domain
		# drop port from the hostname if one is present... probably won't be
		referrer_parse = urlparse.urlparse(referrer)
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
			#print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'ask.com':
			search_engine = 'ask'
			#print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/web' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'aol.com':
			search_engine = 'aol'
			#print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/aol/search' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('q='):
						search_engine_keywords = param[2:]
						break
		elif referrer_domain == 'baidu.com':
			search_engine = 'baidu'
			#print(referrer_parse)
			# almost the same keywords parsing as Google and Bing
			if referrer_parse.path.lower() == '/s' and referrer_parse.query:
				for param in referrer_parse.query.split('&'):
					if param.startswith('wd='):
						search_engine_keywords = param[3:].replace('%20', '+')
						break

		# since the output is space-delimited, the simplest option for now is
		#   to not URL-decode the search engine keywords
		#search_engine_keywords = urlparse.unquote(search_engine_keywords)

		platform = 'unk'
		form_factor = 'non-mobile'

		if 'Windows NT ' in useragent:
			platform = 'windows'
		elif 'Android' in useragent and 'Mobile' in useragent:
			platform = 'android'
			form_factor = 'mobile'
		# if Linux and not Android
		elif 'Linux' in useragent:
			platform = 'linux'
		elif 'iPad;' in useragent and ' like Mac OS X)' in useragent:
			platform = 'ipad'
			form_factor = 'mobile'
		elif 'iPhone;' in useragent and ' like Mac OS X)' in useragent:
			platform = 'iphone'
			form_factor = 'mobile'
		elif 'Mac OS X 10_' in useragent:
			platform = 'macos'

		#print("-----")
		#print("ip: %s, date: %s, time: %s, time_zone: %s, iso_date: %s, verb: %s, uri: %s, proto: %s, resp_code: %s, resp_size: %s, referrer: %s, useragent: %s" % (ip, date, time, time_zone, date_time.isoformat(), verb, uri, proto, resp_code, resp_size, referrer, useragent))
		print("%sZ %s %s %s %s %s %s %s %s %s %s %s" % (date_time.isoformat(), visitor_day_id, verb, uri, proto, resp_code, resp_size, referrer_domain, search_engine, search_engine_keywords, platform, form_factor))
		#print("orig: %s" % (line.strip()))
		#print("-----")
		#lines += 1
		#if lines > 5:
		#	sys.exit(0)