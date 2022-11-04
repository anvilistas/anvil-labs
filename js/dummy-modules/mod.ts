import jsMod from "./anvil-js.ts";
import jsonMod from "./json.ts";
import tzMod from "./anvil-tz.ts";

export const ANVIL_FILES = new Map([
    ["src/lib/json.js", `var $builtinmodule=${jsonMod};`],
    ["src/lib/anvil/__init__.py", "def is_server_side():return False"],
    ["src/lib/anvil/js.js", `var $builtinmodule=${jsMod};`],
    ["src/lib/anvil/tz.py", "import datetime,time\nclass tzoffset(datetime.tzinfo):\n\tdef __init__(B,**A):\n\t\tif len(A)>1 or len(A)==1 and'seconds'not in A and 'hours'not in A and'minutes'not in A:raise TypeError('bad initialization')\n\t\tB._offset=datetime.timedelta(**A)\n\tdef utcoffset(A,dt):return A._offset\n\tdef dst(A,dt):return datetime.timedelta()\n\tdef tzname(A,dt):return None\n\tdef __repr__(A):return'tzoffset(%s hours)'%(A._offset.total_seconds()/3600)\nclass tzlocal(tzoffset):\n\tdef __init__(B):\n\t\tif time.localtime().tm_isdst and time.daylight:A=-time.altzone\n\t\telse:A=-time.timezone\n\t\ttzoffset.__init__(B,seconds=A)\n\tdef __repr__(A):return'tzlocal(%s hour offset)'%(A._offset.total_seconds()/3600)\nclass tzutc(tzoffset):\n\tdef __init__(A):tzoffset.__init__(A,minutes=0)\n\tdef __repr__(A):return'tzutc'\nUTC=tzutc()"],
    ["src/lib/anvil/server.py", `class SerializationError(Exception):0\ndef get_app_origin():return self.anvilAppOrigin\ndef get_api_origin():return get_app_origin()+'/_/api'\ndef call(*args,**kws):\n\tfrom anvil_labs.kompot import serialize,preserve,reconstruct;name,*args=args;rv=self.fetch(get_api_origin()+f"/anvil_labs_private_call?name={name}",{'headers':{'Content-Type':'application/json'},'method':'POST','body':self.JSON.stringify(preserve([args,kws]))});result,error=rv.json()\n\tif error:raise Exception(error)\n\treturn reconstruct(dict(result))\ndef portable_class(*args,**kws):0`],
]);
