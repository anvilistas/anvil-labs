// deno-lint-ignore-file no-explicit-any no-var
import RSVP from "./rsvp_types.d.ts";
import type { HandlerFn, CallData, ResponseData, OutData, StateData, TaskId, Handlers, KillData } from "./types.ts";

declare global {
    interface Window {
        anvilAppMainPackage: string;
        anvilCDNOrigin: string;
        RSVP: typeof RSVP;
    }
}

declare var stopExecution: boolean;
export interface CustomWorker extends Worker {
    registerFn(fnName: string, handler: HandlerFn): void;
    postMessage(message: ResponseData | OutData | StateData): void;
    onmessage(ev: MessageEvent<CallData | KillData>): void;
    currentTask: null | TaskId;
    task_state: any;
    stateHandler: (state: any) => void;
}

export function initWorkerRPC(target: CustomWorker) {
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
                console.debug(`RPC call ${data.id}:`, data.fn, data.args);
                const handler = handlers[data.fn];
                let value, error;
                if (!handler) {
                    error = `No handler registered for '${data.fn}'`;
                } else {
                    try {
                        value = await handler(...data.args);
                    } catch (e) {
                        error = e.toString();
                    }
                }
                try {
                    stopExecution = false;
                    target.postMessage({
                        type: "RESPONSE",
                        id: data.id,
                        value,
                        error,
                    });
                } catch (e) {
                    console.error(e, "Failed to post RPC response:", value, error);
                }
                break;
            }
            case "KILL":
                if (!stopExecution) stopExecution = true;
                break;
        }
    };
}
