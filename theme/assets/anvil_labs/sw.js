function d(){let{ffi:{proxy:e,toPy:t},abstr:{setUpModuleMethods:n,objectSetItem:s},misceval:{promiseToSuspension:r,chain:o}}=Sk,l={__name__:t("js"),window:e(self)};async function v(a){let i=await new Function("return import("+JSON.stringify(a.toString())+")").call(null);return e(i)}return n("js",l,{await_promise:{$meth(a){let i=a.valueOf();return i instanceof Promise||i&&i.then&&typeof i.then=="function"?o(r(i),S=>t(S,{dictHook:A=>e(A)})):a},$flags:{OneArg:!0}},import_from:{$meth(a){return r(v(a))},$flags:{OneArg:!0}}}),s(Sk.sysmodules,t("anvil.js.window"),l.window),l}function u(){let{ffi:{toPy:e,toJs:t},abstr:{setUpModuleMethods:n}}=Sk,s={__name__:new e("json")};return n("js",s,{dumps:{$meth(r){return new e(JSON.stringify(t(r)))},$flags:{OneArg:!0}},loads:{$meth(r){return e(JSON.parse(r.toString()))},$flags:{OneArg:!0}}}),s}var p=new Map([["src/lib/json.js",`var $builtinmodule=${u};`],["src/lib/anvil/__init__.py","def is_server_side():return False"],["src/lib/anvil/js.js",`var $builtinmodule=${d};`],["src/lib/anvil/tz.py",`import datetime,time
class tzoffset(datetime.tzinfo):
	def __init__(B,**A):
		if len(A)>1 or len(A)==1 and'seconds'not in A and 'hours'not in A and'minutes'not in A:raise TypeError('bad initialization')
		B._offset=datetime.timedelta(**A)
	def utcoffset(A,dt):return A._offset
	def dst(A,dt):return datetime.timedelta()
	def tzname(A,dt):return None
	def __repr__(A):return'tzoffset(%s hours)'%(A._offset.total_seconds()/3600)
class tzlocal(tzoffset):
	def __init__(B):
		if time.localtime().tm_isdst and time.daylight:A=-time.altzone
		else:A=-time.timezone
		tzoffset.__init__(B,seconds=A)
	def __repr__(A):return'tzlocal(%s hour offset)'%(A._offset.total_seconds()/3600)
class tzutc(tzoffset):
	def __init__(A):tzoffset.__init__(A,minutes=0)
	def __repr__(A):return'tzutc'
UTC=tzutc()`],["src/lib/anvil/server.py",`class SerializationError(Exception):0
def get_app_origin():return self.anvilAppOrigin
def get_api_origin():return get_app_origin()+'/_/api'
def call(*args,**kws):
	from anvil_labs.kompot import serialize,preserve,reconstruct;name,*args=args;rv=self.fetch(get_api_origin()+f"/anvil_labs_private_call?name={name}",{'headers':{'Content-Type':'application/json'},'method':'POST','body':self.JSON.stringify(preserve([args,kws]))});result,error=rv.json()
	if error:raise Exception(error)
	return reconstruct(dict(result))
def portable_class(*args,**kws):0`]]);var h=m();function m(){let e={resolve:()=>{},reject:()=>{}};return e.promise=new Promise((t,n)=>{e.resolve=t,e.reject=n}),e}var c=new Map;function w(e){let t=crypto.randomUUID();self.postMessage({type:"IMPORT",id:t,filename:e});let n=m();return c.set(t,n),n.promise}var f=e=>{let{builtin:{BaseException:t},ffi:{toJs:n}}=Sk,s,r,o;e instanceof t?(r=n(e.args),s=e.tp$name,o=e.traceback):(s=e.constructor?.name??"<unknown>",r=e.message?[e.message]:[]),self.postMessage({type:"ERROR",errorType:s,errorArgs:r,errorTb:o})};function _(){Sk.configure({output(e){return self.postMessage({type:"OUT",message:e})},yieldLimit:300,syspath:["app"],read(e){let t=p.get(e);return t!==void 0?t:Sk.misceval.promiseToSuspension(w(e).then(n=>{if(n==null)throw"No module named "+e;return n}))},uncaughtException:e=>{f(e)}}),Sk.builtins.self=Sk.ffi.proxy(self),h.resolve(!0)}function b(e){let{data:t}=e;if(t.type==="MODULE"){let{id:n,content:s}=t,r=c.get(n);if(r===void 0)return;let{resolve:o}=r;c.delete(n),o(s)}}self.addEventListener("message",b);importScripts("https://anvil.works/runtime-new/runtime/js/lib/skulpt.min.js","https://cdn.jsdelivr.net/npm/localforage@1.10.0/dist/localforage.min.js","https://cdn.jsdelivr.net/npm/uuid@8.3.2/dist/umd/uuid.min.js");self.window=self;var{builtin:{func:k,none:{none$:D}},misceval:{asyncToPromise:M},ffi:{toJs:J},importMain:j}=Sk;_();E();self.addEventListener("sync",e=>{y("sync",{tag:e.tag})});function E(){function e(t,n=[]){if(t.length!==1)throw new Sk.builtin.TypeError("Expeceted one arg to raise_event");let s={};for(let r=0;r<n.length;r+=2){let o=n[r],l=n[r+1];s[o]=Sk.ffi.toJs(l)}y(t[0].toString(),s)}e.co_fastcall=!0,self.raise_event=new k(e),self.sync_event_handler=t=>n=>n.waitUntil(t(n))}async function O(e){let t=e.data,{type:n}=t;if(n!=="INIT")return;let{name:s}=t;try{await M(()=>j(s,!1,!0))}catch(r){console.error(r),f(r)}}self.addEventListener("message",O);self.anvilAppOrigin="";function z(e){let t=e.data,{type:n}=t;if(n!=="APPORIGIN")return;let{origin:s}=t;self.anvilAppOrigin=s}self.addEventListener("message",z);async function g(e){e.ANVIL_LABS=!0;let t=await self.clients.matchAll({includeUncontrolled:!0,type:"window"});for(let n of t)n.postMessage(e)}self.postMessage=g;function y(e,t={}){t.event_name=e,g({type:"EVENT",name:e,kws:t})}
