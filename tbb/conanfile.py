# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from conans import ConanFile, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration
from os import chdir, listdir, rename, path, environ


class TBBConan(ConanFile):
    name = "tbb"
    version = "2019_U9"
    license = "Apache-2.0"
    url = "https://github.com/conan-community/conan-tbb"
    homepage = "https://github.com/intel/tbb"
    description = """Intel TBB lets you write parallel C++ code"""
    author = "Kai Wolf - SW Consulting <mail@kai-wolf.me>"
    topics = ("tbb", "threading", "parallelism", "tbbmalloc")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "tbbmalloc": [True, False], "tbbproxy": [True, False]}
    default_options = {"shared": True, "tbbmalloc": False, "tbbproxy": False}
    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.os == "Macos" and \
           self.settings.compiler == "apple-clang" and \
           Version(self.settings.compiler.version.value) < "8.0":
            raise ConanInvalidConfiguration("%s %s couldn't be built by apple-clang < 8.0" % (self.name, self.version))
        if not self.options.shared:
            self.output.warn("Intel-TBB strongly discourages usage of static linkage")
        if self.settings.os != "Windows" and self.options.tbbproxy and \
           (not self.options.shared or \
            not self.options.tbbmalloc):
            raise ConanInvalidConfiguration("tbbproxy needs tbbmaloc and shared options")
        if self.settings.os == "Windows" and self.options.tbbproxy and \
           not self.options.tbbmalloc:
            raise ConanInvalidConfiguration("tbbproxy needs tbbmaloc and shared options")
        if self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("TBB could not be built as static lib on Windows")

    @property
    def is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    @property
    def is_mingw(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc'

    @property
    def is_clanglc(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'clang'

    def source(self):
        sha256 = "15652f5328cf00c576f065e5cd3eaf3317422fe82afb67a9bcec0dc065bd2abe"
        tools.get("{}/archive/{}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        rename("{}-{}".format(self.name.lower(), self.version), self._source_subfolder)

        # Get the version of the current compiler instead of gcc
        linux_include = path.join(self._source_subfolder, "build", "linux.inc")
        tools.replace_in_file(linux_include, "shell gcc", "shell $(CC)")
        tools.replace_in_file(linux_include, "= gcc", "= $(CC)")

    def get_targets(self):
        targets = ["tbb"]
        if self.options.tbbmalloc:
            targets.append("tbbmalloc")
        if self.options.tbbproxy:
            targets.append("tbbproxy")
        return targets

    def build(self):
        def add_flag(name, value):
            if name in environ:
                environ[name] += ' ' + value
            else:
                environ[name] = value

        extra = "" if self.settings.os == "Windows" or self.options.shared else "extra_inc=big_iron.inc"
        if self.settings.arch == "x86":
            arch = "ia32"
        elif self.settings.arch == "x86_64":
            arch = "intel64"
        elif self.settings.arch == "armv7":
            arch = "armv7"
        elif self.settings.arch == "armv8":
            arch = "aarch64"
        if self.settings.compiler in ['gcc', 'clang', 'apple-clang']:
            if str(self.settings.compiler.libcxx) in ['libstdc++', 'libstdc++11']:
                extra += " stdlib=libstdc++"
            elif str(self.settings.compiler.libcxx) == 'libc++':
                extra += " stdlib=libc++"
            extra += " compiler=gcc" if self.settings.compiler == 'gcc' else " compiler=clang"

            extra += " gcc_version={}".format(str(self.settings.compiler.version))
        make = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which('mingw32-make'))
        if not make:
            raise ConanInvalidConfiguration("This package needs 'make' in the path to build")

        with tools.chdir(self._source_subfolder):
            # intentionally not using AutoToolsBuildEnvironment for now - it's broken for clang-cl
            if self.is_clanglc:
                add_flag('CFLAGS', '-mrtm')
                add_flag('CXXFLAGS', '-mrtm')

            targets = self.get_targets()
            if self.is_msvc:
                # intentionally not using vcvars for clang-cl yet
                with tools.vcvars(self.settings):
                    self.run("%s arch=%s %s %s" % (make, arch, extra, " ".join(targets)))
            elif self.is_mingw:
                self.run("%s arch=%s compiler=gcc %s %s" % (make, arch, extra, " ".join(targets)))
            else:
                self.run("%s arch=%s %s %s" % (make, arch, extra, " ".join(targets)))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src="%s/include" % self._source_subfolder)
        self.copy(pattern="*", dst="include/tbb/compat", src="%s/include/tbb/compat" % self._source_subfolder)
        build_folder = "%s/build/" % self._source_subfolder
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        self.copy(pattern="*%s*.lib" % build_type, dst="lib", src=build_folder, keep_path=False)
        self.copy(pattern="*%s*.a" % build_type, dst="lib", src=build_folder, keep_path=False)
        self.copy(pattern="*%s*.dll" % build_type, dst="bin", src=build_folder, keep_path=False)
        self.copy(pattern="*%s*.dylib" % build_type, dst="lib", src=build_folder, keep_path=False)
        # Copy also .dlls to lib folder so consumers can link against them directly when using MinGW
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self.copy("*%s*.dll" % build_type, dst="lib", src=build_folder, keep_path=False)

        if self.settings.os == "Linux":
            # leaving the below line in case MacOSX build also produces the same bad libs
            extension = "dylib" if self.settings.os == "Macos" else "so"
            if self.options.shared:
                self.copy("*%s*.%s.*" % (build_type, extension), "lib", build_folder,
                          keep_path=False)
                outputlibdir = path.join(self.package_folder, "lib")
                chdir(outputlibdir)
                for fpath in listdir(outputlibdir):
                    self.run("ln -s \"%s\" \"%s\"" %
                             (fpath, fpath[0:fpath.rfind("." + extension) + len(extension) + 1]))

    def package_info(self):
        suffix = "_debug" if self.settings.build_type == "Debug" else ""
        libs = {"tbb": "tbb", "tbbproxy": "tbbmalloc_proxy", "tbbmalloc": "tbbmalloc"}
        targets = self.get_targets()
        self.cpp_info.libs = ["{}{}".format(libs[target], suffix) for target in targets]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
