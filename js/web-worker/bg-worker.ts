// deno-lint-ignore-file no-explicit-any no-var
import RSVP from "./rsvp_types.d.ts";
import type { ResponseData, OutData, StateData, CallData, TaskId, OutstandingCalls, KillData } from "./types.ts";
import { webWorkerScript } from "./make-script.ts";

declare var Sk: any;
const {
    builtin: { str: pyStr, RuntimeError, print: stdout },
} = Sk;
// declare var RSVP: any;

declare global {
    interface Window {
        anvilAppMainPackage: string;
        anvilCDNOrigin: string;
        RSVP: typeof RSVP;
    }
}

interface CustomWorker extends Worker {
    launchTask(fnName: string, ...args: any[]): [TaskId, string, Promise<any>];
    postMessage(message: CallData | KillData): void;
    onmessage(ev: MessageEvent<ResponseData | OutData | StateData>): void;
    currentTask: null | { fn: string; id: TaskId };
    stateHandler: (state: any) => void;
}

export function initWorkerRPC(target: CustomWorker) {
    const outstandingCalls: OutstandingCalls = {};
    target.currentTask = null;
    target.stateHandler = () => {};

    target.launchTask = (fn, ...args) => {
        const id = crypto.randomUUID();
        target.currentTask = { fn, id };

        target.postMessage({ type: "CALL", id, fn, args });

        outstandingCalls[id] = window.RSVP.defer();
        return [id, fn, new Promise((r) => r(outstandingCalls[id].promise))];
    };

    target.onmessage = ({ data }) => {
        switch (data.type) {
            case "OUT": {
                const { id, fn } = target.currentTask!;
                stdout([`<worker-task '${fn}' (${id})>:`, data.message], ["end", pyStr.$empty]);
                break;
            }

            case "STATE": {
                target.stateHandler({ ...data.state });
                break;
            }

            case "RESPONSE": {
                const call = outstandingCalls[data.id];
                if (!call) {
                    console.warn(`Got worker response for invalid call ${data.id}`, data);
                } else {
                    if (data.error) {
                        console.debug(`RPC error response ${data.id}:`, data.error);
                        call.reject(data.error);
                    } else {
                        console.debug(`RPC response ${data.id}:`, data.value);
                        call.resolve(data.value);
                    }
                }
                delete outstandingCalls[data.id];
                target.currentTask = null;
            }
        }
    };
}

type StateHandler = (state: any) => void;

class Task {
    _handledResult: Promise<any>;
    _startTime: number;
    _state: any = {};
    _rv: any = null;
    _err: any = null;
    _complete = false;
    _status: null | "completed" | "failed" | "killed" = null;
    _stateHandler: StateHandler = () => {};
    constructor(
        readonly _id: TaskId,
        readonly _name: string,
        readonly _result: Promise<any>,
        readonly _target: CustomWorker
    ) {
        this._startTime = Date.now();
        this._handledResult = _result;
        this._target.stateHandler = this._updateState.bind(this);
        this._result.then(
            (r) => {
                this._complete = true;
                this._status = "completed";
                this._rv = r;
            },
            (e) => {
                if (e && e.includes("RuntimeError: killed")) {
                    this._status = "killed";
                } else {
                    this._status = "failed";
                    this._complete = true;
                    this._err = e;
                }
            }
        );
    }
    _updateState(state: any) {
        this._state = state;
        this._stateHandler(state);
    }
    await_result() {
        return this._result;
    }
    on_result(resolve: any, reject: any) {
        this._handledResult = this._result.then(resolve);
        if (reject) {
            this._handledResult = this._handledResult.catch(reject);
        }
    }
    on_error(reject: any) {
        this._handledResult = this._handledResult.catch(reject);
    }
    on_state_change(handler: StateHandler) {
        this._stateHandler = handler;
    }
    get_state() {
        return this._state;
    }
    get_id() {
        return this._id;
    }
    get_task_name() {
        return this._name;
    }
    get_termination_status() {
        return this._status;
    }
    get_return_value() {
        return this._rv;
    }
    get_error() {
        if (this._err !== null) {
            throw this._err;
        }
    }
    get_start_time() {
        return this._startTime;
    }
    is_completed() {
        if (this._status === "killed") {
            throw new RuntimeError("'" + this._name + "' worker task was killed");
        }
        return this._complete;
    }
    is_running() {
        return !this._complete;
    }
    kill() {
        if (this._complete) return;
        this._target.postMessage({ type: "KILL", id: this._id });
    }
}

export class BackgroundWorker {
    target: CustomWorker;
    constructor(pyMod: string) {
        // convert pyMod to a javascript file
        // then convert to blob url
        // then use this as a web worker url
        if (!pyMod.startsWith(window.anvilAppMainPackage)) {
            pyMod = window.anvilAppMainPackage + "." + pyMod;
        }
        let mod = Sk.sysmodules.quick$lookup(new Sk.builtin.str(pyMod));
        if (!mod) {
            Sk.importModule(pyMod, false, true);
            mod = Sk.sysmodules.quick$lookup(new Sk.builtin.str(pyMod));
        }
        const jsMod = mod.$js;
        const blob = new Blob([webWorkerScript.replace("{source}", jsMod)], { type: "text/javascript" });
        this.target = new Worker(URL.createObjectURL(blob)) as CustomWorker;
        initWorkerRPC(this.target);
    }

    launch_task(fnName: string, ...args: any[]) {
        const currentTask = this.target.currentTask;
        if (currentTask !== null) {
            throw new RuntimeError("BackgroundWorker already has an active task");
        }
        const [id, name, result] = this.target.launchTask(fnName, ...args);
        return new Task(id, name, result, this.target);
    }
}
