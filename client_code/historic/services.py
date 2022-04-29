# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from anvil_labs import non_blocking
from anvil_labs.atomic import action, atom, reaction, selector

__version__ = "0.0.1"
_DEFAULT_PROJECTORS = ("current", )


@atom
class Archivist:
    def __init__(self, publisher, projectors=None, deferral=2):
        """A class to sending events to the server for persistence.

        Parameters
        ----------
        publisher : anvil_extras.messaging.Publisher
        projectors : list
            of projector names to run after events have been saved
        deferral : int
            number of seconds to wait before retrying if a save is already in progress
        """
        self.projectors = projectors or _DEFAULT_PROJECTORS
        self.deferral = deferral
        self.saving = []
        self.pending = []
        self.failed = []
        publisher.subscribe(
            channel="event", subscriber=self, handler=self._handle_message
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
        if message.title == "historic.event.occurred":
            self.pending.append(message.content)

        if message.title == "historic.events.occurred":
            self.pending.extend(message.content)

    def _handle_result(self, result):
        """A handler for the result of an async server call

        Parameters
        ----------
        result : object
        """
        self.saving = []

    @action
    def _handle_error(self, err):
        """A handler for errors during an async server call

        Parameters
        ----------
        err : Exception
        """
        print(f"Error in server call: {err}")
        self.failed.extend(self.saving)
        self.saving = []

    def _do_update(self):
        """Make an async call to the server to save any pending changes"""
        unsaved = self.pending
        if not unsaved:
            return
        self.saving, self.pending = unsaved, []
        async_call = non_blocking.call_async(
            "anvil_labs.historic.save_events", unsaved, projectors=self.projectors
        )
        async_call.on_result(self._handle_result)
        async_call.on_error(self._handle_error)

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
