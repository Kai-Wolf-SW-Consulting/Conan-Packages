# Copyright (c) 2019, Kai Wolf - SW Consulting. All rights reserved.
# For the licensing terms see LICENSE file in the root directory. For the
# list of contributors see the AUTHORS file in the same directory.

from bincrafters import build_template_default

if __name__ == "__main__":
    bbuilder = build_template_default.get_builder()
    bbuilder.run()
