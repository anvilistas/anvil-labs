# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import partial

from anvil.tables import app_tables

from ..projection import Projector, register

__version__ = "0.0.1"
projection_name = "current"
table = getattr(app_tables, projection_name)


def _reset():
    for row in table.search():
        row.delete()


def _play(observation):
    row = table.get(object_id=observation["object_id"]) or table.add_row(
        object_id=observation["object_id"], object_type=observation["object_type"]
    )
    if observation["event"] == "termination":
        row.delete()
    else:
        row.update(state=observation["state"])


def _rewind(observation):
    row = table.get(object_id=observation["object_id"]) or table.add_row(
        object_id=observation["object_id"], object_type=observation["object_type"]
    )
    if observation["event"] == "creation":
        row.delete()
    else:
        row.update(state=observation["previous_state"])


def _spool(observations, action):
    for observation in observations:
        actions = {"play": _play, "rewind": _rewind}
        actions[action](observation)


@register(projection_name)
def projector():
    return Projector(
        name=projection_name,
        player=partial(_spool, action="play"),
        rewinder=partial(_spool, action="rewind"),
        resetter=_reset,
    )
