# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import datetime as dt
from uuid import uuid4

import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables, in_transaction

from anvil_extras.server_utils import LOGGER

__version__ = "0.0.1"
_projectors = {}


class register:
    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        _projectors[self.name] = cls
        return cls


def play(name, play_from=None, play_to=None):
    projector = _projectors[name]
    with projector() as p:
        p.play(play_from, play_to)


def play_all(play_from=None, play_to=None):
    for name in _projectors:
        play(name, play_from, play_to)


def rewind(name, rewind_to=None):
    projector = _projectors[name]
    with projector() as p:
        p.rewind(rewind_to=rewind_to)


def rewind_all(rewind_to=None):
    for name in _projectors:
        rewind(name, rewind_to=rewind_to)


def reset(name):
    projector = _projectors[name]
    with projector() as p:
        p.reset()


def reset_all(rewind_to=None):
    for name in _projectors:
        reset(name)


def _null_player(observations):
    LOGGER.info("Playing this projector has no effect")
    LOGGER.info(f"observations: {[o['sequence'] for o in observations]}")


def _null_resestter():
    LOGGER.info("Resetting this projector has no effect")


def _null_rewinder(observations):
    LOGGER.info("Rewinding this projector has no effect")
    LOGGER.info(f"observations: {[o['observation_id'] for o in observations]}")


@in_transaction
def _projection_row(name, projector_id):
    row = app_tables.projections.get(name=name) or app_tables.projections.add_row(
        name=name, played_to=0
    )
    if row["projector"] is not None:
        LOGGER.info(
            f"The {name} projection is already being played by projector {row['projector']}"
        )
        return None
    row["projector"] = projector_id
    return row


class Projector:
    def __init__(self, name, uid=None, resetter=None, player=None, rewinder=None):
        self.name = name
        self.uid = uid or uuid4().hex
        self.resetter = resetter if callable(resetter) else _null_resestter
        self.player = player if callable(player) else _null_player
        self.rewinder = rewinder if callable(rewinder) else _null_rewinder
        self.row = None
        self.played_to = None

    def __enter__(self):
        LOGGER.info(f"Projector {self.uid} starting")
        row = _projection_row(self.name, self.uid)
        self.row = row if row is not None else None
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        LOGGER.info(f"Projector {self.uid} shutting down")
        if self.row is not None:
            self.row.update(
                last_played_at=dt.datetime.now(),
                played_to=self.played_to,
                projector=None,
            )
        self.row = None
        self.played_to = None

    def play(self, play_from=None, play_to=None, *args, **kwargs):
        if self.row is None:
            return

        _play_from = (
            play_from
            if play_from is not None
            else self.played_to
            if self.played_to is not None
            else self.row["played_to"]
        )
        observations = app_tables.observations.search(
            tables.order_by("observation_id"), observation_id=q.greater_than(_play_from)
        )
        if len(observations) == 0:
            LOGGER.info(
                f"The {self.name} projection is already at observation {_play_from}."
            )
            self.played_to = _play_from
            return

        if play_to is None:
            _play_to = app_tables.observations.search(
                tables.order_by("observation_id", ascending=False),
                observation_id=q.greater_than(_play_from),
            )[0]["observation_id"]
        else:
            _play_to = play_to
            observations = (o for o in observations if o["observation_id"] <= play_to)

        LOGGER.info(
            f"Playing the {self.name} projection from observations {_play_from} to {_play_to}"
        )
        self.player(observations, *args, **kwargs)
        self.played_to = _play_to
        LOGGER.info(
            f"The {self.name} projection has been played up to observation {_play_to}"
        )

    def rewind(self, rewind_to=None, *args, **kwargs):
        if self.row is None:
            return

        observations = app_tables.observations.search(
            tables.order_by("observation_id", ascending=False),
            observation_id=q.greater_than(rewind_to),
        )
        if len(observations) == 0:
            LOGGER.info(
                f"The {self.name} projection is already at observation {rewind_to}."
            )
            return

        LOGGER.info(f"Rewinding the {self.name} projection to observation {rewind_to}")
        self.rewinder(observations, *args, **kwargs)
        self.played_to = rewind_to
        LOGGER.info(
            f"The {self.name} projection has been rewound to observation {rewind_to}"
        )

    def reset(self, *args, **kwargs):
        if self.row is None:
            return

        LOGGER.info(f"Resetting {self.name} projection")
        self.resetter(*args, **kwargs)
        self.played_to = 0
        LOGGER.info(f"The {self.name} projection has been reset")
