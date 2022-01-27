# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
"""A projector to maintain a data table with single 'current' record for each object.

The current record would normally show the state of the most recent event, but
can be rewound to a previous point.

The target table should be named 'current' and contain the following colums:

    object_type : text
    object_id : text
    state : simple object
"""
from functools import partial

from anvil.tables import app_tables

from ..projection import Projector, register

__version__ = "0.0.1"
projection_name = "current"
table = getattr(app_tables, projection_name, None)


def _reset():
    """Reset the projection by emptying the target table"""
    for row in table.search():
        row.delete()


def _play(event):
    """Update the target record with the current state

    Termination events will cause the target record to be deleted.
    """
    row = table.get(object_id=event["object_id"]) or table.add_row(
        object_id=event["object_id"], object_type=event["object_type"]
    )
    if event["event_type"] == "termination":
        row.delete()
    else:
        row.update(state=event["state"])


def _rewind(event):
    """Update the target record with the previous state

    Creation events will cause the target record to be deleted.
    """
    row = table.get(object_id=event["object_id"]) or table.add_row(
        object_id=event["object_id"], object_type=event["object_type"]
    )
    if event["event_type"] == "creation":
        row.delete()
    else:
        previous = app_tables.events.get(event_id=event["predecessor"])
        row.update(state=previous["state"])


def _spool(events, action):
    """Call either _play or _rewind depending on the action specified

    Parameters
    ----------
    events : SearchIterator over app_tables.events
    action : str
        either 'play' or 'rewind'
    """
    for event in events:
        actions = {"play": _play, "rewind": _rewind}
        actions[action](event)


@register(projection_name)
def projector():
    """Factory function to create an instance of the 'current' projector"""
    return Projector(
        name=projection_name,
        player=partial(_spool, action="play"),
        rewinder=partial(_spool, action="rewind"),
        resetter=_reset,
    )
