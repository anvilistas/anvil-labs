/// <reference lib="WebWorker" />
// we'll need to request imports that we don't have
// the main app will need to register a handler for bg syncing
importScripts(
    "https://anvil.works/runtime-new/runtime/js/lib/skulpt.min.js",
    "https://cdn.jsdelivr.net/npm/localforage@1.10.0/dist/localforage.min.js",
    "https://cdn.jsdelivr.net/npm/uuid@8.3.2/dist/umd/uuid.min.js"
);

import { configureSkulpt, defer, errHandler } from "../../worker/utils/worker.ts";

self.window = self;

declare const self: ServiceWorkerGlobalScope;
declare const Sk: any;

const {
    builtin: {
        func: pyFunc,
        none: { none$: pyNone },
    },
    misceval: { asyncToPromise },
    ffi: { toJs },
    importMain,
} = Sk;

// Skulpt expectes window to exist

configureSkulpt();
addAPI();

declare global {
    interface ServiceWorkerGlobalScope {
        postMessage(data: any): void;
        raise_event(eventName: string): void;
        window: ServiceWorkerGlobalScope;
        sync_event_handler(cb: (e: any) => void): (e: any) => void;
    }
}

self.addEventListener("sync", (event) => {
    raiseEvent("sync", { tag: (event as any).tag });
});

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

async function onInitModule(e: any) {
    const data = e.data;
    const { type } = data;
    if (type !== "INIT") return;
    const { name } = data;
    try {
        await asyncToPromise(() => importMain(name, false, true));
    } catch (e) {
        console.error(e);
        errHandler(e);
    }
}

self.addEventListener("message", onInitModule);


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
