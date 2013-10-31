# Cactus Sparkle Site

Use Cactus for your Sparkle updates. This is a Cactus template to automatically version, package and sign your mac desktop application builds with Sparkle, generate an appcast.xml file, and keep an upload archive.

## Preparing your site

- Deploy at least once so cactus knows about the url
- Add te public key to your application

## Preparing your app

- Add Sparkle
- Add build.py <build/Release/YourApp.app> as a step in your build script
- Run cactus upload in this folder to upload
- Set the SUPublicDSAKeyFile to yout key name
- Set the SUFeedURL to http://<your-url>/appcast.xml

### Example

http://glueprint-update.s3-website-us-east-1.amazonaws.com/archive/
http://glueprint-update.s3-website-us-east-1.amazonaws.com/appcast.xml

### Versioning

Based on git describe --tags. Make sure you have at least one commit tagged with the format 1.0.0.

### Todo

- Halt on uncomitted changes in build.py
- Make latest.html that redirects to latest download