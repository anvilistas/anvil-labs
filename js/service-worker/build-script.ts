import * as esbuild from "https://deno.land/x/esbuild@v0.17.17/mod.js";
import * as path from "https://deno.land/std/path/mod.ts";

const __dirname = path.dirname(path.fromFileUrl(import.meta.url));
// import * as esbuild from "esbuild";
// deno run -A build-script.ts
const client = path.resolve(__dirname, "./client/mod.ts");
const sw = path.resolve(__dirname, "./worker/mod.ts");

let result = await esbuild.build({
    entryPoints: [sw],
    target: ["es2019"],
    bundle: true,
    format: "cjs",
    outfile: path.resolve(__dirname, "../../theme/assets/anvil_labs/sw.js"),
    minify: true,
});

console.log("result:", result);

result = await esbuild.build({
    entryPoints: [client],
    target: ["es2019"],
    bundle: true,
    format: "esm",
    outfile: path.resolve(__dirname, "../../theme/assets/anvil_labs/client_sw.js"),
    minify: true,
});

console.log("result:", result);
esbuild.stop();
