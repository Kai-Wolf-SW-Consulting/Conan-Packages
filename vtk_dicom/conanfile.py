# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from conans import ConanFile, CMake, tools
from os import sep

class VTKDicomConan(ConanFile):
    name = "vtk_dicom"
    version = "0.8.10"
    description = "DICOM for VTK"
    url = "https://github.com/Kai-Wolf-SW-Consulting/Conan-Packages/vtk-dicom"
    homepage = "https://github.com/dgobbi/vtk-dicom"
    author = "Kai Wolf - SW Consulting <mail@kai-wolf.me>"
    license = "BSD 3-Clause"
    topics = ("vtk", "dicom")
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    requires = "vtk/8.2.0@kwc/stable"
    exports_sources = "FindDICOM.cmake"

    def source(self):
        zipname = "v{0}.zip".format(self.version)
        tools.get(self.homepage + "/archive/" + zipname)
        # tools.patch(patch_file="cmake_config.patch", strip=1)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_PROGRAMS"] = "OFF"
        cmake.definitions["BUILD_TESTING"] = "OFF"
        vtk_root = self.deps_cpp_info["vtk"].rootpath.replace(sep, '/')
        cmake.definitions["CMAKE_PREFIX_PATH"] = vtk_root
        cmake.configure(source_folder="vtk-dicom-{0}".format(self.version))
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("FindDICOM.cmake", ".", ".")
