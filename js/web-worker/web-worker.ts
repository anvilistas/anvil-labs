// deno-lint-ignore-file no-explicit-any no-var
import RSVP from "./rsvp_types.d.ts";
import type { HandlerFn, CallData, ResponseData, OutData, StateData, TaskId, Handlers, KillData } from "./types.ts";

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
    postMessage(message: ResponseData | OutData | StateData): void;
    onmessage(ev: MessageEvent<CallData | KillData>): void;
    currentTask: null | { fn: string; id: TaskId };
    task_state: any;
    stateHandler: (state: any) => void;
}

export function initWorkerRPC(target: CustomWorker) {
    const {
        builtin: { BaseException: pyBaseException },
        ffi: { toJs },
    } = Sk;

    const handlers: Handlers = {};
    target.registerFn = (fnName, handler) => {
        handlers[fnName] = handler;
    };

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

    target.onmessage = async (m) => {
        const { data } = m;
        switch (data.type) {
            case "CALL": {
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
                            errorType = e.constructor ?? "<unknown>";
                            errorArgs = [e.message];
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
        }
    };
}
