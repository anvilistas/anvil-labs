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
