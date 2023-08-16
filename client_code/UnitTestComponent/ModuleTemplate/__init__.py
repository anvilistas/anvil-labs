# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil

from ._anvil_designer import ModuleTemplateTemplate
from .ClassTemplate import ClassTemplate

__version__ = "0.0.1"


class ModuleTemplate(ModuleTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.cp_module = anvil.ColumnPanel(role=self.item["card_role"])
        self.fp_runs = anvil.FlowPanel(align="left")
        self.btn_run = anvil.Button(role=self.item["btn_role"], text=self.item["name"])
        self.lbl_doc = anvil.Label(text=self.item["ref"].__doc__)
        self.lbl_success = anvil.Label(
            icon="fa:check-circle",
            foreground="#4f7a28",
            visible=False,
            font_size=self.item["icon_size"],
        )
        self.lbl_fail = anvil.Label(
            icon="fa:exclamation-circle",
            foreground="#9e1e15",
            visible=False,
            font_size=self.item["icon_size"],
        )
        self.fp_runs.add_component(self.btn_run)
        self.fp_runs.add_component(self.lbl_doc)
        self.fp_runs.add_component(self.lbl_success)
        self.fp_runs.add_component(self.lbl_fail)
        self.cp_module.add_component(self.fp_runs)
        self.add_component(self.cp_module)

        self.rp_classes = anvil.RepeatingPanel(item_template=ClassTemplate)
        self.rp_classes.items = self.item["children"]
        self.cp_module.add_component(self.rp_classes)

        self.btn_run.set_event_handler("click", self.btn_run_test_click)

    def btn_run_test_click(self, **event_args):
        """This method is called when the button is clicked"""
        testclasses = self.rp_classes.get_components()
        for testclass in testclasses:
            test_cp = testclass.get_components()[0]
            test_fp = test_cp.get_components()[0]
            test_btn = test_fp.get_components()[0]
            test_btn.raise_event("click")
            fail_icon = test_fp.get_components()[3]
            if fail_icon.visible:
                self.lbl_fail.visible = True
        if not self.lbl_fail.visible:
            self.lbl_success.visible = True