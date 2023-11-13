declare var Sk: any;

export default function () {
    const {
        ffi: { proxy, toPy },
        abstr: { setUpModuleMethods, objectSetItem },
        misceval: { promiseToSuspension, chain: chainOrSuspend },
        builtin: { func: pyFunc, ExternalError, property: pyProperty }

    } = Sk;

    const jsMod = { __name__: toPy("js"), window: proxy(self), ExternalError };

    async function getModule(url: any) {
        const mod = await new Function("return import(" + JSON.stringify(url.toString()) + ")").call(null);
        return proxy(mod);
    }

    setUpModuleMethods("js", jsMod, {
        await_promise: {
            $meth(wrappedPromise: any) {
                const maybePromise = wrappedPromise.valueOf();
                if (
                    maybePromise instanceof Promise ||
                    (maybePromise && maybePromise.then && typeof maybePromise.then === "function")
                ) {
                    return chainOrSuspend(promiseToSuspension(maybePromise), (res: any) =>
                        toPy(res, { dictHook: (obj: any) => proxy(obj) })
                    );
                }
                // we weren't given a wrapped promise so just return the argument we were given :shrug:
                return wrappedPromise;
            },
            $flags: { OneArg: true },
        },
        import_from: {
            $meth(url: string) {
                return promiseToSuspension(getModule(url));
            },
            $flags: { OneArg: true },
        },
    });

    objectSetItem(Sk.sysmodules, toPy("anvil.js.window"), jsMod.window);

    jsMod.ExternalError.prototype.original_error = new pyProperty(
        new pyFunc((self) => {
            return toPy(self.nativeError, { dictHook: (obj) => proxy(obj) });
        })
    );

    return jsMod;
}
