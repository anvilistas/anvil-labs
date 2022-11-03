// deno-lint-ignore-file no-explicit-any
import { ANVIL_FILES } from "../../dummy-modules/mod.ts";
import { Deferred } from "../types.ts";

declare const Sk: any;

export const SKULPT_LOADED = defer();

export function defer<T = any>() {
    const deferred = { resolve: () => {}, reject: () => {} } as Partial<Deferred<T>>;

    deferred.promise = new Promise<T>((resolve, reject) => {
        deferred.resolve = resolve;
        deferred.reject = reject;
    });

    return deferred as Deferred<T>;
}

export const UNRESOLVED_MODULES: Map<string, Deferred<string | null>> = new Map();

export function fetchModule(filename: string) {
    const id = crypto.randomUUID();
    self.postMessage({ type: "IMPORT", id, filename });
    const deferred = defer();
    UNRESOLVED_MODULES.set(id, deferred);
    return deferred.promise;
}

export const errHandler = (e: any) => {
    const {
        builtin: { BaseException },
        ffi: { toJs },
    } = Sk;

    let errorType, errorArgs, errorTb;
    if (e instanceof BaseException) {
        errorArgs = toJs(e.args);
        errorType = e.tp$name;
        errorTb = e.traceback;
    } else {
        errorType = e.constructor?.name ?? "<unknown>";
        errorArgs = e.message ? [e.message] : [];
    }
    self.postMessage({ type: "ERROR", errorType, errorArgs, errorTb });
};

export function configureSkulpt() {
    Sk.configure({
        output(message: string) {
            return self.postMessage({ type: "OUT", message });
        },
        yieldLimit: 300,
        syspath: ["app"],
        read(filename: string) {
            const rv = ANVIL_FILES.get(filename);
            if (rv !== undefined) return rv;
            return Sk.misceval.promiseToSuspension(
                fetchModule(filename).then((content) => {
                    if (content == null) {
                        throw "No module named " + filename;
                    }
                    return content;
                })
            );
        },
        uncaughtException: (err: any) => {
            errHandler(err);
        },
    });

    // make self available in __builtins__
    Sk.builtins.self = Sk.ffi.proxy(self);

    SKULPT_LOADED.resolve(true);
}

export function onModuleReceived(e: MessageEvent<any>) {
    const { data } = e;
    if (data.type === "MODULE") {
        const { id, content } = data;
        const deferred = UNRESOLVED_MODULES.get(id);
        if (deferred === undefined) return;
        const { resolve } = deferred;
        UNRESOLVED_MODULES.delete(id);
        resolve(content);
    }
}

self.addEventListener("message", onModuleReceived);
