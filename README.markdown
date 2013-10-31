# Preparing your site

- Deploy at least once so cactus knows about the url
- Add te public key to your application
- Set the SUPublicDSAKeyFile to yout key name
- Set the SUFeedURL to http://<your-domain>/appcast.xml

# Preparing your app


- Add build.py <YourApp.app> as a step in your build script
- Run cactus upload in this folder to upload


# Todo

- Check plist for needed keys
- Halt on uncomitted changes