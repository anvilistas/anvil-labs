/// <reference lib="WebWorker" />

import { Deferred } from "../../worker/types.ts";
import { defer } from "../../worker/utils/worker.ts";
import { MODULE_LOADING } from "./constants.ts";

interface OnSyncCallback {
    (): void | Promise<void>;
}

export interface DeferredSync extends Deferred<null> {
    $handled?: boolean;
}

const supportsSync = "sync" in self.registration;

const log = (...args: any[]) => {
    // console.log("%cBACKGROUND SYNC", "color: hotpink;", ...args);
};

export class BackgroundSync {
    static _initSyncs = new Map<string, [SyncEvent, Deferred<null>]>();
    static _instances = new Map<string, BackgroundSync>();

    _requestsAddedDuringSync = false;
    _syncInProgress = false;
    _fallbackRegistered = false;

    constructor(readonly tag: string, readonly onSync: OnSyncCallback) {
        BackgroundSync._instances.set(tag, this);
        this._addSyncListener();
        const initSync = BackgroundSync._initSyncs.get(this.tag);
        if (initSync) {
            this._syncListener(...initSync);
        }
        if (!supportsSync) {
            this._registerFallback();
        }
        // if any active syncs from restarting then call onSync with the event
    }

    _registerFallback() {
        if (this._fallbackRegistered) return;
        this._fallbackRegistered = true;
        self.addEventListener("online", () => {
            this.onSync();
        })
    }

    async _fallbackSync() {
        if (self.navigator.onLine) {
            this.onSync();
        }
    }

    async registerSync(): Promise<void> {
        if (!supportsSync) {
            log("BG SYNC not supported calling early");
            return this._fallbackSync();
        }
        // See https://github.com/GoogleChrome/workbox/issues/2393
        try {
            log("registering sync with tag", this.tag);
            await self.registration.sync.register(this.tag);
        } catch (err) {
            if (err.message.startsWith("Permission denied")) {
                // we're probably on Brave or similar
                this._registerFallback();
                this._fallbackSync();
            } else {
                throw err;
            }
        }
    }

    // use deferred here because we might be a sync event from starting up
    // at which point e.waitUntil is already called
    async _syncListener(event: SyncEvent, deferred: DeferredSync) {
        log("sync listener", event);
        this._syncInProgress = true;
        deferred.$handled = true;
        BackgroundSync._initSyncs.delete(this.tag);
        await MODULE_LOADING?.promise;

        let syncError;
        try {
            await this.onSync();
        } catch (error) {
            if (error instanceof Error) {
                syncError = error;

                // Rethrow the error. Note: the logic in the finally clause
                // will run before this gets rethrown.
                deferred.reject(syncError);
                // throw syncError;
            }
        } finally {
            // New items may have been added to the queue during the sync,
            // so we need to register for a new sync if that's happened...
            // Unless there was an error during the sync, in which
            // case the browser will automatically retry later, as long
            // as `event.lastChance` is not true.
            if (this._requestsAddedDuringSync && !(syncError && !event.lastChance)) {
                await this.registerSync();
            }

            this._syncInProgress = false;
            this._requestsAddedDuringSync = false;
            deferred.resolve(null);
        }
    }

    _addSyncListener() {
        if (!supportsSync) {
            // If the browser doesn't support background sync
            // retry every time the service worker starts up as a fallback.
            return this._fallbackSync();
        }

        self.addEventListener("sync", (event: SyncEvent) => {
            log("sync event handler called", event);
            if (event.tag === this.tag) {
                log("sync listener fired", event);
                const deferred = defer();
                this._syncListener(event, deferred);
                event.waitUntil(deferred.promise);
            }
        });
        log("SYNC LISTENER ADDED");
    }

    static async register(name: string) {
        log("registering sync", name);
        await MODULE_LOADING?.promise;
        const instance = this._instances.get(name);
        if (!instance) {
            throw new Error("No Background sync with this name has been created");
        }
        instance.registerSync();
        log("sync registered for", instance.tag);
    }
}
