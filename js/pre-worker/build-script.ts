import * as esbuild from "https://deno.land/x/esbuild@v0.14.38/mod.js";
import * as path from "https://deno.land/std/path/mod.ts";

const __dirname = path.dirname(path.fromFileUrl(import.meta.url));
// import * as esbuild from "esbuild";
// deno run -A build-script.ts
const mod = path.resolve(__dirname, "./mod.ts");

const result = await esbuild.build({
    entryPoints: [mod],
    bundle: true,
    format: "iife",
    outfile: path.resolve(__dirname, "../../theme/assets/anvil-labs/worker.js"),
    minify: true,
});

console.log("result:", result);
esbuild.stop();
