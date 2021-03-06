// deno-lint-ignore-file no-explicit-any no-var
import { initWorkerRPC } from "./web-worker.ts";
import type { CustomWorker } from "./web-worker.ts";

declare var Sk: any;
declare var stopExecution: boolean;
declare var $compiledmod: (scope: any) => void;

function getSkultpUrl() {
    const scripts = document.getElementsByTagName("script");
    return Array.from(scripts).find((s) => s.src?.includes("skulpt.min.js"))!.src;
}

function workWithSkulpt() {
    Sk.configure({
        output(message: string) {
            return self.postMessage({ type: "OUT", message });
        },
        yieldLimit: 300,
    });

    const {
        builtin: { RuntimeError },
        ffi: { toJs, toPy },
        misceval: {
            tryCatch,
            chain: chainOrSuspend,
            Suspension,
            asyncToPromise: suspToPromise,
            buildClass,
            callsimArray: pyCall,
        },
    } = Sk;

    Sk.builtins.self = toPy(self);

    const WorkerTaskKilled = buildClass({ __name__: "anvil_labs.web_worker" }, () => {}, "WorkerTaskKilled", [
        RuntimeError,
    ]);

    const moduleScope: { [attr: string]: any } = {};
    $compiledmod(moduleScope);
    for (const [attr, maybeFn] of Object.entries(moduleScope)) {
        if (maybeFn.tp$call) {
            (self as unknown as CustomWorker).registerFn(attr, (args: any[], kws: { [key: string]: any }) => {
                args = args.map((x) => toPy(x));
                kws = Object.entries(kws)
                    .map(([k, v]) => [k, toPy(v)])
                    .flat();
                const ret = tryCatch(
                    () => chainOrSuspend(maybeFn.tp$call(args, kws), (rv: any) => toJs(rv)),
                    (e: any) => {
                        throw e;
                    }
                );
                if (ret instanceof Suspension) {
                    return suspToPromise(() => ret, {
                        "*": () => {
                            if (stopExecution) {
                                const { id, fn } = (self as unknown as CustomWorker).currentTask!;
                                throw pyCall(WorkerTaskKilled, [`<WorkerTask '${fn}' (${id})> Killed`]);
                            }
                        },
                    });
                }
                return ret;
            });
        }
    }
}

export const webWorkerScript = `
let stopExecution = false;
const window = self;
self.importScripts([\\'${getSkultpUrl()}\\']);
(${initWorkerRPC})(self);
Sk.builtinFiles = ${JSON.stringify(Sk.builtinFiles)}; Sk.builtins.worker = Sk.ffi.toPy(self);
{source};
(${workWithSkulpt})();
`;
