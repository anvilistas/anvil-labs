# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .. import client_unittest
from ..UnitTestComponent import UnitTestComponent
from ._anvil_designer import Form1Template

__version__ = "0.0.1"


class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.add_component(
            UnitTestComponent(
                test_modules=[client_unittest],
                card_roles=[None, None, None],
                icon_size=30,
                btn_role=None,
                title_role=None,
            )
        )
