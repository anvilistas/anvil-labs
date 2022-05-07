// deno-lint-ignore-file no-explicit-any
import RSVP from "./rsvp_types.d.ts";

export type TaskId = string;
export type OutstandingCalls = { [callId: TaskId]: RSVP.Deferred<any> };
export type HandlerFn = (args: any[], kws: { [key: string]: any }) => Promise<any>;
export type Handlers = { [handler: string]: HandlerFn };

export interface ResponseData {
    type: "RESPONSE";
    id: TaskId;
    value?: any;
    errorType?: string;
    errorArgs?: any[];
    errorTb?: any[];
}

export interface OutData {
    type: "OUT";
    message: string;
}

export interface KillData {
    type: "KILL";
    id: TaskId;
}

export interface StateData {
    type: "STATE";
    state: any;
}

export interface CallData {
    type: "CALL";
    id: TaskId;
    fn: string;
    args: any[];
    kws: { [key: string]: any };
}
