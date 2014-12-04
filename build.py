#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import subprocess
import json
import plistlib
import time
import getpass

config = {}
config["path"] = os.path.realpath(os.path.dirname(__file__))
config["buildPath"] = os.path.join(config["path"], "static", "downloads")
config["siteConfigPath"] = os.path.join(config["path"], "config.json")
config["signScriptPath"] = os.path.join(config["path"], "sparkle", "tools", "sign_update.rb")
config["signKeyPublicPath"] = os.path.join(config["path"], "sparkle", "keys", "dsa_pub.pem")
config["signKeyPrivatePath"] = os.path.join(config["path"], "sparkle", "keys", "dsa_priv.pem")



def run():

    for key, path in config.iteritems():
        if not os.path.exists(path):
            print "Configuration error, path does not exist"
            print "config.%s: %s" % (key, path)
            sys.exit()

    if len(sys.argv) < 2:
        sys.exit("Missing application bundle. Usage: build.py MyApp.app")

    applicationPath = sys.argv[1]
    applicationPath = os.path.realpath(applicationPath)

    if  not os.path.exists(applicationPath) or \
        not os.path.isdir(applicationPath) or \
        not applicationPath.endswith(".app"):
        sys.exit("This does not look like an app bundle")

    applicationName = os.path.splitext(os.path.basename(applicationPath))[0]
    applicationPlistPath = os.path.join(applicationPath, "Contents", "Info.plist")

    if not os.path.exists(applicationPlistPath):
        sys.exit("No plist found at: %s", applicationPlistPath)

    applicationPlist = plistlib.readPlist(applicationPlistPath)
    applicationVersion = gitVersion(applicationPath)

    if gitBranchName(applicationPath) != "master":
        raise AssertionError('Branch not master but %s' % gitBranchName(applicationPath))

    # Write the new version to the application plist

    # applicationPlist["CFBundleVersion"] = str(applicationVersion["build"])
    # applicationPlist["CFBundleShortVersionString"] = str(applicationVersion["version"])

    print "Preparing %s %s (%s)" % (applicationName, applicationVersion["version"], applicationVersion["build"])

    # Writing to the plist breaks signing, we should just alert

    def assertEqual(a, b, name):
        if a != b: sys.exit("%s does not match '%s' '%s'" % (name, a, b))

    assertEqual(
        applicationPlist["CFBundleVersion"], 
        str(applicationVersion["build"]), 
        "CFBundleVersion")

    assertEqual(
        applicationPlist["CFBundleShortVersionString"], 
        str(applicationVersion["version"]), 
        "CFBundleShortVersionString")


    # Check if the cactus configuration is correct

    if not os.path.exists(config["siteConfigPath"]):
        sys.exit("No cactus config at: %s", config["siteConfigPath"])

    siteConfig = json.loads(open(config["siteConfigPath"], "r").read())

    siteBucketName = siteConfig.get("aws-bucket-name")
    siteBucketWebsite = siteConfig.get("aws-bucket-website")

    # Check if the right keys are in the plist
    plistSUFeedURL = applicationPlist.get("SUFeedURL")
    plistSUFeedURLActual = "http://%s/appcast.xml" % siteBucketWebsite

    plistSUPublicDSAKeyFile = applicationPlist.get("SUPublicDSAKeyFile")

    # if not plistSUFeedURL == plistSUFeedURLActual:
    #     sys.exit("SUFeedURL is not correct...\n-> %s\n-> %s" % (plistSUFeedURL, plistSUFeedURLActual))

    if not plistSUPublicDSAKeyFile:
        sys.exit("Missing key SUPublicDSAKeyFile in plist")


    # Package up the application in a versioned gzip file

    # applicationArchiveName = "%s-%s.tar.gz" % (applicationName, applicationVersion["version"])
    applicationArchiveName = "%s-%s.zip" % (applicationName, applicationVersion["version"])
    applicationArchivePath = os.path.join(config["buildPath"], applicationArchiveName)

    if os.path.exists(applicationArchivePath):
        os.remove(applicationArchivePath)

    print "%s (creating archive)" % applicationArchivePath

    # We use tar.gz because it's so much smaller then just zip
    # os.system("cd '%s'; /Volumes/Backup/usr/bin/tar -cz -f '%s' '%s'" % \
    #     (os.path.dirname(applicationPath), applicationArchivePath, os.path.basename(applicationPath)))

    os.system("cd '%s'; zip -r --symlinks '%s' '%s'" % \
        (os.path.dirname(applicationPath), applicationArchivePath, os.path.basename(applicationPath)))

    # Sign the package
    
    applicationArchiveSignature = subprocess.check_output("ruby '%s' '%s' '%s'" % \
        (config["signScriptPath"], applicationArchivePath, config["signKeyPrivatePath"]), shell=True).strip()

    if not len(applicationArchiveSignature) is 64:
        sys.exit("Could not sign application (length: %s)" % len(applicationArchiveSignature))

    # Create json info file

    applicationInfoName = "%s-%s.json" % (applicationName, applicationVersion["version"])
    applicationInfoPath = os.path.join(config["buildPath"], applicationInfoName)

    applicationInfo = {
        "time": int(time.time()),
        "author": getpass.getuser(), 
        "applicationName": applicationName,
        "applicationVersion": applicationVersion,
        "applicationArchiveName": applicationArchiveName,
        "applicationArchiveSignature": applicationArchiveSignature,
        "applicationArchiveSize": os.stat(applicationArchivePath).st_size
    }

    open(applicationInfoPath, "w").write(json.dumps(applicationInfo, sort_keys=True, indent=4))

    print "%s (writing info)" % applicationInfoPath


def gitBranchName(gitPath):
    return subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True).strip()

    if getBranchName(gitPath) != "master":
        raise AssertionError('Branch not master but %s' % getBranchName(gitPath))

def gitVersion(gitPath):

    def parse(build):
        
        parts = build.replace('-dirty', '').split('-')
        
        if len(parts) > 1: return "%s.%s" % (parts[0], parts[1])
        if len(parts) > 0: return "%s.0" % parts[0]
        
        raise AssertionError('Could not parse version')

    # assert parse('0.1') == '0.1.0'
    # assert parse('0.1-35-g4d57b8f') == '0.1.35'
    # assert parse('0.1-35') == '0.1.35'
    # assert parse('0.1-35-g4d57b8f-dirty') == '0.1.35'

    def sub(cmd):
        cmd = "cd '%s'; %s" % (gitPath, cmd)
        return subprocess.check_output(cmd, shell=True).strip()

    version = {
        "version": parse(sub('git describe --tags').strip('v')),
        "hash": sub('git describe --always --dirty'),
        "build": int(sub('git rev-list master| wc -l')),
    }

    return version


run()
