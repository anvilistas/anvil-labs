import jsMod from "./anvil-js.ts";
import jsonMod from "./json.ts";

export const ANVIL_FILES = new Map([
    ["src/lib/json.js", `var $builtinmodule=${jsonMod};`],
    ["src/lib/anvil/__init__.py", "def is_server_side():return False"],
    ["src/lib/anvil/js.js", `var $builtinmodule=${jsMod};`],
    [
        "src/lib/anvil/tz.py",
        "import datetime,time\nclass tzoffset(datetime.tzinfo):\n\tdef __init__(A,**B):A._offset=datetime.timedelta(**B)\n\tdef utcoffset(A,dt):return A._offset\n\tdef dst(A,dt):return datetime.timedelta()\n\tdef tzname(A,dt):return None\nclass tzlocal(tzoffset):\n\tdef __init__(B):\n\t\tif time.localtime().tm_isdst and time.daylight:A=-time.altzone\n\t\telse:A=-time.timezone\n\t\ttzoffset.__init__(B,seconds=A)\nclass tzutc(tzoffset):0\nUTC=tzutc()",
    ],
    [
        "src/lib/anvil/server.py",
        `class SerializationError(Exception):0\ndef get_app_origin():return self.anvilAppOrigin\ndef get_api_origin():return get_app_origin()+'/_/api'\ndef call(*args,**kws):\n\tfrom anvil_labs.kompot import preserve,reconstruct,serialize;name,*args=args;rv=self.fetch(get_api_origin()+f"/anvil_labs_private_call?name={name}",{'headers':{'Content-Type':'application/json'},'method':'POST','body':self.JSON.stringify(preserve([args,kws]))});result,error=rv.json()\n\tif error:raise Exception(error)\n\treturn reconstruct(dict(result))\ndef portable_class(cls,name=None):\n\tif name is None and isinstance(cls,str):name=cls;return lambda cls:cls\n\telse:return cls`,
    ],
]);
