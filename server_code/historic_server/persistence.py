# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from uuid import UUID, uuid4

import anvil.users
from anvil.server import ServiceNotAdded
from anvil.tables import app_tables, in_transaction, order_by

from anvil_extras import logging

from ..historic.events import Change, Creation
from ..historic.exceptions import (
    AuthorizationError,
    DuplicationError,
    InvalidUIDError,
    NonExistentError,
    ResurrectionError,
)

__version__ = "0.0.1"

LOGGER = logging.Logger("anvil_labs.historic.persistence")


def _default_identifier():
    try:
        user = anvil.users.get_user()["email"]
    except (TypeError, ServiceNotAdded):
        user = None
    return user


class _Authorization:
    """A class to check whether authorization exists for an operation on an object

    Attributes
    ----------
    policy: callable
        which must take an event instance as its argument and return a bool.
    identifier : callable
        which must return a string.
    """

    def __init__(self):
        self.policy = None
        self.identifier = None

    def check(self, event):
        if self.policy is None:
            return True
        return self.policy(event)

    def user_id(self):
        if self.identifier is None:
            self.identifier = _default_identifier
        return self.identifier()


authorization = _Authorization()


def _is_valid_uid(uid):
    try:
        UUID(uid, version=4)
        return True
    except ValueError:
        return False


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


def _record_event(event, record_duplicates, user_id):
    """Write a single event record to the data table

    Parameters
    ----------
    event : Event
    prevent_duplication : bool
        Whether to disallow records where the state is unchanged from previously
    """
    if isinstance(event, Creation):
        if event.affected.uid is None:
            event.affected.uid = str(uuid4())
        elif not _is_valid_uid(event.affected.uid):
            raise InvalidUIDError(f"Invalid UID {event.affected.uid}")

    object_id = event.affected.uid
    state = None
    diff = None

    try:
        state = event.affected.__persist__()
    except AttributeError:
        state = event.affected.__dict__

    previous_event = _previous_event(object_id)

    try:
        previous_event_id = previous_event["event_id"]
    except TypeError:
        previous_event_id = None

    if isinstance(event, Creation) and previous_event is not None:
        raise DuplicationError(
            f"Object {object_id} already exists (event {previous_event_id})"
        )

    if isinstance(event, Change) and previous_event is None:
        raise NonExistentError(
            f"Object {object_id} does not exist and so cannot be updated"
        )

    if isinstance(event, Change):
        diff = _state_diff(state, previous_event["state"])
        if diff is None and not record_duplicates:
            return object_id

    sequence = app_tables.sequences.get(name="events") or app_tables.sequences.add_row(
        name="events", value=1
    )
    app_tables.events.add_row(
        event_id=sequence["value"],
        recorded_at=event.recorded_at,
        object_id=object_id,
        object_type=type(event.affected).__name__,
        event_type=type(event).__name__.lower(),
        occurred_at=event.occurred_at,
        state=state,
        predecessor=previous_event_id,
        state_diff=diff,
        user_id=user_id,
    )
    sequence["value"] += 1
    return object_id


@in_transaction
def save_event_records(events, log_level, record_duplicates, return_identifiers):
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
    LOGGER.level = log_level
    result = []
    if not isinstance(events, list):
        events = [events]

    user_id = authorization.user_id()

    LOGGER.debug(f"Saving payload of {len(events)} events")
    try:
        for event in events:
            if not authorization.check(event):
                raise AuthorizationError(
                    f"You do not have {type(event).__name__} permission for this "
                    f"{type(event.affected).__name__} "
                    f"object (id: {event.affected.uid}])"
                )
            LOGGER.debug(
                f"Attempting {type(event).__name__} of {type(event.affected).__name__} "
                f"object (id: {event.affected.uid})"
            )
            uid = _record_event(event, record_duplicates, user_id)
            if return_identifiers:
                result.append(uid)
        LOGGER.debug(f"{len(events)} Events saved")
        return result
    except Exception as e:
        LOGGER.error(
            "An error occurred whilst attempting to save these events. "
            "No changes were committed to the db."
        )
        raise e
