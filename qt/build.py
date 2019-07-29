# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from bincrafters import build_template_default
from os import getenv
from sys import exit

if __name__ == "__main__":
    # Qt only supports latest and greatest SDKs
    if (getenv('CONAN_APPLE_CLANG_VERSIONS', '0') != '10.0'): exit(0)

    bbuilder = build_template_default.get_builder()
    bbuilder.run()
