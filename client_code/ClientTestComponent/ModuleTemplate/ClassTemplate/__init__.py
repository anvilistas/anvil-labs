# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil

from ._anvil_designer import ClassTemplateTemplate
from .MethodTemplate import MethodTemplate
from ....UnitTestTemplate import UnitTestTemplate

__version__ = "0.0.1"


class ClassTemplate(ClassTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.success = True
        self.rp_panels = anvil.RepeatingPanel(item_template=MethodTemplate)
        self.rp_panels.items = self.item["children"]
        
        self.test_obj = UnitTestTemplate(
            cp_role=self.item["card_role"],
            btn_role=self.item['btn_role'],
            btn_text=self.item["name"],
            test_desc=self.item["ref"].__doc__,
            icon_size=self.item["icon_size"],
            btn_run_function=self.btn_run_click,
            rp_panels=self.rp_panels
        )

        self.add_component(self.test_obj)
        self.add_event_handler('x-run', self.btn_run_click)

    def btn_run_click(self, **event_args):
        children = self.rp_panels.get_components()
        for child in children:
            child.raise_event('x-run')
            if not child.success:
                self.success = False
        print('main success ', self.success)
        self.test_obj.pass_fail_icon_change(self.success)