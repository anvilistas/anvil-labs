# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from anvil.js import window
from anvil.js.window import navigator

SW, REG = window.anvilLabs.importFrom("./_/theme/anvil_labs/client_sw.js").init()
EVENT_LISTENERS = {}

# escape haches
service_worker = SW
registration = REG

_Proxy = type(window)


def _message(event):
    data = event.data
    if not isinstance(data, _Proxy):
        return
    if "ANVIL_LABS" not in data:
        return
    type = data.type

    if type == "OUT":
        print("<SERVICE WORKER>:", data.message)

    if type == "EVENT":
        kws = data.kws
        name = data.name
        for listener in EVENT_LISTENERS.get(name, []):
            listener(**kws)


navigator.serviceWorker.addEventListener("message", _message)

# custom api
def add_listener(event, listener):
    EVENT_LISTENERS.setdefault(event, []).append(listener)


def remove_listener(event, listener=None):
    if not isinstance(event, str):
        raise TypeError(f"event should be a str, got {type(event).__name__}")
    if listener is None:
        EVENT_LISTENERS.pop(event, None)
        return
    if not callable(listener):
        raise TypeError("the event listener is not a callable")

    listeners = EVENT_LISTENERS.get(event, [])
    new_listeners = [h for h in listeners if h != listener]

    if len(new_listeners) == len(listeners):
        raise ValueError(f"Could not find event listener for event {event!r}")

    EVENT_LISTENERS[event] = new_listeners


def init(modname):
    if not modname.startswith(window.anvilAppMainPackage):
        modname = window.anvilAppMainPackage + "." + modname
    SW.postMessage({"type": "INIT", "name": modname})


def register_sync(tag):
    """Call this function"""
    REG.sync.register(tag)
