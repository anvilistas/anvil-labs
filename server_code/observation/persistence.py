# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import datetime as dt
from enum import Enum
from uuid import uuid4

import anvil.server
from anvil.tables import app_tables, in_transaction, order_by

from anvil_extras.server_utils import LOGGER

from ..exceptions import DuplicationError, NonExistentError, ResurrectionError
from .projection import play_all

__version__ = "0.0.1"


class Event(Enum):
    creation = "creation"
    change = "change"
    termination = "termination"


def _previous_observation(object_id):
    result = None
    try:
        result = app_tables.observations.search(
            order_by("observation_id", ascending=False), object_id=object_id
        )[0]
    except IndexError:
        pass
    if result is not None and result["event"] == Event.termination.value:
        raise ResurrectionError(
            f"Object {object_id} was terminated at {result['recorded_at']} (observation {result['observation_id']})"
        )
    return result


def _state_diff(state, previous_state):
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


def _record_observation(obj, event, prevent_duplication):
    if obj.uid is None:
        obj.uid = uuid4().hex
    state = None
    diff = None

    try:
        state = obj.__serialize__()
    except AttributeError:
        state = obj.__dict__

    previous_observation = _previous_observation(obj.uid)

    try:
        previous_state = previous_observation["state"]
        previous_observation_id = previous_observation["observation_id"]
    except TypeError:
        previous_state = None
        previous_observation_id = None

    if event == Event.creation and previous_observation is not None:
        raise DuplicationError(
            f"Object {obj.uid} already exists (observation {previous_observation['observation_id']})"
        )

    if event == Event.change and previous_observation is None:
        raise NonExistentError(
            f"Object {obj.uid} does not exist and so cannot be updated"
        )

    if event == Event.change:
        diff = _state_diff(state, previous_observation["state"])
        if prevent_duplication and diff is None:
            raise DuplicationError(
                f"Object {obj.uid} already exists in this state (observation {previous_observation['observation_id']})"
            )

    sequence = app_tables.sequences.get(
        name="observation"
    ) or app_tables.sequences.add_row(name="observation", value=0)
    app_tables.observations.add_row(
        observation_id=sequence["value"],
        recorded_at=dt.datetime.now(),
        object_id=obj.uid,
        object_type=obj.__class__.__name__,
        event=event.value,
        state=state,
        previous_observation=previous_observation_id,
        previous_state=previous_state,
        state_diff=diff,
    )
    sequence["value"] += 1


@in_transaction
def _save_payload(payload, prevent_duplication):
    events = {
        "create": Event.creation,
        "update": Event.change,
        "delete": Event.termination,
    }
    if not isinstance(payload, list):
        payload = [payload]

    LOGGER.info(f"Saving payload of {len(payload)} operations")
    try:
        for item in payload:
            operation = item["operation"]
            obj = item["object"]
            LOGGER.info(
                f"Attempting to {operation} {obj.__class__.__name__} object (id: {obj.uid})"
            )
            _record_observation(
                obj, event=events[operation], prevent_duplication=prevent_duplication
            )
        LOGGER.info("Payload saved")
    except Exception as e:
        LOGGER.error(
            "An error occurred whilst attempting to save this payload. No changes were committed to the db."
        )
        raise e


@anvil.server.callable
def save(payload, prevent_duplication=True, play_projections=True):
    _save_payload(payload, prevent_duplication)
    if play_projections:
        play_all()
