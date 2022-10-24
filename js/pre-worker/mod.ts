/** Because anvil doesn't expose source code of app files and we need it */
declare const Sk: any;

let oldRead: (x: string) => string = () => {
    throw new Error("not implemented");
};

function anvilLabsRead(filename: string) {
    // this will throw if the file doesn't exist
    const rv = oldRead(filename);
    const files = Sk.builtinFiles.files;
    if (filename.startsWith("app/")) {
        files[filename] = rv;
        const [app, root] = filename.split("/");
        // root app package needs to exist
        files[`app/${root}/__init__.py`] ??= "pass";
    }
    return rv;
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
