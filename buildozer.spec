[app]

title = ANKIT PRO Calculator
package.name = ankitprocalculator
package.domain = org.ankit

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy,charset-normalizer==2.1.1
orientation = portrait
fullscreen = 0

[buildozer]

log_level = 2
warn_on_root = 1

[android]

android.permissions = INTERNET
android.archs = arm64-v8a
android.api = 35
android.minapi = 23
android.accept_sdk_license = True
