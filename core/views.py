import re
import os
from pprint import pformat
from django.shortcuts import render, reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.static import serve
from django.conf import settings # cool!
# from django.

# .fa-icon_name:before {
# 	content: "\code";
# }
parse_re = re.compile(r'''\.fa-(?P<icon_name>[\w-]*)(?::){1,2}(?:before|after)\s*{[^{}]*content\s*:\s*(?:[']([^']*)[']|["]([^"]*)["])\s*[^{}]*}''')
CSS_FILENAME = 'css/all.min.css'
SEARCH_QUERY_NAME = "query_string"


def _parse_icons(css_string):
	'''Gathter all icon names from a presumable fontawesome css file'''
	for mo in parse_re.finditer(css_string):
		icon_code = mo.group(2) or mo.group(3)
		yield mo.group('icon_name'), icon_code


def _get_icons(request, css_filename, where=os.path.join(settings.BASE_DIR, 'static')):
	css_file = serve(request, css_filename, where)
	# css = list(_parse_icons(b''.join(list(css_file.streaming_content))))
	icons = _parse_icons(b''.join(list(css_file.streaming_content)).decode())	# [('iname', hexcode), ...]
	return sorted(icons)


def _search(request, query, css_filename):
	query = query.lower()
	for icon in _get_icons(request, css_filename):
		if query in icon[0]:
			yield icon
		else:
			# get best match
			pass

def index(request):
	return render(request, 'core/index.html', {
		'icons': _get_icons(request, CSS_FILENAME),
		'query_name': SEARCH_QUERY_NAME
		})


def svgs(request):
	return render(request, 'core/svgs.html', {})


def search(request):
	try:
		query_string = request.GET[SEARCH_QUERY_NAME]
	except KeyError:
		return HttpResponseRedirect(reverse('index'))
	return render(request, 'core/index.html', {
		'icons': tuple(_search(request, query_string, CSS_FILENAME)),
		'query_name': SEARCH_QUERY_NAME,
		'query_placeholder_value': query_string
		})