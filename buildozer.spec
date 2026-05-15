[app]
title = Delta AI Agent
package.name = deltaagent
package.domain = org.delta.agent
source.dir = app
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.0,pandas==2.0.3,yfinance==0.2.43,numpy==1.24.4,delta-rest-client==1.2.0,requests==2.31.0,android
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK
android.keep_screen_on = 1
android.wakelock = 1
android.enable_androidx = 1
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
