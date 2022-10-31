import jsMod from "./anvil-js.ts";
import serverMod from "./anvil-server.ts";

export const ANVIL_FILES = new Map([
    ["src/lib/anvil/__init__.py", ""],
    ["src/lib/anvil/js.js", `var $builtinmodule=${jsMod};`],
    ["src/lib/anvil/server.js", `var $builtinmodule=${serverMod};`],
]);
