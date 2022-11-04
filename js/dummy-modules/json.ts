declare var Sk: any;

export default function () {
    const {
        ffi: { toPy, toJs },
        abstr: { setUpModuleMethods },
    } = Sk;

    const jsonMod = { __name__: new toPy("json") };

    setUpModuleMethods("js", jsonMod, {
        dumps: {
            $meth(pyObj: any) {
                return new toPy(JSON.stringify(toJs(pyObj)));
            },
            $flags: { OneArg: true },
        },
        loads: {
            $meth(s: any) {
                return toPy(JSON.parse(s.toString()));
            },
            $flags: { OneArg: true },
        },
    });

    return jsonMod;
}
