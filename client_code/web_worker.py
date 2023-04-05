# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{var E=Object.defineProperty;var R=(e,t,r)=>t in e?E(e,t,{enumerable:!0,configurable:!0,writable:!0,value:r}):e[t]=r;var f=(e,t,r)=>(R(e,typeof t!="symbol"?t+"":t,r),r);function $(e){let{builtin:{BaseException:t},ffi:{toJs:r}}=Sk;function n(){let c={resolve:()=>{},reject:()=>{}};return c.promise=new Promise((i,o)=>{c.resolve=i,c.reject=o}),c}let a={};e.registerFn=(c,i)=>{a[c]=i},e.moduleLoaded=n();function s(){e.task_state=new Proxy({},{set(c,i,o){return c[i]===o||(c[i]=o,e.postMessage({type:"STATE",state:{...c}})),!0}})}let l=new Map;e.fetchModule=c=>{let i=Math.random().toString(36).substring(6);e.postMessage({type:"IMPORT",id:i,filename:c});let o=n();return l.set(i,o),o.promise},e.onmessage=async c=>{var o,y;let{data:i}=c;switch(i.type){case"CALL":{await e.moduleLoaded.promise,s();let{id:p,fn:m,args:_,kws:g}=i;console.debug(`RPC call ${p}:`,m,_);let h=a[m],u,k,v,D;if(e.currentTask={id:p,fn:m},!h)k="RuntimeError",v=[`No handler registered for '${i.fn}'`];else try{u=await h(_,g)}catch(d){d instanceof t?(v=r(d.args),k=d.tp$name,D=d.traceback):(k=(y=(o=d.constructor)==null?void 0:o.name)!=null?y:"<unknown>",v=d.message?[d.message]:[])}e.currentTask=null;try{stopExecution=!1,e.postMessage({type:"RESPONSE",id:i.id,value:u,errorType:k,errorArgs:v,errorTb:D})}catch(d){console.error(d,"Failed to post RPC response:",u,d)}break}case"KILL":stopExecution||(stopExecution=!0);break;case"MODULE":{let{id:p,content:m}=i,{resolve:_}=l.get(p);l.delete(p),_(m)}}}}function W(){let{ffi:{proxy:e,toPy:t},abstr:{setUpModuleMethods:r,objectSetItem:n},misceval:{promiseToSuspension:a,chain:s}}=Sk,l={__name__:t("js"),window:e(self)};async function c(i){let o=await new Function("return import("+JSON.stringify(i.toString())+")").call(null);return e(o)}return r("js",l,{await_promise:{$meth(i){let o=i.valueOf();return o instanceof Promise||o&&o.then&&typeof o.then=="function"?s(a(o),y=>t(y,{dictHook:p=>e(p)})):i},$flags:{OneArg:!0}},import_from:{$meth(i){return a(c(i))},$flags:{OneArg:!0}}}),n(Sk.sysmodules,t("anvil.js.window"),l.window),l}function M(){let{ffi:{toPy:e,toJs:t},abstr:{setUpModuleMethods:r}}=Sk,n={__name__:new e("json")};return r("js",n,{dumps:{$meth(a){return new e(JSON.stringify(t(a)))},$flags:{OneArg:!0}},loads:{$meth(a){return e(JSON.parse(a.toString()))},$flags:{OneArg:!0}}}),n}function A(){let e=document.getElementsByTagName("script");return Array.from(e).find(t=>{var r;return(r=t.src)==null?void 0:r.includes("skulpt.min.js")}).src}function j(){Sk.configure({output(e){return self.postMessage({type:"OUT",message:e})},yieldLimit:300,syspath:["app"],read(e){let t=self.anvilFiles[e];return t!==void 0?t:Sk.misceval.promiseToSuspension(self.fetchModule(e).then(r=>{if(r==null)throw"No module named "+e;return r}))}})}function x(){let{builtin:{RuntimeError:e},ffi:{toJs:t,toPy:r},misceval:{tryCatch:n,chain:a,Suspension:s,asyncToPromise:l,buildClass:c,callsimArray:i}}=Sk;Sk.builtins.self=Sk.builtins.worker=r(self);let o=c({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[e]),y=Sk.sysmodules.quick$lookup(r("__main__")).$d;for(let[p,m]of Object.entries(y))m.tp$call&&self.registerFn(p,(_,g)=>{_=_.map(u=>r(u)),g=Object.entries(g).map(([u,k])=>[u,r(k)]).flat();let h=n(()=>a(m.tp$call(_,g),u=>t(u)),u=>{throw u});return h instanceof s?l(()=>h,{"*":()=>{if(stopExecution){let{id:u,fn:k}=self.currentTask;throw i(o,[`<WorkerTask '${k}' (${u})> Killed`])}}}):h})}var P=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${A()}\\']);
(${$})(self);
const $f = (self.anvilFiles = {});
$f["src/lib/json.js"] = \`var $builtinmodule=${M};\`;
$f["src/lib/anvil/__init__.py"] = "def is_server_side():return False";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${W};\`;
$f["src/lib/anvil/tz.py"] = \`import datetime,time
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
UTC=tzutc()\`;
$f["src/lib/anvil/server.py"] = \`class SerializationError(Exception):0
def get_app_origin():return self.anvilAppOrigin
def get_api_origin():return get_app_origin()+'/_/api'
def call(*args,**kws):
  from anvil_labs.kompot import preserve,reconstruct,serialize;name,*args=args;rv=self.fetch(get_api_origin()+f"/anvil_labs_private_call?name={name}",{'headers':{'Content-Type':'application/json'},'method':'POST','body':self.JSON.stringify(preserve([args,kws]))});result,error=rv.json()
  if error:raise Exception(error)
  return reconstruct(dict(result))
def portable_class(cls,name=None):
  if name is None and isinstance(cls,str):name=cls;return lambda cls:cls
  else:return cls\`;
(${j})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${x})();
})
`;function L(){let e={resolve:()=>{},reject:()=>{}};return e.promise=new Promise((t,r)=>{e.resolve=t,e.reject=r}),e}var{misceval:{callsimArray:C,buildClass:H},ffi:{toPy:K},builtin:{RuntimeError:T,str:I,print:N}}=Sk,S=H({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[T]);function z(e,t,r){let n;if(e==="WorkerTaskKilled")return n=C(S,t),n.traceback=r,n;try{let a=Sk.builtin[e];n=C(a,t.map(s=>K(s))),n.traceback=r!=null?r:[]}catch{let a;try{a=new window[e](...t)}catch{a=new Error(...t)}n=new Sk.builtin.ExternalError(a)}return n}function F(e){let t={};e.currentTask=null,e.stateHandler=()=>{},e.launchTask=(r,n,a)=>{let s=Math.random().toString(36).substring(6);return e.currentTask={fn:r,id:s},e.postMessage({type:"CALL",id:s,fn:r,args:n,kws:a}),t[s]=L(),[s,r,new Promise(l=>l(t[s].promise))]},e.onmessage=async({data:r})=>{var n;switch(r.type){case"OUT":{let{id:a,fn:s}=(n=e.currentTask)!=null?n:{};N([`<worker-task '${s}' (${a})>:`,r.message],["end",I.$empty]);break}case"STATE":{e.stateHandler({...r.state});break}case"RESPONSE":{let{id:a,value:s,errorType:l,errorArgs:c,errorTb:i}=r,o=t[r.id];o?l?(console.debug(`RPC error response ${a}:`,l,c),o.reject(z(l,c,i))):(console.debug(`RPC response ${a}:`,s),o.resolve(s)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete t[r.id],e.currentTask=null;return}case"IMPORT":{let{id:a,filename:s}=r,l=null;try{l=Sk.read(s),typeof l!="string"&&(l=await Sk.misceval.asyncToPromise(()=>l))}catch{if(s.startsWith("app/")){let[c,i,o]=s.split("/");o==="__init__.py"&&i!=="anvil"&&(l="pass")}else l=null}e.postMessage({type:"MODULE",id:a,content:l})}}}}var b=class{constructor(t,r,n,a){this._id=t;this._name=r;this._result=n;this._target=a;f(this,"_handledResult");f(this,"_startTime");f(this,"_state",{});f(this,"_rv",null);f(this,"_err",null);f(this,"_complete",!1);f(this,"_status",null);f(this,"_stateHandler",()=>{});this._startTime=Date.now(),this._handledResult=n,this._target.stateHandler=this._updateState.bind(this),this._result.then(s=>{this._complete=!0,this._status="completed",this._rv=s},s=>{this._complete=!0,s instanceof S?(this._status="killed",this._err=new T("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=s)})}_updateState(t){this._state=t,this._stateHandler(t)}await_result(){return this._result}on_result(t,r){this._handledResult=this._result.then(t),r&&(this._handledResult=this._handledResult.catch(r))}on_error(t){this._handledResult=this._handledResult.catch(t)}on_state_change(t){this._stateHandler=t}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},w=class{constructor(t){f(this,"target");t.startsWith(window.anvilAppMainPackage)||(t=window.anvilAppMainPackage+"."+t);let r=P.replace("{$filename$}",JSON.stringify(t)).replace("self.anvilAppOrigin",JSON.stringify(window.anvilAppOrigin)),n=new Blob([r],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(n)),F(this.target)}launch_task(t,r,n){if(this.target.currentTask!==null)throw new T("BackgroundWorker already has an active task");let[s,l,c]=this.target.launchTask(t,r,n);return new b(s,l,c,this.target)}};var O;(O=window.anvilLabs)!=null||(window.anvilLabs={});window.anvilLabs.Worker=w;window.anvilLabs.WorkerTaskKilled=S;})();
"""

_blob = _W.Blob([_script], {type: "text/javascript"})
_src = _W.URL.createObjectURL(_blob)
_s = _W.document.createElement("script")
_s.src = _src
_s.type = "text/javascript"
_W.document.body.appendChild(_s)


def _load(res, rej):
    _s.onload = res
    _s.onerror = rej


_p = _W.Promise(_load)
anvil.js.await_promise(_p)

_Worker = _W.anvilLabs.Worker
WorkerTaskKilled = _W.anvilLabs.WorkerTaskKilled


class WorkerTask:
    def __init__(self, task):
        self._task = task

    def await_result(self):
        return self._task.await_result()

    def on_result(self, resolve=None, reject=None):
        return self._task.on_result(resolve, reject)

    def on_error(self, reject):
        return self._task.on_error(reject)

    def on_state_change(self, handler):
        return self._task.on_state_change(handler)

    def get_state(self):
        return self._task.get_state()

    def get_id(self):
        return self._task.get_id()

    def get_task_name(self):
        return self._task.get_task_name()

    def get_termination_status(self):
        return self._task.get_termination_status(self)

    def get_return_value(self):
        return self._task.get_return_value()

    def get_error(self):
        return self._task.get_error()

    def get_start_time(self):
        return datetime.fromtimestamp(self._task.get_start_time() / 1000)

    def is_completed(self):
        return self._task.is_completed()

    def is_running(self):
        return self._task.is_running()

    def kill(self):
        return self._task.kill()

    def __repr__(self):
        return f"<WorkerTask {self._task._name!r} ({self._task._id})>"


class Worker:
    def __init__(self, module):
        self._worker = _Worker(module)

    def launch_task(self, fn, *args, **kws):
        task = self._worker.launch_task(fn, args, kws)
        return WorkerTask(task)
