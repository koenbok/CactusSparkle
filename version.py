#!/usr/bin/env python
# encoding: utf-8

# Add to build scripts in XCode

import sys
import os
import subprocess
import plistlib

def gitVersion(gitPath):

    def parse(build):
        
        parts = build.replace('-dirty', '').split('-')
        
        if len(parts) > 1: return "%s.%s" % (parts[0], parts[1])
        if len(parts) > 0: return "%s.0" % parts[0]
        
        raise AssertionError('Could not parse version')

    def sub(cmd):
        cmd = "cd '%s'; %s" % (gitPath, cmd)
        return subprocess.check_output(cmd, shell=True).strip()

    return {
        "version": parse(sub('git describe --tags').strip('v')),
        "hash": sub('git describe --always --dirty'),
        "build": sub('git rev-list master | wc -l'),
    }

def writePlist(path, data):

    if not os.path.exists(path):
        sys.exit("Could not find plist at: %s" % path)

    plistData = plistlib.readPlist(path)

    for k, v in data.iteritems():
        plistData[k] = v

    plistlib.writePlist(plistData, path)



def run():

    applicationInfoListPath = os.path.join(
        os.environ.get('BUILT_PRODUCTS_DIR'), 
        os.environ.get('INFOPLIST_PATH'))

    applicationDSYMListPath = os.path.join(
        os.environ['DWARF_DSYM_FOLDER_PATH'], 
        os.environ['DWARF_DSYM_FILE_NAME'], 
        "Contents", "Info.plist")

    version = gitVersion(os.environ["PROJECT_DIR"])

    writePlist(applicationInfoListPath, {
        "CFBundleVersion": version["build"],
        "CFBundleShortVersionString": version["version"],
    })

run()