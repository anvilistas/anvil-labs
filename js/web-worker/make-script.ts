// deno-lint-ignore-file no-explicit-any no-var
import { initWorkerRPC } from "./web-worker.ts";
import type { CustomWorker } from "./web-worker.ts";
import jsMod from "../dummy-modules/anvil-js.ts";
import jsonMod from "../dummy-modules/json.ts";

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
$f["src/lib/json.js"] = \`var $builtinmodule=${jsonMod};\`;
$f["src/lib/anvil/__init__.py"] = "def is_server_side():return False";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${jsMod};\`;
$f["src/lib/anvil/tz.py"] = \`import datetime,time\nclass tzoffset(datetime.tzinfo):\n  def __init__(A,**B):A._offset=datetime.timedelta(**B)\n  def utcoffset(A,dt):return A._offset\n  def dst(A,dt):return datetime.timedelta()\n  def tzname(A,dt):return None\nclass tzlocal(tzoffset):\n  def __init__(B):\n    if time.localtime().tm_isdst and time.daylight:A=-time.altzone\n    else:A=-time.timezone\n    tzoffset.__init__(B,seconds=A)\nclass tzutc(tzoffset):0\nUTC=tzutc()\`;
$f["src/lib/anvil/server.py"] = \`class SerializationError(Exception):0\ndef get_app_origin():return self.anvilAppOrigin\ndef get_api_origin():return get_app_origin()+'/_/api'\ndef call(*args,**kws):\n  from anvil_labs.kompot import preserve,reconstruct,serialize;name,*args=args;rv=self.fetch(get_api_origin()+f"/anvil_labs_private_call?name={name}",{'headers':{'Content-Type':'application/json'},'method':'POST','body':self.JSON.stringify(preserve([args,kws]))});result,error=rv.json()\n  if error:raise Exception(error)\n  return reconstruct(dict(result))\ndef portable_class(*args,**kws):from anvil_labs.kompot import register;return register(*args)\`;
(${configureSkulpt})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${workWithSkulpt})();
})
`;
