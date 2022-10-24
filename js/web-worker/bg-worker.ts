// deno-lint-ignore-file no-explicit-any no-var
import type {
    ResponseData,
    OutData,
    StateData,
    CallData,
    TaskId,
    OutstandingCalls,
    KillData,
    Deferred,
} from "./types.ts";
import { webWorkerScript } from "./make-script.ts";

declare var Sk: any;

declare global {
    interface Window {
        anvilAppMainPackage: string;
        anvilCDNOrigin: string;
    }
}

export function defer<T = any>() {
    const deferred = { resolve: () => {}, reject: () => {} } as Partial<Deferred<T>>;

    deferred.promise = new Promise<T>((resolve, reject) => {
        deferred.resolve = resolve;
        deferred.reject = reject;
    });

    return deferred as Deferred<T>;
}

interface CustomWorker extends Worker {
    launchTask(fnName: string, args: any[], kws: { [key: string]: any }): [TaskId, string, Promise<any>];
    postMessage(message: CallData | KillData): void;
    onmessage(ev: MessageEvent<ResponseData | OutData | StateData>): void;
    currentTask: null | { fn: string; id: TaskId };
    stateHandler: (state: any) => void;
}

const {
    misceval: { callsimArray: pyCall, buildClass },
    ffi: { toPy },
    builtin: { RuntimeError, str: pyStr, print: stdout },
} = Sk;

export const WorkerTaskKilled = buildClass({ __name__: "anvil_labs.web_worker" }, () => {}, "WorkerTaskKilled", [
    RuntimeError,
]);

function reconstructError(type: string, args: any[], tb: any) {
    let reconstructed;
    if (type === "WorkerTaskKilled") {
        reconstructed = pyCall(WorkerTaskKilled, args);
        reconstructed.traceback = tb;
        return reconstructed;
    }
    try {
        const pyError = Sk.builtins[type];
        reconstructed = pyCall(
            pyError,
            args.map((x) => toPy(x))
        );
        reconstructed.traceback = tb ?? [];
    } catch {
        reconstructed = new Error(...args);
    }
    return reconstructed;
}

export function initWorkerRPC(target: CustomWorker) {
    const outstandingCalls: OutstandingCalls = {};
    target.currentTask = null;
    target.stateHandler = () => {};

    target.launchTask = (fn, args, kws) => {
        const id = crypto.randomUUID();
        target.currentTask = { fn, id };

        target.postMessage({ type: "CALL", id, fn, args, kws });

        outstandingCalls[id] = defer();
        return [id, fn, new Promise((r) => r(outstandingCalls[id].promise))];
    };

    target.onmessage = ({ data }) => {
        switch (data.type) {
            case "OUT": {
                const { id, fn } = target.currentTask ?? {};
                stdout([`<worker-task '${fn}' (${id})>:`, data.message], ["end", pyStr.$empty]);
                break;
            }

            case "STATE": {
                target.stateHandler({ ...data.state });
                break;
            }

            case "RESPONSE": {
                const { id, value, errorType, errorArgs, errorTb } = data;
                const call = outstandingCalls[data.id];
                if (!call) {
                    console.warn(`Got worker response for invalid call ${data.id}`, data);
                } else if (errorType) {
                    console.debug(`RPC error response ${id}:`, errorType, errorArgs);
                    call.reject(reconstructError(errorType, errorArgs!, errorTb));
                } else {
                    console.debug(`RPC response ${id}:`, value);
                    call.resolve(value);
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
                this._complete = true;
                if (e instanceof WorkerTaskKilled) {
                    this._status = "killed";
                    this._err = new RuntimeError("'" + this._name + "' worker task was killed");
                } else {
                    this._status = "failed";
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
        if (this._err) {
            throw this._err;
        }
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
        if (this._err) {
            throw this._err;
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
    constructor(pyModName: string) {
        if (!pyModName.startsWith(window.anvilAppMainPackage)) {
            pyModName = window.anvilAppMainPackage + "." + pyModName;
        }
        let mod = Sk.sysmodules.quick$lookup(new Sk.builtin.str(pyModName));
        if (!mod) {
            Sk.importModule(pyModName, false, true);
            mod = Sk.sysmodules.quick$lookup(new Sk.builtin.str(pyModName));
        }
        if (mod === undefined) {
            throw new Sk.builtin.RuntimeError("Problem importing module '" + pyModName + "'");
        }
        const blobSource = webWorkerScript
            .replace("{$filename$}", JSON.stringify(pyModName))
            .replace("{$files$}", JSON.stringify(JSON.stringify(Sk.builtinFiles)));
        const blob = new Blob([blobSource], { type: "text/javascript" });
        this.target = new Worker(URL.createObjectURL(blob)) as CustomWorker;
        initWorkerRPC(this.target);
    }

    launch_task(fnName: string, args: any[], kws: { [key: string]: any }) {
        const currentTask = this.target.currentTask;
        if (currentTask !== null) {
            throw new RuntimeError("BackgroundWorker already has an active task");
        }
        const [id, name, result] = this.target.launchTask(fnName, args, kws);
        return new Task(id, name, result, this.target);
    }
}
