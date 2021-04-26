# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from conans import ConanFile, CMake, tools
from fnmatch import fnmatch
from os import path, rename, walk
import re


class VTKConan(ConanFile):
    name = "vtk"
    version = "9.0.1_master"
    description = "Visualization Toolkit by Kitware"
    url = "https://github.com/Kai-Wolf-SW-Consulting/Conan-Packages/VTK"
    homepage = "http://www.vtk.org/files/release"
    author = "Kai Wolf - SW Consulting <mail@kai-wolf.me>"
    license = "MIT"
    topics = ("vtk", "visualization", "toolkit")
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
        tools.get("https://gitlab.kitware.com/vtk/vtk/-/archive/master/vtk-master.zip")
        rename("vtk-master", self.source_subfolder)

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

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["VTK_MODULE_ENABLE_VTK_ChartsCore"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_CommonColor"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_CommonCore"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_FiltersParallelImaging"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_FiltersSMP"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_FiltersSources"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_IOGeometry"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_IOImage"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_IOOggTheora"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_ImagingStatistics"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_InteractionImage"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_InteractionStyle"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingContextOpenGL2"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingCore"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingFreeType"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingGL2PSOpenGL2"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingOpenGL2"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingVolumeOpenGL2"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_ViewsContext2D"] = "YES"
        cmake.definitions["VTK_MODULE_ENABLE_VTK_ViewsQt"] = "YES"
        if self.options.minimal:
            cmake.definitions["VTK_Group_StandAlone"] = "OFF"
            cmake.definitions["VTK_Group_Rendering"] = "OFF"
        if self.options.ioxml:
            cmake.definitions["Module_vtkIOXML"] = "ON"
        if self.options.qt:
            cmake.definitions["VTK_Group_Qt"] = "ON"
            cmake.definitions["VTK_MODULE_ENABLE_VTK_GUISupportQt"] = "YES"
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
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        if self.settings.os == 'Macos':
            lib_path = path.join(self.build_folder, 'lib')
            self.run('DYLD_LIBRARY_PATH={0} cmake --build build {1} -j'.format(
                lib_path, cmake.build_config))
        else:
            cmake.build()

    def cmake_fix_tbb_dependency_path(self, file_path):
        # Read in the file
        with open(file_path, 'r') as file:
            file_data = file.read()

        if file_data:
            # Replace the target string
            tbb_root = self.deps_cpp_info["tbb"].rootpath.replace('\\', '/')
            file_data = re.sub(tbb_root, r"${CONAN_TBB_ROOT}", file_data, re.M)

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
        cmake = self._configure_cmake()
        lib_cmake_path = path.join(self.package_folder, 'lib', 'cmake')
        self.output.info("Searching for *.cmake in %s" % lib_cmake_path)
        for fpath, subdirs, names in walk(lib_cmake_path):
            for name in names:
                if fnmatch(name, '*.cmake'):
                    cmake_file = path.join(fpath, name)
                    self.output.info("Patching %s" % cmake_file)
                    self.cmake_fix_tbb_dependency_path(cmake_file)
                    if tools.os_info.is_macos:
                        self.cmake_fix_macos_sdk_path(cmake_file)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [
            "include/vtk-%s" % self.short_version,
            "%s/include" % self.deps_cpp_info["tbb"].rootpath
        ]

        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
