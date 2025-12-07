[app]

# (str) Title of your application
title = QR Attendance Checker

# (str) Package name
package.name = qrattendance

# (str) Package domain (needed for android/ios packaging)
package.domain = org.attendance

# (source.dir) Source code directory where the main.py live
source.dir = ./final-project/src

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of exclusions using pattern matching
#source.exclude_patterns = tests/*,bin/*

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,flet,bcrypt,flask,flask-cors,python-dotenv

# (str) Supported orientation (landscape, sensorLandscape, portrait or sensorPortrait)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Requested permissions
android.permissions = INTERNET,CAMERA,ACCESS_NETWORK_STATE

# (str) Minimum API level
android.minapi = 21

# (str) Target API level
android.targetapi = 33

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy application icon to build directory
#android.icon_filename = %(source.dir)s/data/icon.png

# (str) Android specific meta-data to add in the manifest
android.meta_data = 

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya_icon_filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file for custom backup agent declaration within the manifest
#android.backup_xml_filename = %(source.dir)s/data/backup.xml

# (str) XML file for custom Java classes declaration within the manifest.
# Use this is only needed if you want to add Java classes not defined in the
# nn.Activity and list them in the manifest.xml automatically.
#android.add_manifest_xml_filename = %(source.dir)s/data/manifest.xml

# (str) proguard rules file
#android.proguard_filename = %(source.dir)s/proguard-rules.pro

# (str) Bootstrap to use (sdl2 is chosen by default)
p4a.bootstrap = sdl2

#
# Python for android (p4a) specific
#

# (bool) Enable AndroidX support. Enable this only if your project
# requires any AndroidX libraries
#android.enable_androidx = True

# (str) Android entrypoint to use
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy presplash png
#android.presplash_filename = %(source.dir)s/data/presplash.png

# (list) Gradle dependencies (ex. ['android.gradle:gradle:gradle_version'])
#p4a.gradle_dependencies = com.google.android.material:material:1.0.0

# (str) python-for-android specific argument to pass when building the app
#p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port = 5000

#
# Python Cryptography support
#

# (bool) Enable the use of SSL in your application
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warnings (1) or not (0)
warn_on_root = 1
