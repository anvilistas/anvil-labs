/// <reference lib="dom" />
import { getModule } from "../../worker/utils/client.ts";

let reg: ServiceWorkerRegistration;
declare const Sk: any;

const {
    builtin: { ExternalError },
    misceval: { callsimArray: pyCall, callsimOrSuspendArray: pyCallOrSuspend },
    ffi: { toPy },
} = Sk;

async function onImport(e: any) {
    const { data } = e;
    if (!data.ANVIL_LABS) return;
    if (data.type !== "IMPORT") return;
    const { filename, id } = data;

    const content = await getModule(filename);
    reg.active?.postMessage({ type: "MODULE", content, id });
}

function reconstructError(type: string, args: any[], tb: any) {
    let reconstructed;
    try {
        const pyError = Sk.builtin[type];
        reconstructed = pyCall(
            pyError,
            args.map((x) => toPy(x))
        );
        reconstructed.traceback = tb ?? [];
    } catch {
        let jsError;
        try {
            // @ts-ignore
            jsError = new window[type](...args);
        } catch {
            jsError = new Error(...args);
        }
        reconstructed = new ExternalError(jsError);
    }
    return reconstructed;
}

function onError(e: any) {
    const { data } = e;
    if (!data.ANVIL_LABS) return;
    if (data.type !== "ERROR") return;
    const { errorType, errorArgs, errorTb } = data;
    const error = reconstructError(errorType, errorArgs, errorTb);
    // a bit of a hack
    const mod = Sk.sysmodules.quick$lookup(toPy("anvil_labs.service_worker"));
    if (!mod) {
        throw error;
    }
    const errorHandler = mod.$d._error_handler;
    pyCallOrSuspend(errorHandler, [error]);
}

export async function init() {
    reg = await navigator.serviceWorker.register("_/theme/anvil_labs/sw.js");
    try {
        await reg.update();
    } catch {
        // we might be offline
    }

    navigator.serviceWorker.addEventListener("message", onImport);
    navigator.serviceWorker.addEventListener("message", onError);

    return reg;
}

export default init;
