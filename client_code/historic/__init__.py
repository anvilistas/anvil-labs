# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import anvil.server

from .logging import LOGGER

__version__ = "0.0.1"


def create(obj, projectors=None):
    """Save a new object and optionally play all projections

    Parameters
    ----------
    obj : portable class instance
    projectors : list
        of projector names to play

    Returns
    -------
    str
        The uid of the object
    """
    return anvil.server.call(
        "anvil_labs.historic.create",
        obj=obj,
        log_level=LOGGER.level,
        projectors=projectors,
    )


def update(obj, projectors=None):
    """Save changes to an object and optionally play all projections

    Parameters
    ----------
    obj : portable class instance
    projectors : list
        of projector names to play

    Returns
    -------
    str
        The uid of the object
    """
    return anvil.server.call(
        "anvil_labs.historic.update",
        obj=obj,
        log_level=LOGGER.level,
        projectors=projectors,
    )


def delete(obj, projectors=None):
    """Delete an object and optionally play all projections

    Parameters
    ----------
    obj : portable class instance
    projectors : list
        of projector names to play
    """
    anvil.server.call(
        "anvil_labs.historic.delete",
        obj=obj,
        log_level=LOGGER.level,
        projectors=projectors,
    )
