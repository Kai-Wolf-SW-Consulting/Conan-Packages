# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from bincrafters import build_shared

if __name__ == "__main__":
    recipe = build_shared.get_recipe_path()
    bbuilder = build_shared.get_builder(build_policy=None)
    shared_option_name = None
    if (build_shared.is_shared()):
        shared_option_name = "%s:shared" % build_shared.get_name_from_recipe(recipe=recipe)

    bbuilder.add_common_builds(
        shared_option_name=shared_option_name, pure_c=False, dll_with_static_runtime=False)
    bbuilder.run()
