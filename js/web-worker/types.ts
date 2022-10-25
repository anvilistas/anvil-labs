// deno-lint-ignore-file no-explicit-any

export type ID = string;
export type OutstandingCalls = { [callId: ID]: Deferred<any> };
export type HandlerFn = (args: any[], kws: { [key: string]: any }) => Promise<any>;
export type Handlers = { [handler: string]: HandlerFn };

export type Deferred<T> = {
    promise: Promise<T>;
    resolve: (value: T | PromiseLike<T>) => void;
    reject: (reason?: any) => void;
};

export interface ResponseData {
    type: "RESPONSE";
    id: ID;
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
    id: ID;
}

export interface StateData {
    type: "STATE";
    state: any;
}

export interface ImportData {
    type: "IMPORT";
    id: ID;
    filename: string;
}

export interface ModuleData {
    type: "MODULE";
    id: ID;
    content: string | null;
}

export interface CallData {
    type: "CALL";
    id: ID;
    fn: string;
    args: any[];
    kws: { [key: string]: any };
}
