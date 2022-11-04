declare const Sk: any;

export default function () {
    const {
        builtin: {
            TypeError: pyTypeError,
            str: pyStr,
            none: { none$: pyNone },
            func: pyFunc,
        },
        misceval: { callsimArray: pyCall, buildClass: buildPyClass },
        abstr: { checkOneArg, lookupSpecial },
        ffi: { toPy, toJs },
    } = Sk;

    const pyMod: any = { __name__: toPy("anvil.tz") };

    const kwToObj = (kws?: any) => {
        const rv: { [argName: string]: any } = {};
        if (!kws) return rv;
        for (let i = 0; i < kws.length; i += 2) {
            rv[kws[i] as string] = kws[i + 1];
        }
        return rv;
    };

    debugger;
    const datetimeMod = Sk.importModule("datetime", false, true);
    const tzinfo = datetimeMod.tp$getattr(toPy("tzinfo"));
    const timedelta = datetimeMod.tp$getattr(toPy("timedelta"));

    const s_offset = toPy("_offset");

    const initOffset = (args: any, kws: any[] = []) => {
        checkOneArg("tzoffset", args);
        const self = args[0];
        const kwObj = kwToObj(kws);
        const kwLen = kws.length / 2;

        if (kwLen > 1 || !(kwLen === 0 || "hours" in kwObj || "minutes" in kwObj || "seconds" in kwObj)) {
            throw new pyTypeError(
                "tzoffset must be initialised with precisely one of 'seconds', 'minutes' or 'hours' keyword arguments"
            );
        }

        const offset = pyCall(timedelta, [], kws);
        self.tp$setattr(s_offset, offset);
        return pyNone;
    };

    initOffset.co_fastcall = 1;

    pyMod["tzoffset"] = buildPyClass(
        pyMod,
        (_: any, $loc: any) => {
            $loc["__init__"] = new pyFunc(initOffset);
            $loc["utcoffset"] = new pyFunc((self: any) => self.tp$getattr(s_offset));
            $loc["dst"] = new pyFunc(() => pyCall(timedelta));
            $loc["tzname"] = new pyFunc(() => pyNone);
            $loc["__repr__"] = new pyFunc((self: any) => {
                const totalSecondsFunc = self.tp$getattr(s_offset).tp$getattr(toPy("total_seconds"));
                const modname = lookupSpecial(self, pyStr.$module);
                const name = self.tp$name;
                return toPy(`<${modname}.${name} (${toJs(pyCall(totalSecondsFunc)) / 3600} hour offset)>`);
            });
        },
        "tzoffset",
        [tzinfo]
    );

    pyMod["tzlocal"] = buildPyClass(
        pyMod,
        (_: any, $loc: any) => {
            $loc["__init__"] = new pyFunc((self: any) =>
                initOffset([self], ["minutes", toPy(-new Date().getTimezoneOffset())])
            );
            $loc["tzname"] = new pyFunc(() => toPy("Browser Local"));
        },
        "tzlocal",
        [pyMod["tzoffset"]]
    );

    pyMod["tzutc"] = buildPyClass(
        pyMod,
        (_: any, $loc: any) => {
            $loc["__init__"] = new pyFunc((self: any) => initOffset([self], ["minutes", toPy(0)]));
            $loc["tzname"] = new pyFunc(() => toPy("UTC"));
            $loc["__repr__"] = new pyFunc(() => toPy("<anvil.tz.tzutc>"));
        },
        "tzlocal",
        [pyMod["tzoffset"]]
    );

    pyMod["UTC"] = pyCall(pyMod["tzutc"]);

    return pyMod;
}
