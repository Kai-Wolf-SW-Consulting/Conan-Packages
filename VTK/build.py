# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from conan.packager import ConanMultiPackager
from copy import copy

if __name__ == "__main__":
    builder = ConanMultiPackager(archs=["x86_64"])
    builder.add_common_builds(pure_c=False)

    items = []
    for item in builder.items:
        if item.settings["compiler"] == "Visual Studio":
            MtOrMtd = item.settings["compiler.runtime"] == "MT" or item.settings["compiler.runtime"] == "MTd"
            if MtOrMtd: continue # Ignore MT runtime
        if item.options["VTK:shared"]: continue # Only static

        new_options = copy(item.options)
        new_options["VTK:qt"] = True
        items.append([item.settings, new_options, item.env_vars, item.build_requires])

        new_options = copy(item.options)
        new_options["VTK:minimal"] = True
        new_options["VTK:ioxml"] = True
        items.append([item.settings, new_options, item.env_vars, item.build_requires])

    builder.items = items
    builder.run()
