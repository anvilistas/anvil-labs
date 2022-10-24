declare var Sk: any;

/** @todo - we could add anvil.server.call but it might be too clever */

export default function () {
    const {
        abstr: { setUpModuleMethods },
        ffi: { toPy },
    } = Sk;

    const mod = { __name__: toPy("server") };

    setUpModuleMethods("server", mod, {
        get_api_origin: {
            $meth() {
                // @ts-ignore
                return toPy(self.anvilLabsEndpoint);
            },
            $flags: { NoArgs: true },
        },
    });

    return mod;
}
