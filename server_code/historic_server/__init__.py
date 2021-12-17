# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import anvil.server

from .projection import play
from .persistence import save_event_records, fetch_object

__version__ = "0.0.1"


@anvil.server.callable
def save(events, prevent_duplication=True, return_identifiers=False, projectors=None):
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
    projectors = [] if projectors is None else projectors
    for projector in projectors:
        play(projector)
    return identifiers if return_identifiers else None


@anvil.server.callable
def fetch(object_id, portable_class, as_at=None):
    """Fetch an object with state at a given point in time

    Parameters
    ----------
    object_id : str
        The object identifier
    as_at : datetime.datetime
    """
    if as_at is not None:
        raise NotImplementedError

    state = fetch_object(object_id, as_at)
    return portable_class(state)
