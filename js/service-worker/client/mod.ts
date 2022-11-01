/// <reference lib="dom" />
import { getModule, getSkulptUrl } from "../../worker/utils/client.ts";

let sw: ServiceWorker | null;

async function onImport(e: any) {
    const { data } = e;
    if (!data.ANVIL_LABS) return;
    if (data.type !== "IMPORT") return;
    const { filename, id } = data;

    const content = await getModule(filename);
    sw?.postMessage({ type: "MODULE", content, id });
}

export async function init() {
    const reg = await navigator.serviceWorker.register("_/theme/anvil_labs/sw.js");
    try {
        reg.update();
    } catch {
        // we might be offline
    }

    sw = reg.active || reg.installing || reg.waiting || null;

    sw?.postMessage({ type: "SKULPT", url: getSkulptUrl() });

    navigator.serviceWorker.addEventListener("message", onImport);

    return [sw, reg];
}

export default init;
