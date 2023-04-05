import * as esbuild from "https://deno.land/x/esbuild@v0.14.38/mod.js";
import * as path from "https://deno.land/std/path/mod.ts";

const __dirname = path.dirname(path.fromFileUrl(import.meta.url));
// import * as esbuild from "esbuild";
// deno run -A build-script.ts
const mod = path.resolve(__dirname, "./mod.ts");

let result = await esbuild.build({
    entryPoints: [mod],
    target: ["es2019"],
    bundle: true,
    format: "iife",
    outfile: path.resolve(__dirname, "./worker.min.cjs"),
    minify: true,
});

console.log("result:", result);

result = await esbuild.build({
    entryPoints: [mod],
    bundle: true,
    format: "iife",
    outfile: path.resolve(__dirname, "./worker.cjs"),
});

console.log("result:", result);
esbuild.stop();

const in_ = path.resolve(__dirname, "./worker.min.cjs");
const out_ = path.resolve(__dirname, "../../", "client_code/web_worker.py");

const script = Deno.readTextFileSync(in_);

let pyFile = Deno.readTextFileSync(out_);
pyFile = pyFile.replace(/_script = """.*?"""/s, `_script = """\n'use strict';\n${script}"""`);
Deno.writeTextFileSync(out_, pyFile);
