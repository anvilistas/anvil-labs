# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import unittest

import anvil

from ._anvil_designer import ClientTestComponentTemplate
from .ModuleTemplate import ModuleTemplate
from ..UnitTestTemplate import UnitTestTemplate

__version__ = "0.0.1"


class ClientTestComponent(ClientTestComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        if not self.card_roles:
            self.card_roles = [None, None, None]

        if not self.test_modules:
            self.test_modules = []

        self.test_config = []
        mod_cnt = 0
        for module_ref in self.test_modules:
            classlist = self.get_test_classes(module_ref)
            self.test_config.append(
                {
                    "name": "Module: " + getattr(module_ref, "__name__").split(".")[-1],
                    "ref": module_ref,
                    "children": [],
                    "card_role": self.card_roles[0],
                    "btn_role": self.btn_role,
                    "icon_size": self.icon_size,
                }
            )

            for testclass in classlist:
                testclass_ref = getattr(module_ref, testclass)
                methods_in_class = dir(testclass_ref)
                methods_list = [
                    {
                        "name": "Method: " + am,
                        "classref": testclass_ref,
                        "ref": getattr(testclass_ref(), am),
                        # "setUp": getattr(testclass_ref(), 'setUp'),
                        # "tearDown": getattr(testclass_ref(), 'tearDown'),
                        "card_role": self.card_roles[2],
                        "btn_role": self.btn_role,
                        "icon_size": self.icon_size,
                    }
                    for am in methods_in_class
                    if am.startswith("test_")
                ]
                self.test_config[mod_cnt]["children"].append(
                    {
                        "name": "Class: " + testclass,
                        "ref": testclass_ref,
                        "children": methods_list,
                        "card_role": self.card_roles[1],
                        "btn_role": self.btn_role,
                        "icon_size": self.icon_size,
                    }
                )

            mod_cnt += 1
            
        self.rp_panels = anvil.RepeatingPanel(item_template=ModuleTemplate)
        self.rp_panels.items = self.test_config
        
        self.test_obj = UnitTestTemplate(
            btn_role=self.btn_role,
            btn_text='Run All',
            test_desc='Run all tests',
            icon_size=self.icon_size,
            btn_run_function=self.btn_run_click,
            rp_panels=self.rp_panels
        )

        self.add_component(self.test_obj)
        self.success = True

    def get_test_classes(self, module):
        test_classes = []
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, unittest.TestCase):
                test_classes.append(attribute_name)
        return test_classes

    def btn_run_click(self, **event_args):
        children = self.rp_panels.get_components()
        for child in children:
            child.raise_event('x-run')
            if not child.success:
                self.success = False
        print('main success ', self.success)
        self.test_obj.pass_fail_icon_change(self.success)