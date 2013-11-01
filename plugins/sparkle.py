import os
import datetime
import logging
import json

Globals = {"config": {}, "releases": []}

sitePath = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
siteConfigPath = os.path.join(sitePath, "config.json")
siteReleaseLocation = os.path.join("static", "downloads")
siteReleasePath = os.path.join(sitePath, siteReleaseLocation)

# Check and load the config path
if os.path.exists(siteConfigPath):
	Globals["config"] = json.loads(open(siteConfigPath, "r").read())
else:
	logging.warning("Config file is missing at %s", siteConfigPath)

def preBuild(site):
	
	global Globals

	for path in os.listdir(siteReleasePath):
		
		if not path.endswith(".json"):
			continue

		releaseInfo = json.loads(open(os.path.join(siteReleasePath, path), "r").read())

		print "* %s %s (%s)" % (
			releaseInfo["applicationName"],
			releaseInfo["applicationVersion"]["version"],
			releaseInfo["applicationVersion"]["build"])

		Globals["releases"].append(releaseInfo)

	# Reverse sort by build number
	Globals["releases"].sort(key=lambda x: 0 - x["applicationVersion"]["build"])

def preBuildPage(site, page, context, data):
	
	context["releases"] = Globals["releases"]
	context["config"] = {
		"website": Globals["config"]["aws-bucket-website"],
		"releases": siteReleaseLocation
	}

	if len(Globals["releases"]) > 0:
		context['latest'] = Globals["releases"][0]
	else:
		context['latest'] = None
	
	return context, data