/// <reference lib="WebWorker" />
// we'll need to request imports that we don't have
// the main app will need to register a handler for bg syncing

import { configureSkulpt, SKULPT_LOADED } from "../../worker/utils/worker.ts";

declare const self: ServiceWorkerGlobalScope;
declare const Sk: any;

// Skulpt expectes window to exist
self.window = self;

declare global {
    interface ServiceWorkerGlobalScope {
        postMessage(data: any): void;
        raise_event(eventName: string): void;
        window: ServiceWorkerGlobalScope;
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
        raiseEvent(args[0].toString(), kws);
    }
    raise_event.co_fastcall = true;
    self.raise_event = new Sk.builtin.func(raise_event);
}

self.onmessage = async (e) => {
    const data = e.data;
    const { type } = data;
    switch (type) {
        case "SKULPT": {
            // This is very hacky - do it so that we can use browser cache
            // we could use importScripts - but we need to do importScripts on load
            // and before then we don't necessarily know the location of the skulpt file
            const skMod = await fetch(data.url);
            eval(await skMod.text());
            configureSkulpt();
            addAPI();
            break;
        }
        case "INIT": {
            await SKULPT_LOADED.promise;
            const { name } = data;
            Sk.misceval.asyncToPromise(() => Sk.importMain(name, false, true));
            break;
        }
    }
};

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
