import * as esbuild from "https://deno.land/x/esbuild@v0.14.38/mod.js";
import * as path from "https://deno.land/std/path/mod.ts";

const __dirname = path.dirname(path.fromFileUrl(import.meta.url));
// import * as esbuild from "esbuild";
// deno run -A build-script.ts

let result = await esbuild.build({
    entryPoints: ["mod.ts"],
    bundle: true,
    format: "esm",
    outfile: "worker.min.js",
    minify: true,
});

console.log("result:", result);

result = await esbuild.build({
    entryPoints: ["mod.ts"],
    bundle: true,
    format: "esm",
    outfile: "worker.js",
});

console.log("result:", result);
esbuild.stop();

const in_ = path.resolve(__dirname, "./worker.min.js");
const out_ = path.resolve(__dirname, "../../", "client_code/web_worker.py");

const script = Deno.readTextFileSync(in_);

let pyFile = Deno.readTextFileSync(out_);
pyFile = pyFile.replace(/_script = """.*?"""/s, `_script = """\n${script}"""`);
Deno.writeTextFileSync(out_, pyFile);
