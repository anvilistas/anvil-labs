# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from anvil_extras import logging

from anvil_labs import non_blocking
from anvil_labs.atomic import action, atom, reaction, selector

from .logging import LOGGER

__version__ = "0.0.1"

_DEFAULT_PROJECTORS = ("current",)
_DEFAULT_CHANNEL = "event"
_DEFAULT_MESSAGE_TITLES = {
    "single": "historic.event.occurred",
    "multiple": "historic.events.occurred",
}
LOGGER = logging.Logger("historic.archivist")


@atom
class Archivist:
    def __init__(
        self,
        publisher,
        projectors=_DEFAULT_PROJECTORS,
        deferral=2,
        channel=_DEFAULT_CHANNEL,
        message_titles=None,
        post_result_handler=None,
        post_error_handler=None,
    ):
        """A class to handle sending events to the server in response to published
        messages.

        Parameters
        ----------
        publisher : anvil_extras.messaging.Publisher
        projectors : list
            of projector names to run after events have been saved
        deferral : int
            number of seconds to wait before retrying if a save is already in progress
        channel : str
            the channel to listen for messages on
        message_titles : dict
            mapping keys "single" and "multiple" to the titles of messages to listen for
        post_result_handler : callable
            called with the result of the save_events call
        post_error_handler : callable
            called with any error from the save_events call
        """
        self.projectors = projectors
        self.deferral = deferral
        self.message_titles = message_titles or _DEFAULT_MESSAGE_TITLES
        self.post_result_handler = post_result_handler
        self.post_error_handler = post_error_handler
        self.saving = []
        self.pending = []
        self.failed = []
        publisher.subscribe(
            channel=channel, subscriber=self, handler=self._handle_message
        )
        reaction(lambda: self.pending, self._update_db)
        self.deferred_save = None

    @property
    @selector
    def status(self):
        pending, saving, failed = self.pending, self.saving, self.failed
        if failed:
            return "unsaved"
        if pending or saving:
            return "saving"
        return "saved"

    def _handle_message(self, message):
        if message.title == self.message_titles["single"]:
            self.pending.append(message.content)

        if message.title == self.message_titles["multiple"]:
            self.pending.extend(message.content)

    def _handle_result(self, result):
        self.saving = []
        if self.post_result_handler:
            self.post_result_handler(result)

    @action
    def _default_error_handler(self, err):
        LOGGER.error(f"Error in server call: {err}")
        self.failed.extend(self.saving)
        self.saving = []
        if self.post_error_handler:
            self.post_error_handler(err)

    def _do_update(self):
        """Make an async call to the server to save any pending changes"""
        unsaved = self.pending
        if not unsaved:
            return
        self.saving, self.pending = unsaved, []
        async_call = non_blocking.call_async(
            "anvil_labs.historic.save_events",
            unsaved,
            LOGGER.level,
            projectors=self.projectors,
        )
        async_call.on_result(self.result_handler)
        async_call.on_error(self.error_handler)

    @action
    def _update_db(self, pending):
        """An action to call _do_update if there are unsaved changes

        Parameters
        ----------
        unsaved : List
        """
        if not pending:
            return
        non_blocking.cancel(self.deferred_save)
        if self.saving:
            self.deferred_save = non_blocking.defer(self._do_update, self.deferral)
        else:
            self._do_update()
