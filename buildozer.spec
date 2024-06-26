[app]
# (str) Title of your application
title = MultyGameApp

# (str) Package name
package.name = multygameapp

# (str) Package domain (needed for Play Store / crash reporting)
package.domain = org.mygame

# (str) Source code where the main.py live
source.dir = .

# (str) Source code where the main.py is located
source.include_exts = py,png,jpg,kv

# (list) Source code patterns to exclude (comma separated)
source.exclude_exts = spec

# (str) Application versioning (method 1)
version = 0.1

# (str) Application icon
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of: landscape, sensorLandscape, portrait or all)
orientation = landscape

# (list) Permissions
# List of Android permissions here
# For example:
# android.permissions = INTERNET, ACCESS_WIFI_STATE, ACCESS_NETWORK_STATE

# (str) Presplash of your application
presplash.filename = %(source.dir)s/splash.png

# (str) Application entry point
entrypoint = main.py

# (list) Application requirements
requirements = python3,kivy,sqlite3,werkzeug,pillow

# (str) Bootstrap to use for the application
# Supported values: sdl2, service_only
bootstrap = sdl2

# (str) The directory in which python-for-android should look for your own recipes (if any)
#p4a.local_recipes = 

# (str) Custom source folders
#source.include_dirs = 

# (str) Directory to put temporary build files in
#build.tmp_dir = %(source.dir)s/.buildozer/tmp

# (str) Directory to put the application assets in
#build.assets_dir = %(source.dir)s/assets

# (str) Path to the buildozer.spec file
# (this should normally be just 'buildozer.spec')
#buildozer.spec_file = buildozer.spec

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) The minimum API level required to run the application
android.minapi = 21

# (str) The API level to target when creating the application
android.api = 31

# (str) The ndk API to use when creating the application
android.ndk_api = 21

# (str) The package format to use for the application
# Supported values: apk, aar, bundle
android.package_format = apk

# (bool) Indicate if the application should be built in debug or release mode
# (one of: debug, release)
android.debug = 1

# (list) Pattern to include in the source distribution
source.include_patterns = assets/*,breakout/*,color/*,color_match/*,fifteen_game/*,game2048/*,jigsaw/*,matchmaster/*,pong_game/*,sudoku/*,tictactoe/*

# (list) Pattern to exclude from the source distribution
source.exclude_patterns = build,*.pyc,*.pyo,*.swp,*.bak,*.tmp,*.old

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
