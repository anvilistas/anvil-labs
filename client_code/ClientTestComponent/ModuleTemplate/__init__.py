# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil

from ._anvil_designer import ModuleTemplateTemplate
from .ClassTemplate import ClassTemplate
from ...UnitTestTemplate import UnitTestTemplate

__version__ = "0.0.1"


class ModuleTemplate(ModuleTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.success = True
        self.rp_children = anvil.RepeatingPanel(item_template=ClassTemplate)
        self.rp_children.items = self.item["children"]
        
        self.module_tests = UnitTestTemplate(
            cp_role=self.item["card_role"],
            btn_role=self.item['btn_role'],
            btn_text=self.item["name"],
            test_desc=self.item["ref"].__doc__,
            icon_size=self.item["icon_size"],
            rp_panels=self.rp_children
        )

        self.add_component(self.module_tests)
