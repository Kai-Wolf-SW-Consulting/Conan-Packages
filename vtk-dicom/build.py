# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(archs=["x86_64"])
    builder.add_common_builds(pure_c=False)
    builder.run()
