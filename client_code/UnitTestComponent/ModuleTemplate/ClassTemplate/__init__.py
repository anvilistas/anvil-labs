# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

# SPDX-License-Identifier: MIT
#
# Copyright (c) 2021 The Anvil Extras project team members listed at
# https://github.com/anvilistas/anvil-extras/graphs/contributors
#
# This software is published at https://github.com/anvilistas/anvil-extras

import anvil

from ._anvil_designer import ClassTemplateTemplate
from .TestTemplate import TestTemplate

__version__ = "0.0.1"


class ClassTemplate(ClassTemplateTemplate):
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

        self.rp_methods = anvil.RepeatingPanel(item_template=TestTemplate)
        self.rp_methods.items = self.item["children"]
        self.cp_module.add_component(self.rp_methods)

        self.btn_run.set_event_handler("click", self.btn_run_test_click)

    def btn_run_test_click(self, **event_args):
        """This method is called when the button is clicked"""
        testmethods = self.rp_methods.get_components()
        for test in testmethods:
            test_cp = test.get_components()[0]
            test_fp = test_cp.get_components()[0]
            test_btn = test_fp.get_components()[0]
            try:
                test_btn.raise_event("click")
            except Exception:
                fail_icon = test_fp.get_components()[3]
                fail_icon.visible = True
                self.lbl_fail.visible = True
        if not self.lbl_fail.visible:
            self.lbl_success.visible = True
