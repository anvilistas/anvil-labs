# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from ._anvil_designer import Form1Template

__version__ = "0.0.1"


class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
