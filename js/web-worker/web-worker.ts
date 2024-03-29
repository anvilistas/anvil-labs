// deno-lint-ignore-file no-explicit-any no-var
import RSVP from "./rsvp_types.d.ts";
import type {
    HandlerFn,
    CallData,
    ResponseData,
    OutData,
    StateData,
    ID,
    Handlers,
    KillData,
    Deferred,
    ImportData,
    ModuleData,
} from "./types.ts";

declare var Sk: any;
declare var stopExecution: boolean;

declare global {
    interface Window {
        anvilAppMainPackage: string;
        anvilCDNOrigin: string;
        RSVP: typeof RSVP;
    }
}

export interface CustomWorker extends Worker {
    registerFn(fnName: string, handler: HandlerFn): void;
    postMessage(message: ResponseData | OutData | StateData | ImportData): void;
    onmessage(ev: MessageEvent<CallData | KillData | ModuleData>): void;
    currentTask: null | { fn: string; id: ID };
    task_state: any;
    stateHandler: (state: any) => void;
    moduleLoaded: Deferred<any>;
    fetchModule(filename: string): Promise<string>;
}

export function initWorkerRPC(target: CustomWorker) {
    const {
        builtin: { BaseException: pyBaseException },
        ffi: { toJs },
    } = Sk;

    // repeat this function here since we string this function
    // TODO since we can now use scripts in dependencies we could probably handle this behaviour better
    function defer<T = any>() {
        const deferred = { resolve: () => {}, reject: () => {} } as Partial<Deferred<T>>;
        deferred.promise = new Promise<T>((resolve, reject) => {
            deferred.resolve = resolve;
            deferred.reject = reject;
        });
        return deferred as Deferred<T>;
    }

    const handlers: Handlers = {};
    target.registerFn = (fnName, handler) => {
        handlers[fnName] = handler;
    };

    target.moduleLoaded = defer();

    function newState() {
        target.task_state = new Proxy({} as any, {
            set(t, k, v) {
                const current = t[k];
                if (current === v) {
                    return true;
                }

                t[k] = v;

                target.postMessage({
                    type: "STATE",
                    state: { ...t },
                });
                return true;
            },
        });
    }

    const unresolvedModules: Map<string, Deferred<string | null>> = new Map();

    target.fetchModule = (filename: string) => {
        const id = Math.random().toString(36).substring(6);
        target.postMessage({ type: "IMPORT", id, filename });
        const deferred = defer();
        unresolvedModules.set(id, deferred)
        return deferred.promise;
    }

    target.onmessage = async (m) => {
        const { data } = m;
        switch (data.type) {
            case "CALL": {
                await target.moduleLoaded.promise;
                newState();
                const { id, fn, args, kws } = data;
                console.debug(`RPC call ${id}:`, fn, args);
                const handler = handlers[fn];
                let value, errorType, errorArgs, errorTb;
                target.currentTask = { id, fn };
                if (!handler) {
                    errorType = "RuntimeError";
                    errorArgs = [`No handler registered for '${data.fn}'`];
                } else {
                    try {
                        value = await handler(args, kws);
                    } catch (e) {
                        if (e instanceof pyBaseException) {
                            errorArgs = toJs(e.args);
                            errorType = e.tp$name;
                            errorTb = e.traceback;
                        } else {
                            errorType = e.constructor?.name ?? "<unknown>";
                            errorArgs = e.message ? [e.message] : [];
                        }
                    }
                }
                target.currentTask = null;
                try {
                    stopExecution = false;
                    target.postMessage({
                        type: "RESPONSE",
                        id: data.id,
                        value,
                        errorType,
                        errorArgs,
                        errorTb,
                    });
                } catch (e) {
                    console.error(e, "Failed to post RPC response:", value, e);
                }
                break;
            }
            case "KILL":
                if (!stopExecution) stopExecution = true;
                break;

            case "MODULE": {
                const {id, content} = data;
                const { resolve } = unresolvedModules.get(id)!;
                unresolvedModules.delete(id);
                resolve(content);
            }
        }
    };
}
