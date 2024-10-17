# Copyright (C) 2002-2020 CERN for the benefit of the ATLAS collaboration
################################################################################
# Package: Voxelisation
################################################################################

cmake_minimum_required(VERSION 3.8 FATAL_ERROR)
 
# Set project
project(Voxelisation VERSION 1.0.0)

# Find the needed external(s):
find_package( ROOT COMPONENTS Core RIO Hist Tree Physics)
find_package( LibXml2 REQUIRED)

include_directories(${ROOT_INCLUDE_DIRS} ${LIBXML2_INCLUDE_DIR} Root Voxelisation)

file(GLOB SOURCES "Root/*.cxx")

add_executable(runVoxelisation Root/runVoxelisation.cxx ${SOURCES})
target_link_libraries(runVoxelisation PUBLIC ${LIBXML2_LIBRARIES} Hist Tree Core Physics)
