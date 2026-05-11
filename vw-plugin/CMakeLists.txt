cmake_minimum_required(VERSION 3.20)
project(lattice_vw_plugin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# VWSDK is downloaded into sdk/ (not committed). Update VW_SDK_ROOT if it lives
# elsewhere on your machine.
set(VW_SDK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/sdk" CACHE PATH "Vectorworks SDK root")

if(NOT EXISTS "${VW_SDK_ROOT}/Include")
  message(FATAL_ERROR
    "Vectorworks SDK not found at ${VW_SDK_ROOT}. "
    "Download from https://developer.vectorworks.net and unzip into vw-plugin/sdk/. "
    "See vw-plugin/sdk/README.md for instructions.")
endif()

include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${VW_SDK_ROOT}/Include
)

add_library(lattice_vw_plugin MODULE
  src/plugin-entry.cpp
  src/PlaceholderCmd.cpp
  src/MCPBridge.cpp
  src/GeometryUtils.cpp
)

if(APPLE)
  set_target_properties(lattice_vw_plugin PROPERTIES
    BUNDLE TRUE
    BUNDLE_EXTENSION "vwlibrary"
    PREFIX ""
  )
elseif(WIN32)
  set_target_properties(lattice_vw_plugin PROPERTIES
    SUFFIX ".vwlibrary"
    PREFIX ""
  )
endif()

# TODO: target_link_libraries against the VWSDK static libs once they're unzipped.
# target_link_libraries(lattice_vw_plugin PRIVATE VWSDK)
