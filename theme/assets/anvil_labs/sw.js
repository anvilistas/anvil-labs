function f() {
    let {
            ffi: { proxy: e, toPy: t },
            abstr: { setUpModuleMethods: n, objectSetItem: o },
            misceval: { promiseToSuspension: r, chain: a },
        } = Sk,
        c = { __name__: t("js"), window: e(self) };
    async function g(i) {
        let s = await new Function("return import(" + JSON.stringify(i.toString()) + ")").call(null);
        return e(s);
    }
    return (
        n("js", c, {
            await_promise: {
                $meth(i) {
                    let s = i.valueOf();
                    return s instanceof Promise || (s && s.then && typeof s.then == "function")
                        ? a(r(s), (S) => t(S, { dictHook: (v) => e(v) }))
                        : i;
                },
                $flags: { OneArg: !0 },
            },
            import_from: {
                $meth(i) {
                    return r(g(i));
                },
                $flags: { OneArg: !0 },
            },
        }),
        o(Sk.sysmodules, t("anvil.js.window"), c.window),
        c
    );
}
var u = new Map([
    ["src/lib/anvil/__init__.py", ""],
    ["src/lib/anvil/js.js", `var $builtinmodule=${f};`],
    ["src/lib/anvil/server.py", ""],
]);
var w = d();
function d() {
    let e = { resolve: () => {}, reject: () => {} };
    return (
        (e.promise = new Promise((t, n) => {
            (e.resolve = t), (e.reject = n);
        })),
        e
    );
}
var l = new Map();
function M(e) {
    let t = crypto.randomUUID();
    postMessage({ type: "IMPORT", id: t, filename: e });
    let n = d();
    return l.set(t, n), n.promise;
}
function p() {
    Sk.configure({
        output(e) {
            return self.postMessage({ type: "OUT", message: e });
        },
        yieldLimit: 300,
        syspath: ["app"],
        read(e) {
            let t = u.get(e);
            return t !== void 0
                ? t
                : Sk.misceval.promiseToSuspension(
                      M(e).then((n) => {
                          if (n == null) throw "No module named " + e;
                          return n;
                      })
                  );
        },
    }),
        (Sk.builtins.self = Sk.ffi.proxy(self)),
        w.resolve(!0);
}
function _(e) {
    let { data: t } = e;
    if (t.type === "MODULE") {
        let { id: n, content: o } = t,
            r = l.get(n);
        if (r === void 0) return;
        let { resolve: a } = r;
        l.delete(n), a(o);
    }
}
self.addEventListener("message", _);
self.window = self;
importScripts(
    "https://anvil.works/runtime-new/runtime/js/lib/skulpt.min.js",
    "https://cdn.jsdelivr.net/npm/localforage@1.10.0/dist/localforage.min.js"
);
p();
k();
self.addEventListener("sync", (e) => {
    m("sync", { tag: e.tag });
});
function k() {
    function e(t, n = []) {
        if (t.length !== 1) throw new Sk.builtin.TypeError("Expeceted one arg to raise_event");
        let o = {};
        for (let r = 0; r < n.length; r += 2) {
            let a = n[r],
                c = n[r + 1];
            o[a] = Sk.ffi.toJs(c);
        }
        m(t[0].toString(), o);
    }
    (e.co_fastcall = !0), (self.raise_event = new Sk.builtin.func(e));
}
function h(e) {
    let t = e.data,
        { type: n } = t;
    if (n !== "INIT") return;
    let { name: o } = t;
    Sk.misceval.asyncToPromise(() => Sk.importMain(o, !1, !0));
}
self.addEventListener("message", h);
async function y(e) {
    e.ANVIL_LABS = !0;
    let t = await self.clients.matchAll({ includeUncontrolled: !0, type: "window" });
    for (let n of t) n.postMessage(e);
}
self.postMessage = y;
function m(e, t = {}) {
    (t.event_name = e), y({ type: "EVENT", name: e, kws: t });
}
