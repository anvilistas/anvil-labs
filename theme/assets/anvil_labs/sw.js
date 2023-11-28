var U=Object.defineProperty;var z=(t,e,n)=>e in t?U(t,e,{enumerable:!0,configurable:!0,writable:!0,value:n}):t[e]=n;var g=(t,e,n)=>(z(t,typeof e!="symbol"?e+"":e,n),n);function A(){let{ffi:{proxy:t,toPy:e},abstr:{setUpModuleMethods:n,objectSetItem:r},misceval:{promiseToSuspension:s,chain:i},builtin:{func:o,ExternalError:c,property:m}}=Sk,p={__name__:e("js"),window:t(self),ExternalError:c};async function b(f){let l=await new Function("return import("+JSON.stringify(f.toString())+")").call(null);return t(l)}return n("js",p,{await_promise:{$meth(f){let l=f.valueOf();return l instanceof Promise||l&&l.then&&typeof l.then=="function"?i(s(l),x=>e(x,{dictHook:$=>t($)})):f},$flags:{OneArg:!0}},import_from:{$meth(f){return s(b(f))},$flags:{OneArg:!0}}}),r(Sk.sysmodules,e("anvil.js.window"),p.window),p.ExternalError.prototype.original_error=new m(new o(f=>e(f.nativeError,{dictHook:l=>t(l)}))),p}function M(){let{ffi:{toPy:t,toJs:e},abstr:{setUpModuleMethods:n}}=Sk,r={__name__:new t("json")};return n("js",r,{dumps:{$meth(s){return new t(JSON.stringify(e(s)))},$flags:{OneArg:!0}},loads:{$meth(s){return t(JSON.parse(s.toString()))},$flags:{OneArg:!0}}}),r}var O=new Map([["src/lib/json.js",`var $builtinmodule=${M};`],["src/lib/anvil/__init__.py","def is_server_side():return False"],["src/lib/anvil/js.js",`var $builtinmodule=${A};`],["src/lib/anvil/tz.py",`import datetime,time
class tzoffset(datetime.tzinfo):
	def __init__(A,**B):A._offset=datetime.timedelta(**B)
	def utcoffset(A,dt):return A._offset
	def dst(A,dt):return datetime.timedelta()
	def tzname(A,dt):return None
class tzlocal(tzoffset):
	def __init__(B):
		if time.localtime().tm_isdst and time.daylight:A=-time.altzone
		else:A=-time.timezone
		tzoffset.__init__(B,seconds=A)
class tzutc(tzoffset):0
UTC=tzutc()`],["src/lib/anvil/server.py",`class SerializationError(Exception):0
def get_app_origin():return self.anvilAppOrigin
def get_api_origin():return get_app_origin()+'/_/api'
def call(*args,**kws):
	from anvil_labs.kompot import preserve,reconstruct,serialize;name,*args=args;rv=self.fetch(get_api_origin()+f"/anvil_labs_private_call?name={name}",{'headers':{'Content-Type':'application/json'},'method':'POST','body':self.JSON.stringify(preserve([args,kws]))});result,error=rv.json()
	if error:raise Exception(error)
	return reconstruct(dict(result))
def portable_class(cls,name=None):
	if name is None and isinstance(cls,str):name=cls;return lambda cls:cls
	else:return cls`]]);importScripts("https://anvil.works/runtime-new/runtime/js/lib/skulpt.min.js","https://cdn.jsdelivr.net/npm/localforage@1.10.0/dist/localforage.min.js","https://cdn.jsdelivr.net/npm/uuid@8.3.2/dist/umd/uuid.min.js");var j=localforage.createInstance({name:"anvil-labs-sw",storeName:"lib"}),R=d();function d(){let t={resolve:()=>{},reject:()=>{}};return t.promise=new Promise((e,n)=>{t.resolve=e,t.reject=n}),t}var k=new Map;function C(t){let e=Math.random().toString(36).substring(6);self.postMessage({type:"IMPORT",id:e,filename:t});let n=d();return k.set(e,n),n.promise}var S=t=>{var o,c;let{builtin:{BaseException:e},ffi:{toJs:n}}=Sk,r,s,i;t instanceof e?(s=n(t.args),r=t.tp$name,i=t.traceback):(r=(c=(o=t.constructor)==null?void 0:o.name)!=null?c:"<unknown>",s=t.message?[t.message]:[]),self.postMessage({type:"ERROR",errorType:r,errorArgs:s,errorTb:i})};async function B(t){return await j.getItem(t)}function D(){Sk.configure({output(t){return self.postMessage({type:"OUT",message:t})},yieldLimit:300,syspath:["app"],read(t){let e=O.get(t);return e!==void 0?e:Sk.misceval.promiseToSuspension(B(t).then(n=>n!=null?n:C(t).then(r=>(j.setItem(t,r!=null?r:0),r))).then(n=>{if(n==null||n===0)throw"No module named "+t;return n}))}}),Sk.builtins.self=Sk.ffi.proxy(self),R.resolve(!0)}function F(t){let{data:e}=t;if(e.type==="MODULE"){let{id:n,content:r}=e,s=k.get(n);if(s===void 0)return;let{resolve:i}=s;k.delete(n),i(r)}}self.onunhandledrejection=t=>{S(t.reason)};self.addEventListener("message",F);var a=null;function L(){a!=null||(a=d())}var E="sync"in self.registration,u=(...t)=>{},_=class{constructor(e,n){this.tag=e;this.onSync=n;g(this,"_requestsAddedDuringSync",!1);g(this,"_syncInProgress",!1);g(this,"_fallbackRegistered",!1);_._instances.set(e,this),this._addSyncListener();let r=_._initSyncs.get(this.tag);r&&this._syncListener(...r),E||this._registerFallback()}_registerFallback(){this._fallbackRegistered||(this._fallbackRegistered=!0,self.addEventListener("online",()=>{this.onSync()}))}async _fallbackSync(){self.navigator.onLine&&this.onSync()}async registerSync(){if(!E)return u("BG SYNC not supported calling early"),this._fallbackSync();try{u("registering sync with tag",this.tag),await self.registration.sync.register(this.tag)}catch(e){if(e.message.startsWith("Permission denied"))this._registerFallback(),this._fallbackSync();else throw e}}async _syncListener(e,n){var s;u("sync listener",e),this._syncInProgress=!0,n.$handled=!0,_._initSyncs.delete(this.tag),await((s=a)==null?void 0:s.promise);let r;try{await this.onSync()}catch(i){i instanceof Error&&(r=i,n.reject(r))}finally{this._requestsAddedDuringSync&&!(r&&!e.lastChance)&&await this.registerSync(),this._syncInProgress=!1,this._requestsAddedDuringSync=!1,n.resolve(null)}}_addSyncListener(){if(!E)return this._fallbackSync();self.addEventListener("sync",e=>{if(u("sync event handler called",e),e.tag===this.tag){u("sync listener fired",e);let n=d();this._syncListener(e,n),e.waitUntil(n.promise)}}),u("SYNC LISTENER ADDED")}static async register(e){var r;u("registering sync",e),await((r=a)==null?void 0:r.promise);let n=this._instances.get(e);if(!n)throw new Error("No Background sync with this name has been created");n.registerSync(),u("sync registered for",n.tag)}},y=_;g(y,"_initSyncs",new Map),g(y,"_instances",new Map);self.window=self;self.anvilAppOrigin="";async function T(t){L(),a.promise.then(()=>w({type:"READY"})),await v.setItem("__main__",t);try{await J(()=>V(t,!1,!0)),a.resolve(!0)}catch(e){console.error(e),S(e),a.reject(e)}}var{builtin:{func:G},misceval:{asyncToPromise:J},importMain:V}=Sk;D();H();function W(t){return new Promise(e=>setTimeout(e,t))}var h=0;function H(){function t(e,n=[]){if(e.length!==1)throw new Sk.builtin.TypeError("Expected one arg to raise_event");let r={};for(let s=0;s<n.length;s+=2){let i=n[s],o=n[s+1];r[i]=Sk.ffi.toJs(o)}N(e[0].toString(),r)}t.co_fastcall=!0,self.raise_event=new G(t),self.BackgroundSync=y,self.sync_event_handler=e=>n=>{let r=async()=>{var s;await((s=a)==null?void 0:s.promise);try{let i=await e(n);return h=0,i}catch(i){if(h<5&&String(i).toLowerCase().includes("failed to fetch"))return h++,w({type:"OUT",message:`It looks like we're offline re-registering sync: '${n.tag}'
`}),await W(500),self.registration.sync.register(n.tag);h=0,S(i)}};n.waitUntil(r())}}var v=localforage.createInstance({name:"anvil-labs-sw",storeName:"locals"});async function Y(t){let e=t.data,{type:n}=e;if(n!=="INIT")return;let{name:r}=e;await T(r)}self.addEventListener("message",Y);self.addEventListener("activate",t=>{console.log("%cSW ACTIVATED","color: hotpink;")});async function q(t){let e=t.data,{type:n}=e;if(n!=="APPORIGIN")return;let{origin:r}=e;self.anvilAppOrigin=r,await v.setItem("apporigin",r)}self.addEventListener("message",q);function K(t){let e=t.data,{type:n}=e;if(n!=="SYNC")return;let{tag:r}=e;y.register(r)}self.addEventListener("message",K);async function w(t){t.ANVIL_LABS=!0;let e=await self.clients.matchAll({includeUncontrolled:!0,type:"window"});for(let n of e)n.postMessage(t)}self.postMessage=w;function N(t,e={}){e.event_name=t,w({type:"EVENT",name:t,kws:e})}function I(t,e){var r;let{get:n}=(r=Object.getOwnPropertyDescriptor(self,t))!=null?r:{};delete self[t],Object.defineProperty(self,t,{get:n,set:e,configurable:!0})}function P(t){var i;let e="on"+t,{set:n}=(i=Object.getOwnPropertyDescriptor(self,e))!=null?i:{},r=[],s=[];self[e]=o=>{r.push(o);let c=d();s.push(c),y._initSyncs.set(o.tag,[o,c]),Q(),setTimeout(()=>{c.$handled||c.resolve(null)},5e3),o.waitUntil(c.promise)},I(e,async o=>{var p;I(e,n),self[e]=o;let c=r.pop(),m=s.pop();if(!(!c||!m))try{await((p=a)==null?void 0:p.promise),await o(c),m.resolve(null)}catch(b){m.reject(b)}}),self.addEventListener(t,o=>{N(t,{tag:o.tag})})}P("sync");P("periodicsync");async function Q(){let t=await v.getItem("apporigin");if(self.anvilAppOrigin=t!=null?t:"",a)return a.promise;let e=await v.getItem("__main__");e&&await T(e)}console.log("%cRUNNING SW SCRIPT","color: green;");
