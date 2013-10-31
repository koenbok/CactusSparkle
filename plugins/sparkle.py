import os
import datetime
import logging
import json

from cactus.utils.filesystem import fileList

CONFIG_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "config.json"))
RELEASE_PATH = 'static/downloads'
RELEASES = []
CONFIG = {}

def preBuild(site):
	
	global RELEASES
	global CONFIG

	if os.path.exists(CONFIG_PATH):
		data = json.loads(open(CONFIG_PATH, "r").read())
		CONFIG["website"] = data["aws-bucket-website"]
	else:
		logging.warning("Config file is missing at %s", CONFIG_PATH)


	files = os.listdir(RELEASE_PATH)
	files.sort(key=lambda x: 0 - os.path.getmtime(os.path.join(RELEASE_PATH, x)))
	
	for item in files:
		
		if 'latest' in item:
			continue
		
		if not item.endswith(".tar.gz"):
			continue
		
		try:
			name, version = item.replace('.tar.gz', '').split('-')
		except:
			continue

		try:
			signature = open(os.path.join(RELEASE_PATH, 
				item.replace('.tar.gz', '.signature')), 'r').read()
		except Exception, e:
			print "WARNING: Could not read signature for %s" % item
			continue
		
		fileLength = os.stat(os.path.join(RELEASE_PATH, item)).st_size
		
		logging.info('* %s', item)
		
		RELEASES.append({
			'name': name,
			'path': os.path.join(RELEASE_PATH, item),
			'file': item,
			'version': version.replace('v', ''),
			'signature': signature.strip(),
			'length': fileLength
		})

def preBuildPage(site, page, context, data):
	
	
	context['releases'] = RELEASES
	context['config'] = CONFIG

	context['latest'] = None

	if len(RELEASES) > 0:
		context['latest'] = RELEASES[0]
	
	return context, data