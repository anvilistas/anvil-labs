declare const Sk: any;

export function getSkulptUrl() {
    const scripts = document.getElementsByTagName("script");
    return Array.from(scripts).find((s) => s.src?.includes("skulpt.min.js"))!.src;
}

export async function getModule(filename: string) {
    let content: string | null = null;
    try {
        content = Sk.read(filename);
        if (typeof content !== "string") {
            content = await Sk.misceval.asyncToPromise(() => content);
        }
    } catch {
        if (filename.startsWith("app/")) {
            const [app, root, rest] = filename.split("/");
            if (rest === "__init__.py" && root !== "anvil") {
                // then we're an app root package and we should already appear in sysmodules
                content = "pass";
            }
        } else {
            content = null;
        }
    }
    return content;
}

export async function reloadModules() {
    let localforage = window.localforage;
    if (localforage === undefined) {
        localforage = (
            await import(
                "https://cdn.skypack.dev/pin/localforage@v1.10.0-vSTz1U7CF0tUryZh6xTs/mode=imports,min/optimized/localforage.js"
            )
        ).default;
    }
    const store = localforage.createInstance({
        name: "anvil-labs-sw",
        storeName: "lib",
    });
    await store.ready();
    const keys = await store.keys();
    for (const key of keys) {
        const value = store.getItem(key);
        const content = await getModule(key) ?? 0;
        if (content !== value) {
            store.setItem(key, content);
        }
    }
}
