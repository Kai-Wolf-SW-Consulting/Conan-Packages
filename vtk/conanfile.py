# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from conans import ConanFile, CMake, tools
from fnmatch import fnmatch
from os import path, rename, walk
import re


class VTKConan(ConanFile):
    name = "vtk"
    version = "8.2.0"
    description = "Visualization Toolkit by Kitware"
    url = "https://github.com/Kai-Wolf-SW-Consulting/Conan-Packages/VTK"
    homepage = "http://www.vtk.org/files/release"
    author = "Kai Wolf - SW Consulting <mail@kai-wolf.me>"
    license = "MIT"
    topics = ("vtk", "visualization", "toolkit")
    exports = ["CMakeLists.txt", "FindVTK.cmake", "vtknetcdf_snprintf.diff", "vtktiff_mangle.diff"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    source_subfolder = "source_subfolder"
    short_paths = True
    version_split = version.split('.')
    short_version = "%s.%s" % (version_split[0], version_split[1])
    options = {
        "shared": [True, False],
        "qt": [True, False],
        "mpi": [True, False],
        "smp": [True, False],
        "fPIC": [True, False],
        "minimal": [True, False],
        "ioxml": [True, False],
        "mpi_minimal": [True, False]
    }
    default_options = ("shared=False", "qt=True", "mpi=False", "fPIC=False", "minimal=False",
                       "smp=True", "ioxml=False", "mpi_minimal=False")

    def source(self):
        tools.get(self.homepage +
                  "/{0}/{1}-{2}.tar.gz".format(self.short_version, "VTK", self.version))
        extracted_dir = "VTK-" + self.version
        rename(extracted_dir, self.source_subfolder)
        tools.patch(base_path=self.source_subfolder, patch_file="vtknetcdf_snprintf.diff")
        tools.patch(base_path=self.source_subfolder, patch_file="vtktiff_mangle.diff")

    def requirements(self):
        if self.options.smp:
            self.requires("tbb/2019_U9@kwc/stable")
            self.options["tbb"].shared = True
        if self.options.qt:
            self.requires("qt/5.12.4@kwc/stable")
            self.options["qt"].shared = True
            self.options["qt"].xmlpatterns = True
            if tools.os_info.is_linux:
                self.options["qt"].x11extras = True

    def _system_package_architecture(self):
        if tools.os_info.with_apt:
            if self.settings.arch == "x86": return ':i386'
            elif self.settings.arch == "x86_64": return ':amd64'

        if tools.os_info.with_yum:
            if self.settings.arch == "x86": return '.i686'
            elif self.settings.arch == 'x86_64': return '.x86_64'
        return ""

    def build_requirements(self):
        pack_names = None
        if not self.options.minimal and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                pack_names = [
                    "freeglut3-dev", "mesa-common-dev", "mesa-utils-extra", "libgl1-mesa-dev",
                    "libglapi-mesa", "libsm-dev", "libx11-dev", "libxext-dev", "libxt-dev",
                    "libglu1-mesa-dev"
                ]

        if pack_names:
            installer = tools.SystemPackageTool()
            for item in pack_names:
                installer.install(item + self._system_package_architecture())

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        if self.options.minimal:
            cmake.definitions["VTK_Group_StandAlone"] = "OFF"
            cmake.definitions["VTK_Group_Rendering"] = "OFF"
        if self.options.ioxml:
            cmake.definitions["Module_vtkIOXML"] = "ON"
        if self.options.qt:
            cmake.definitions["VTK_Group_Qt"] = "ON"
            cmake.definitions["VTK_QT_VERSION"] = "5"
            cmake.definitions["VTK_BUILD_QT_DESIGNER_PLUGIN"] = "OFF"
        if self.options.smp:
            cmake.definitions["VTK_SMP_IMPLEMENTATION_TYPE"] = "TBB"
            cmake.definitions["TBB_ROOT"] = self.deps_cpp_info["tbb"].rootpath
        if self.options.mpi:
            cmake.definitions["VTK_Group_MPI"] = "ON"
            cmake.definitions["Module_vtkIOParallelXML"] = "ON"
        if self.options.mpi_minimal:
            cmake.definitions["Module_vtkIOParallelXML"] = "ON"
            cmake.definitions["Module_vtkParallelMPI"] = "ON"

        if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
            cmake.definitions["CMAKE_DEBUG_POSTFIX"] = "_d"

        if self.settings.os == 'Macos':
            self.env['DYLD_LIBRARY_PATH'] = path.join(self.build_folder, 'lib')
            self.output.info("cmake build: %s" % self.build_folder)

        cmake.configure(build_folder='build')
        if self.settings.os == 'Macos':
            lib_path = path.join(self.build_folder, 'lib')
            self.run('DYLD_LIBRARY_PATH={0} cmake --build build {1} -j'.format(lib_path, cmake.build_config))
        else:
            cmake.build()
        cmake.install()

    def cmake_fix_tbb_dependency_path(self, file_path):
        # Read in the file
        with open(file_path, 'r') as file:
            file_data = file.read()

        if file_data:
            # Replace the target string
            file_data = re.sub(
                repr(self.deps_cpp_info["tbb"].rootpath),
                r"${CONAN_TBB_ROOT}",
                file_data,
                re.M)

            # Write the file out again
            with open(file_path, 'w') as file:
                file.write(file_data)

    def cmake_fix_macos_sdk_path(self, file_path):
        # Read in the file
        with open(file_path, 'r') as file:
            file_data = file.read()

        if file_data:
            # Replace the target string
            file_data = re.sub(
                # Match sdk path
                r';/Applications/Xcode\.app/Contents/Developer/Platforms/MacOSX\.platform/Developer/SDKs/MacOSX\d\d\.\d\d\.sdk/usr/include',
                '',
                file_data,
                re.M)

            # Write the file out again
            with open(file_path, 'w') as file:
                file.write(file_data)

    def package(self):
        for fpath, subdirs, names in walk(path.join(self.package_folder, 'lib', 'cmake')):
            for name in names:
                if fnmatch(name, '*.cmake'):
                    cmake_file = path.join(fpath, name)
                    self.cmake_fix_tbb_dependency_path(cmake_file)
                    if tools.os_info.is_macos:
                        self.cmake_fix_macos_sdk_path(cmake_file)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.includedirs = [
            "include/vtk-%s" % self.short_version,
            "include/vtk-%s/vtknetcdf/include" % self.short_version,
            "include/vtk-%s/vtknetcdfcpp" % self.short_version,
            "%s/include" % self.deps_cpp_info["tbb"].rootpath
        ]

        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
