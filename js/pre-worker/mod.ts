/** Because anvil doesn't expose source code of app files and we need it */
declare const Sk: any;

let oldRead: (x: string) => any = () => {
    throw new Error("not implemented");
};

function updateFiles(filename: string, sourceCode: string) {
    if (filename.startsWith("app/")) {
        const files = Sk.builtinFiles.files;
        files[filename] = sourceCode;
        const [app, root] = filename.split("/");
        // root app package needs to exist
        files[`app/${root}/__init__.py`] ??= "pass";
    }
    return sourceCode;
}

function anvilLabsRead(filename: string) {
    // this will throw if the file doesn't exist
    const rv = oldRead(filename);
    if (rv instanceof Sk.misceval.Suspension) {
        return Sk.misceval.promiseToSuspension(
            Sk.misceval.asyncToPromise(() => rv).then((sourceCode: string) => updateFiles(filename, sourceCode))
        );
    } else {
        return updateFiles(filename, rv);
    }
}

Object.defineProperty(Sk, "read", {
    get() {
        return anvilLabsRead;
    },
    set(v) {
        oldRead = v;
    },
    configurable: true,
});
