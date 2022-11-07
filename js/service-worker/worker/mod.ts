/// <reference lib="WebWorker" />
// we'll need to request imports that we don't have
// the main app will need to register a handler for bg syncing

import { configureSkulpt, errHandler, defer, modStore } from "../../worker/utils/worker.ts";

declare global {
    interface ServiceWorkerGlobalScope {
        postMessage(data: any): void;
        raise_event(eventName: string): void;
        window: ServiceWorkerGlobalScope;
        sync_event_handler(cb: (e: any) => void): (e: any) => void;
        anvilAppOrigin: string;
        onsync: any;
        onperiodicsync: any;
    }
}

declare const self: ServiceWorkerGlobalScope;
declare const Sk: any;
declare const localforage: any;

// Skulpt expectes window to exist
self.window = self;
self.anvilAppOrigin = "";
let MODULE_LOADED = false;

async function loadInitModule(name: string) {
    MODULE_LOADED = true;
    await localVarStore.setItem("__main__", name);
    try {
        await asyncToPromise(() => importMain(name, false, true));
    } catch (e) {
        console.error(e);
        errHandler(e);
    }
}

const {
    builtin: { func: pyFunc },
    misceval: { asyncToPromise },
    importMain,
} = Sk;

configureSkulpt();
addAPI();

function addAPI() {
    // can only do this one skulpt has loaded
    function raise_event(args: any[], kws: any[] = []) {
        if (args.length !== 1) {
            throw new Sk.builtin.TypeError("Expeceted one arg to raise_event");
        }
        const objectKws: any = {};
        for (let i = 0; i < kws.length; i += 2) {
            const key = kws[i];
            const val = kws[i + 1];
            objectKws[key as string] = Sk.ffi.toJs(val);
        }
        raiseEvent(args[0].toString(), objectKws);
    }
    raise_event.co_fastcall = true;

    self.raise_event = new pyFunc(raise_event);
    self.sync_event_handler = (cb) => (e) => e.waitUntil(cb(e));
}

const localVarStore = localforage.createInstance({
    name: "anvil-labs-sw",
    storeName: "locals",
});

async function onInitModule(e: any) {
    const data = e.data;
    const { type } = data;
    if (type !== "INIT") return;
    const { name } = data;
    // we're being loaded from the client so clear our module cache
    await modStore.clear();
    await loadInitModule(name);
}

self.addEventListener("message", onInitModule);

self.addEventListener("activate", (e) => {
    console.log("%cSW ACTIVATED", "color: hotpink;");
});

async function onAppOrigin(e: any) {
    const data = e.data;
    const { type } = data;
    if (type !== "APPORIGIN") return;
    const { origin } = data;
    self.anvilAppOrigin = origin as string;
    await localVarStore.setItem("apporigin", origin);
}
self.addEventListener("message", onAppOrigin);

async function postMessage(data: { type: string; [key: string]: any }) {
    // flag for the client
    data.ANVIL_LABS = true;

    const clients = await self.clients.matchAll({
        includeUncontrolled: true,
        type: "window",
    });

    for (const c of clients) {
        c.postMessage(data);
    }
}

self.postMessage = postMessage;

function raiseEvent(name: string, kws: any = {}) {
    kws.event_name = name;
    postMessage({ type: "EVENT", name, kws });
}

function resetHandler(onwhat: string, setter: any) {
    const { get: onGet } = Object.getOwnPropertyDescriptor(self, onwhat) ?? {};
    // @ts-ignore
    delete self[onwhat];
    Object.defineProperty(self, onwhat, {
        get: onGet,
        set: setter,
        configurable: true,
    });
}

/**
 * The approach here is to set a dummy onsync event handler
 *
 * When this script wakes up from being dormant, a sync event might fire
 * (this could be the reason the service worker is waking up)
 * But the python module won't be loaded, so the python sync handler doesn't exist
 * So we use e.waitUntil with a deferred promise
 * reload the module that was called with `sw.init(modname)`
 * when the module loads onsync may get overridden by the python module
 * when it does we call the python function and resolve the deferred promise
 *
 * This is quite a bit of a hack
 * it relies on the module setting onsync rather than using self.addEventListener("sync")
 * We can document this
 * And/Or add support for addEventListner
 */
function initSyncCall(eventName: "sync" | "periodicsync") {
    const onEvent = ("on" + eventName) as "onsync" | "onperiodicsync";
    const deferred = defer();
    const { set: onSet } = Object.getOwnPropertyDescriptor(self, onEvent) ?? {};
    let initEvent: any;

    self[onEvent] = (e: any) => {
        if (MODULE_LOADED) return;
        initEvent = e;
        initModule();
        setTimeout(() => {
            deferred.resolve("timeout");
        }, 5000);
        e.waitUntil(deferred.promise);
    };

    resetHandler(onEvent, async (fn: any) => {
        resetHandler(onEvent, onSet);
        self[onEvent] = fn;
        if (!initEvent) return;
        try {
            await fn(initEvent);
            deferred.resolve(null);
        } catch (e) {
            deferred.reject(e);
        }
    });

    // convenience method to catch a sync/periodicsync in the client
    self.addEventListener(eventName, (event) => {
        raiseEvent(eventName, { tag: (event as any).tag });
    });
}

initSyncCall("sync");
initSyncCall("periodicsync");

async function initModule() {
    const appOrigin = await localVarStore.getItem("apporigin");
    self.anvilAppOrigin = appOrigin ?? "";
    if (MODULE_LOADED) return;
    const name = await localVarStore.getItem("__main__");
    if (name) await loadInitModule(name);
}

console.log("%cRUNNING SW SCRIPT", "color: green;");
