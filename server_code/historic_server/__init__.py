# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import anvil.server
from anvil.tables import app_tables

from ..historic.exceptions import UnregisteredClassError
from ..historic.model import Event
from .persistence import save_event_records
from .projection import play

__version__ = "0.0.1"
_classes = {}


def register(cls, name):
    _classes[name] = cls


def play_projectors(projectors):
    if projectors is None:
        return
    for projector in projectors:
        play(projector)


@anvil.server.callable
def save_events(
    events, prevent_duplication=True, return_identifiers=False, projectors=None
):
    """Save event records and optionally play all projections

    events : list
        of Event instances
    prevent_duplication : bool
        Whether to disallow records where the state is unchanged from previously
    return_identifiers : bool
    projectors : list
        of projector names to play

    Returns
    -------
    None or list
        Depending on the value of return_identifiers
    """
    identifiers = save_event_records(events, prevent_duplication, return_identifiers)
    play_projectors(projectors)
    return identifiers if return_identifiers else None


@anvil.server.callable
def save(obj, projectors=None):
    event_type = "creation" if obj.uid is None else "change"
    return_identifiers = True if event_type == "change" else False
    event = Event(event_type, obj)
    identifier = save_event_records(event, return_identifiers=return_identifiers)[0]
    play_projectors(projectors)
    return identifier


@anvil.server.callable
def delete(obj, projectors=None):
    event = Event("termination", obj)
    save_event_records(event, return_identifiers=return_identifiers)[0]
    play_projectors(projectors)


@anvil.server.callable
def fetch(object_id, as_at=None):
    """Fetch an object with state at a given point in time

    Parameters
    ----------
    object_id : str
        The object identifier
    as_at : datetime.datetime
    """
    if as_at is None:
        record = app_tables.current.get(object_id=object_id)
    else:
        raise NotImplementedError

    try:
        cls = _classes[record["object_type"]]
    except KeyError:
        raise UnregisteredClassError(
            f"No {record['object_type']} portable class has been registered."
        )

    try:
        return cls.__restore__(record["state"])
    except AttributeError:
        return cls(**record["state"])
