# Vectorworks SDK (NOT committed)

The VWSDK is licensed and large — it does not live in this repo.

## Download instructions

1. Sign in at https://developer.vectorworks.net
2. Download the SDK matching your installed Vectorworks version (currently 2026)
3. Unzip into this directory so the layout becomes:
   ```
   sdk/
     SDKLib/
     Include/
     Tools/
   ```
4. The `.gitignore` rule keeps these subdirs out of git automatically.

## What it provides

C++ headers and static libraries for:
- Vectorworks document API (read layers, classes, records, geometry)
- Plug-in menu command registration
- Plug-in object event handlers
- Resource manager (for Plant Styles)

CMakeLists.txt picks these up via `find_package(VWSDK)` once configured.
