import { BackgroundWorker as Worker } from "./bg-worker.ts";
declare global {
    interface Window {
        _BgWorker: typeof Worker;
    }
}

window._BgWorker = Worker;
