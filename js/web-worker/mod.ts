import { BackgroundWorker as Worker, WorkerTaskKilled } from "./client-worker.ts";
declare global {
    interface Window {
        anvilLabs: {
            Worker: typeof Worker;
            WorkerTaskKilled: typeof WorkerTaskKilled;
        };
    }
}

window.anvilLabs = { Worker, WorkerTaskKilled };
