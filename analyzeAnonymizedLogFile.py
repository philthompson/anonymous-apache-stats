import sys
import csv
import datetime
import calendar
import re

# number of views by day

# number of unique visitors by day

# articles

# number of visitors by article by day

# top 10 most visitors for an article across all days:
#   "2018-11-01 article A: 40 visitors, 2018-11-05 article B: 36 visitors, ...")

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

# as of October 2021, consider any .html file an "article"
# (gallery pages do not have same URL pattern as articles, so
#   we need to use a more general pattern here)
#article_uri_pattern = re.compile("^/20[0-9][0-9]/.+\.html$")
article_uri_pattern = re.compile("^.+\.html$")

csv_reader = csv.DictReader(sys.stdin, fieldnames=field_names, delimiter=' ')

view_visitors_by_day = dict()
views_by_day = dict()

view_visitors_by_article_by_day = dict()

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

		# consider the home page "/" as an article
		if row['uri'] == '/' or row['uri'].lower() == '/index.html' or article_uri_pattern.match(row['uri']):
			if not date in view_visitors_by_article_by_day:
				view_visitors_by_article_by_day[date] = dict()
			if not row['uri'] in view_visitors_by_article_by_day[date]:
				view_visitors_by_article_by_day[date][row['uri']] = dict()
			view_visitors_by_article_by_day[date][row['uri']][row['visitor-day-id']] = None

	if not date in all_visitors_by_day:
		all_visitors_by_day[date] = dict()
	all_visitors_by_day[date][row['visitor-day-id']] = None
	#print("at %s (%s) saw %s" % (date, row['date-time'], row['visitor-day-id']))

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

article_days = dict()

print("Unique visitors per article by day:")
for date in sorted(view_visitors_by_article_by_day):
	day_name = get_weekday_from_iso_date(date)
	d = dict()
	for article in view_visitors_by_article_by_day[date]:
		d[article] = len(view_visitors_by_article_by_day[date][article])
	# thanks to https://stackoverflow.com/a/20948781
	day_article_visitors = [(k, d[k]) for k in sorted(d, key=d.get, reverse=True)]
	for article, visitors in day_article_visitors:
		article_day = "%s %s - %s" % (day_name, date, article)
		print("%s: %d" % (article_day, visitors))
		article_days[article_day] = visitors
print("")

print("Top 10 articles by unique visitors by day:")
for article_day in sorted(article_days, key=article_days.get, reverse=True)[0:10]:
	print("%s: %d" % (article_day, article_days[article_day]))
print("")