# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from uuid import uuid4

from anvil.tables import app_tables, in_transaction, order_by

from anvil_extras.server_utils import LOGGER

from ..historic.exceptions import (
    AuthorizationError,
    DuplicationError,
    NonExistentError,
    ResurrectionError,
)

__version__ = "0.0.1"


class Authorization:
    """A class to check whether authorization exists for an operation on an object

    Attributes
    ----------
    checker : callable
        which must take a portable class instance and an operation ('create', 'change'
        or 'delete') as its arguments and return a bool.
    """

    def __init__(self, checker=None):
        self.checker = checker

    def check(self, obj, operation):
        if self.checker is None:
            return True
        return self.checker(obj, operation)


authorization = Authorization()


def _previous_event(object_id):
    """Find the most recent event record for a given object_id

    Parameters
    ----------
    object_id : str

    Returns
    -------
    app_tables.events row
    """
    result = None
    try:
        result = app_tables.events.search(
            order_by("event_id", ascending=False), object_id=object_id
        )[0]
    except IndexError:
        pass
    if result is not None and result["event_type"] == "termination":
        raise ResurrectionError(
            f"Object {object_id} was terminated at {result['occurred_at']} "
            f"(event {result['event_id']})",
        )
    return result


def _state_diff(state, previous_state):
    """A dict to show the new, changed and removed attributes between two states

    Parameters
    ----------
    state : dict
    previous_state : dict

    Returns
    -------
    dict
        with keys 'new', 'changed' and 'removed' for each of those with content
    """
    new = {k: v for k, v in state.items() if k not in previous_state}
    changed = {
        k: {"from": previous_state[k], "to": v}
        for k, v in state.items()
        if k in previous_state and v != previous_state[k]
    }
    removed = {k: v for k, v in previous_state.items() if k not in state}
    diff = {"new": new, "changed": changed, "removed": removed}
    result = {k: v for k, v in diff.items() if len(v) > 0}
    return result if len(result) > 0 else None


def _record_event(event, prevent_duplication):
    """Write a single event record to the data table

    Parameters
    ----------
    event : Event
    prevent_duplication : bool
        Whether to disallow records where the state is unchanged from previously
    """
    if event.event_type == "creation" and event.affected.uid is not None:
        raise AttributeError("Object uid cannot be assigned on creation")

    if event.event_type == "creation":
        event.affected.uid = uuid4().hex

    object_id = event.affected.uid
    state = None
    diff = None

    try:
        state = event.affected.__serialize__()
    except AttributeError:
        state = event.affected.__dict__

    previous_event = _previous_event(object_id)

    try:
        previous_event_id = previous_event["event_id"]
    except TypeError:
        previous_event_id = None

    if event.event_type == "creation" and previous_event is not None:
        raise DuplicationError(
            f"Object {object_id} already exists (event {previous_event_id})"
        )

    if event.event_type == "change" and previous_event is None:
        raise NonExistentError(
            f"Object {object_id} does not exist and so cannot be updated"
        )

    if event.event_type == "change":
        diff = _state_diff(state, previous_event["state"])
        if prevent_duplication and diff is None:
            raise DuplicationError(
                f"Object {object_id} already exists in this state "
                "(event {previous_event_id})"
            )

    sequence = app_tables.sequences.get(name="events") or app_tables.sequences.add_row(
        name="events", value=0
    )
    app_tables.events.add_row(
        event_id=sequence["value"],
        recorded_at=event.recorded_at,
        object_id=object_id,
        object_type=event.affected.__class__.__name__,
        event_type=event.event_type,
        occurred_at=event.occurred_at,
        state=state,
        predecessor=previous_event_id,
        state_diff=diff,
    )
    sequence["value"] += 1
    return object_id


@in_transaction
def save_event_records(events, prevent_duplication, return_identifiers):
    """Save event records for a batch of events

    Parameters
    ----------
    payload : list
        of Event instances
    prevent_duplication : bool
        Whether to disallow records where the state is unchanged from previously
    return_identifiers : bool

    Returns
    -------
    list
        either empty or with the uids of the saved objects depending on
        return_identifiers
    """
    result = []
    if not isinstance(events, list):
        events = [events]

    LOGGER.info(f"Saving payload of {len(events)} events")
    try:
        for event in events:
            if not authorization.check(event.affected, event.event_type):
                raise AuthorizationError(
                    f"You do not have {event.event_type} permission for this "
                    f"{event.affected.__class__.__name__} "
                    f"object (id: {event.affected.uid}])"
                )
            LOGGER.info(
                f"Attempting {event.event_type} of {event.affected.__class__.__name__} "
                f"object (id: {event.affected.uid})"
            )
            uid = _record_event(event, prevent_duplication)
            if return_identifiers:
                result.append(uid)
        LOGGER.info(f"{len(events)} Events saved")
        return result
    except Exception as e:
        LOGGER.error(
            "An error occurred whilst attempting to save these events. "
            "No changes were committed to the db."
        )
        raise e
