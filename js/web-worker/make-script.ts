// deno-lint-ignore-file no-explicit-any no-var
import { initWorkerRPC } from "./web-worker.ts";
import type { CustomWorker } from "./web-worker.ts";

declare var Sk: any;
declare var stopExecution: boolean;
declare var $compiledmod: (scope: any) => void;

let skulptUrl: string;

function getSkultpUrl() {
    if (skulptUrl !== undefined) return skulptUrl;

    for (const s of document.getElementsByTagName("script")) {
        if (s.src.includes("skulpt.min.js")) {
            skulptUrl = s.src;
            break;
        }
    }
    return skulptUrl!;
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
        misceval: { tryCatch, chain: chainOrSuspend, Suspension, asyncToPromise: suspToPromise },
    } = Sk;

    Sk.builtins.self = toPy(self);

    const moduleScope: { [attr: string]: any } = {};
    $compiledmod(moduleScope);
    for (const [attr, maybeFn] of Object.entries(moduleScope)) {
        if (maybeFn.tp$call) {
            (self as unknown as CustomWorker).registerFn(attr, (...args) => {
                args = args.map((x) => toPy(x));
                const ret = tryCatch(
                    () => chainOrSuspend(maybeFn.tp$call(args), (rv: any) => toJs(rv)),
                    (e: any) => {
                        throw e;
                    }
                );
                if (ret instanceof Suspension) {
                    return suspToPromise(() => ret, {
                        "*": () => {
                            if (stopExecution) {
                                throw new RuntimeError("killed");
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
(${initWorkerRPC})(self);
self.importScripts(['${getSkultpUrl()}']); Sk.builtinFiles = ${JSON.stringify(
    Sk.builtinFiles
)}; Sk.builtins.worker = Sk.ffi.toPy(self);
{source};
(${workWithSkulpt})();
`;
