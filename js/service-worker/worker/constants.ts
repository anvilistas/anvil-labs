import { Deferred } from "../../worker/types.ts";
import { defer } from "../../worker/utils/worker.ts";

export let MODULE_LOADING: null | Deferred<boolean> = null;

export function setModuleLoading() {
    MODULE_LOADING ??= defer();
}
