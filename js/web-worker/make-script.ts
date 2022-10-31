// deno-lint-ignore-file no-explicit-any no-var
import { initWorkerRPC } from "./web-worker.ts";
import type { CustomWorker } from "./web-worker.ts";
import jsMod from "../dummy-modules/anvil-js.ts";

declare var Sk: any;
declare var stopExecution: boolean;
declare var self: CustomWorker;

function getSkultpUrl() {
    const scripts = document.getElementsByTagName("script");
    return Array.from(scripts).find((s) => s.src?.includes("skulpt.min.js"))!.src;
}

function configureSkulpt() {
    Sk.configure({
        output(message: string) {
            return self.postMessage({ type: "OUT", message });
        },
        yieldLimit: 300,
        syspath: ["app"],
        read(filename: string) {
            // @ts-ignore
            const rv = self.anvilFiles[filename];
            if (rv !== undefined) return rv;
            return Sk.misceval.promiseToSuspension(
                self.fetchModule(filename).then((content) => {
                    if (content == null) {
                        throw "No module named " + filename;
                    }
                    return content;
                })
            );
        },
    });
}

function workWithSkulpt() {
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

    Sk.builtins.self = Sk.builtins.worker = toPy(self);

    const WorkerTaskKilled = buildClass({ __name__: "anvil_labs.web_worker" }, () => {}, "WorkerTaskKilled", [
        RuntimeError,
    ]);

    const moduleScope: { [attr: string]: any } = Sk.sysmodules.quick$lookup(toPy("__main__")).$d;

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
const $f = (self.anvilFiles = {});
$f["src/lib/anvil/__init__.py"] = "";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${jsMod};\`;
$f["src/lib/anvil/server.js"] = "";
(${configureSkulpt})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${workWithSkulpt})();
})
`;
