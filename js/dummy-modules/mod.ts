import jsMod from "./anvil-js.ts";

export const ANVIL_FILES = new Map([
    ["src/lib/anvil/__init__.py", ""],
    ["src/lib/anvil/js.js", `var $builtinmodule=${jsMod};`],
    ["src/lib/anvil/server.js", ""],
]);
