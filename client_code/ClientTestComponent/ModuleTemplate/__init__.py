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
        self.class_tests = UnitTestTemplate(
            cp_role=self.item["card_role"],
            btn_role=self.item['btn_role'],
            btn_text=self.item["name"],
            test_desc=self.item["ref"].__doc__,
            icon_size=self.item["icon_size"],
            btn_run_function=self.btn_run_test_click
        )

        self.rp_children = anvil.RepeatingPanel(item_template=ClassTemplate)
        self.rp_children.items = self.item["children"]
        self.add_component(self.class_tests)
        self.add_component(self.rp_children)

    def btn_run_test_click(self, **event_args):
        """This method is called when the button is clicked"""
        testclasses = self.rp_children.get_components()
        for testclass in testclasses:
            test_fp = testclass.get_components()[0].get_components()[0].get_components()[0]
            test_btn = test_fp.get_components()[0]
            test_btn.raise_event("click")
            fail_icon = test_fp.get_components()[3]
            if fail_icon.visible:
                self.class_tests.lbl_fail.visible = True
        if not self.class_tests.lbl_fail.visible:
            self.class_tests.lbl_success.visible = True
