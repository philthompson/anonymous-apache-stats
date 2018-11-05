import sys
import csv
import datetime
import calendar

# number of views by day

# number of unique visitors by day

# articles

# top 10 articles: total unique visitors
# (full list at bottom of output)

# top 10 articles: viewed by percent of seen visitors
# (full list at bottom of output)

# top 10 articles: total views, percent of total views
# (full list at bottom of output)

# top 10 articles: views per visitor per day
# (full list at bottom of output)

# search engines

# top 10 most-viewed articles: percent of views with each referrer domain
# (full list at bottom of output)

# top 10 most-viewed articles: percent of views with each seen search engine keyword
# (full list at bottom of output)

# top 10 most-viewed articles: percent of views with each seen platform-os
# (full list at bottom of output)

# top 10 most-viewed articles: percent of views with each seen platform-form-factor
# (full list at bottom of output)

def get_weekday_from_iso_date(iso_date):
	date_y = int(iso_date[0:4])
	date_m = int(iso_date[5:7])
	date_d = int(iso_date[8:10])
	return calendar.day_name[datetime.date(date_y, date_m, date_d).weekday()]

field_names = [
	'date-time', 'visitor-day-id', 'http-verb', 'uri', 'proto', 'resp-code',
	'resp-size', 'referrer-domain', 'search-engine', 'search-engine-keywords',
	'platform-os', 'platform-form-factor'
]

csv_reader = csv.DictReader(sys.stdin, fieldnames=field_names, delimiter=' ')

view_visitors_by_day = dict()
views_by_day = dict()

all_visitors_by_day = dict()

for row in csv_reader:
	date = row['date-time'][0:10]
	# count only successful html page GET requests as a "page view"
	if row['http-verb'] == 'GET' and row['resp-code'][0:1] in ['2','3'] and (row['uri'].endswith('/') or row['uri'].lower().endswith('.html')):
		if not date in views_by_day:
			views_by_day[date] = 0
		views_by_day[date] += 1

		if not date in view_visitors_by_day:
			view_visitors_by_day[date] = dict()
		view_visitors_by_day[date][row['visitor-day-id']] = None

	if not date in all_visitors_by_day:
		all_visitors_by_day[date] = dict()
	all_visitors_by_day[date][row['visitor-day-id']] = None
	print("at %s (%s) saw %s" % (date, row['date-time'], row['visitor-day-id']))

print("Successful page views by day:")
for date in sorted(views_by_day):
	day_name = get_weekday_from_iso_date(date)
	print("%s %s - %d" % (day_name, date, views_by_day[date]))
print("")

print("Number of visitors with at least one successful page view by day:")
for date in sorted(view_visitors_by_day):
	day_name = get_weekday_from_iso_date(date)
	print("%s %s - %d" % (day_name, date, len(view_visitors_by_day[date])))
print("")

print("Number of visitors with at least one HTTP request by day:")
for date in sorted(all_visitors_by_day):
	day_name = get_weekday_from_iso_date(date)
	print("%s %s - %d" % (day_name, date, len(all_visitors_by_day[date])))
print("")