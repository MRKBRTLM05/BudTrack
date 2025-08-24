# BudTrack

BudTrack is a Python/Kivy-based Android app for simple budget tracking.  
This repository contains the source code and configuration for building the APK with [Buildozer](https://github.com/kivy/buildozer).

---

## Features
- Track income and expenses
- Local data storage (SQLite)
- Simple and lightweight Kivy UI

---

## Requirements

You’ll need the following on your build machine (tested on **WSL2 / Ubuntu**):

- Python 3.11 (recommended, newer versions may not work with python-for-android)
- [Buildozer](https://github.com/kivy/buildozer)
- Java JDK 17
- Android SDK/NDK (installed automatically by Buildozer)
- A Linux environment (WSL2 or native Linux; not supported on Windows directly)

---

## Setup

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/your-username/BudTrack.git
cd BudTrack

# Create and activate virtual environment
python3.11 -m venv buildozer-env
source buildozer-env/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel cython buildozer

Build APK

From the project root:

# Initialize buildozer (if buildozer.spec is not yet created)
buildozer init

# Build debug APK
buildozer -v android debug


The generated APK will be available in:

bin/BudTrack-0.1-arm64-v8a_armeabi-v7a-debug.apk

Install on Android device

Copy the APK to your phone or install directly via adb:

adb install -r bin/BudTrack-0.1-arm64-v8a_armeabi-v7a-debug.apk
