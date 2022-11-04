# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from anvil.js import window as _W

__version__ = "0.0.1"

REG = _W.anvilLabs.importFrom("./_/theme/anvil_labs/client_sw.js").init()
SW = REG.installing or REG.waiting or REG.active
EVENT_LISTENERS = {}

# escape hatches
registration = REG
service_worker = SW
sync_manager = REG.sync
periodic_sync_manager = REG.periodicSync


def _error_handler(err):
    print("<SERVICE WORKER STDERR>:", repr(err))
    raise err


def set_default_error_handler(fn):
    global _error_handler
    _error_handler = fn


_ProxyType = type(_W)


def _message(event):
    data = event.data
    if not isinstance(data, _ProxyType):
        return
    if "ANVIL_LABS" not in data:
        return
    type = data.type

    if type == "OUT":
        print("<SERVICE WORKER STDOUT>:", data.message, end="")

    if type == "EVENT":
        kws = data.kws
        name = data.name
        for listener in EVENT_LISTENERS.get(name, []):
            listener(**kws)


_W.navigator.serviceWorker.addEventListener("message", _message)

# custom api
def subscribe(event, listener):
    EVENT_LISTENERS.setdefault(event, []).append(listener)


def unsubscribe(event, listener=None):
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
    if not modname.startswith(_W.anvilAppMainPackage):
        modname = _W.anvilAppMainPackage + "." + modname
    SW.postMessage({"type": "INIT", "name": modname})


def _camel(s):
    init, *rest = s.split("_")
    return init + "".join(map(str.title, rest))


def register_sync(tag, **options):
    """Registers a background sync when the app comes back online - may fail in some browsers"""
    if sync_manager.getTags(tag):
        return
    options = {_camel(k): v for k, v in options.items()}
    sync_manager.register(tag, options)


def register_periodic_sync(tag, *, min_interval=None, **options):
    """Registers a periodic sync request with the browser with the specified tag and options"""
    if periodic_sync_manager.getTags(tag):
        return
    options["min_interval"] = min_interval
    options = {_camel(k): v for k, v in options.items()}
    periodic_sync_manager.register(tag, options)
