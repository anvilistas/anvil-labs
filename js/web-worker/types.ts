// deno-lint-ignore-file no-explicit-any
import RSVP from "./rsvp_types.d.ts";

export type TaskId = string;
export type OutstandingCalls = { [callId: TaskId]: RSVP.Deferred<any> };
export type HandlerFn = (...args: any[]) => Promise<any>;
export type Handlers = { [handler: string]: HandlerFn };

export interface ResponseData {
    type: "RESPONSE";
    id: TaskId;
    value?: any;
    error?: string;
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
}
