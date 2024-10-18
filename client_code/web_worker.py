# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{var O=Object.defineProperty;var R=(e,t,r)=>t in e?O(e,t,{enumerable:!0,configurable:!0,writable:!0,value:r}):e[t]=r;var _=(e,t,r)=>(R(e,typeof t!="symbol"?t+"":t,r),r);function $(e){let{builtin:{BaseException:t},ffi:{toJs:r}}=Sk;function n(){let i={resolve:()=>{},reject:()=>{}};return i.promise=new Promise((l,c)=>{i.resolve=l,i.reject=c}),i}let a={};e.registerFn=(i,l)=>{a[i]=l},e.moduleLoaded=n();function s(){e.task_state=new Proxy({},{set(i,l,c){return i[l]===c||(i[l]=c,e.postMessage({type:"STATE",state:{...i}})),!0}})}let o=new Map;e.fetchModule=i=>{let l=Math.random().toString(36).substring(6);e.postMessage({type:"IMPORT",id:l,filename:i});let c=n();return o.set(l,c),c.promise},e.onmessage=async i=>{var c,y;let{data:l}=i;switch(l.type){case"CALL":{await e.moduleLoaded.promise,s();let{id:d,fn:u,args:f,kws:h}=l;console.debug(`RPC call ${d}:`,u,f);let g=a[u],p,k,w,D;if(e.currentTask={id:d,fn:u},!g)k="RuntimeError",w=[`No handler registered for '${l.fn}'`];else try{p=await g(f,h)}catch(m){m instanceof t?(w=r(m.args),k=m.tp$name,D=m.traceback):(k=(y=(c=m.constructor)==null?void 0:c.name)!=null?y:"<unknown>",w=m.message?[m.message]:[])}e.currentTask=null;try{stopExecution=!1,e.postMessage({type:"RESPONSE",id:l.id,value:p,errorType:k,errorArgs:w,errorTb:D})}catch(m){console.error(m,"Failed to post RPC response:",p,m)}break}case"KILL":stopExecution||(stopExecution=!0);break;case"MODULE":{let{id:d,content:u}=l,{resolve:f}=o.get(d);o.delete(d),f(u)}}}}function W(){let{ffi:{proxy:e,toPy:t},abstr:{setUpModuleMethods:r,objectSetItem:n},misceval:{promiseToSuspension:a,chain:s},builtin:{func:o,ExternalError:i,property:l}}=Sk,c={__name__:t("js"),window:e(self),ExternalError:i};async function y(d){let u=await new Function("return import("+JSON.stringify(d.toString())+")").call(null);return e(u)}return r("js",c,{await_promise:{$meth(d){let u=d.valueOf();return u instanceof Promise||u&&u.then&&typeof u.then=="function"?s(a(u),f=>t(f,{dictHook:h=>e(h)})):d},$flags:{OneArg:!0}},import_from:{$meth(d){return a(y(d))},$flags:{OneArg:!0}}}),n(Sk.sysmodules,t("anvil.js.window"),c.window),c.ExternalError.prototype.original_error=new l(new o(d=>t(d.nativeError,{dictHook:u=>e(u)}))),c}function P(){let{ffi:{toPy:e,toJs:t},abstr:{setUpModuleMethods:r}}=Sk,n={__name__:new e("json")};return r("js",n,{dumps:{$meth(a){return new e(JSON.stringify(t(a)))},$flags:{OneArg:!0}},loads:{$meth(a){return e(JSON.parse(a.toString()))},$flags:{OneArg:!0}}}),n}function A(){let e=document.getElementsByTagName("script");return Array.from(e).find(t=>{var r;return(r=t.src)==null?void 0:r.includes("skulpt.min.js")}).src}function x(){Sk.configure({output(e){return self.postMessage({type:"OUT",message:e})},yieldLimit:300,syspath:["app"],read(e){let t=self.anvilFiles[e];return t!==void 0?t:Sk.misceval.promiseToSuspension(self.fetchModule(e).then(r=>{if(r==null)throw"No module named "+e;return r}))}})}function j(){let{builtin:{RuntimeError:e},ffi:{toJs:t,toPy:r},misceval:{tryCatch:n,chain:a,Suspension:s,asyncToPromise:o,buildClass:i,callsimArray:l}}=Sk;Sk.builtins.self=Sk.builtins.worker=r(self);let c=i({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[e]),y=Sk.sysmodules.quick$lookup(r("__main__")).$d;for(let[d,u]of Object.entries(y))u.tp$call&&self.registerFn(d,(f,h)=>{f=f.map(p=>r(p)),h=Object.entries(h).map(([p,k])=>[p,r(k)]).flat();let g=n(()=>a(u.tp$call(f,h),p=>t(p)),p=>{throw p});return g instanceof s?o(()=>g,{"*":()=>{if(stopExecution){let{id:p,fn:k}=self.currentTask;throw l(c,[`<WorkerTask '${k}' (${p})> Killed`])}}}):g})}var M=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${A()}\\']);
(${$})(self);
const $f = (self.anvilFiles = {});
$f["src/lib/json.js"] = \`var $builtinmodule=${P};\`;
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
(${x})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${j})();
})
`;function L(){let e={resolve:()=>{},reject:()=>{}};return e.promise=new Promise((t,r)=>{e.resolve=t,e.reject=r}),e}var{misceval:{callsimArray:E,buildClass:H},ffi:{toPy:K},builtin:{RuntimeError:T,str:I,print:N}}=Sk,S=H({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[T]);function z(e,t,r){let n;if(e==="WorkerTaskKilled")return n=E(S,t),n.traceback=r,n;try{let a=Sk.builtin[e];n=E(a,t.map(s=>K(s))),n.traceback=r!=null?r:[]}catch{let a;try{a=new window[e](...t)}catch{a=new Error(...t)}n=new Sk.builtin.ExternalError(a)}return n}function F(e){let t={};e.currentTask=null,e.stateHandler=()=>{},e.launchTask=(r,n,a)=>{let s=Math.random().toString(36).substring(6);return e.currentTask={fn:r,id:s},e.postMessage({type:"CALL",id:s,fn:r,args:n,kws:a}),t[s]=L(),[s,r,new Promise(o=>o(t[s].promise))]},e.onmessage=async({data:r})=>{var n;switch(r.type){case"OUT":{let{id:a,fn:s}=(n=e.currentTask)!=null?n:{};N([`<worker-task '${s}' (${a})>:`,r.message],["end",I.$empty]);break}case"STATE":{e.stateHandler({...r.state});break}case"RESPONSE":{let{id:a,value:s,errorType:o,errorArgs:i,errorTb:l}=r,c=t[r.id];c?o?(console.debug(`RPC error response ${a}:`,o,i),c.reject(z(o,i,l))):(console.debug(`RPC response ${a}:`,s),c.resolve(s)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete t[r.id],e.currentTask=null;return}case"IMPORT":{let{id:a,filename:s}=r,o=null;try{o=Sk.read(s),typeof o!="string"&&(o=await Sk.misceval.asyncToPromise(()=>o))}catch{if(s.startsWith("app/")){let[i,l,c]=s.split("/");c==="__init__.py"&&l!=="anvil"&&(o="pass")}else o=null}e.postMessage({type:"MODULE",id:a,content:o})}}}}var b=class{constructor(t,r,n,a){this._id=t;this._name=r;this._result=n;this._target=a;_(this,"_handledResult");_(this,"_startTime");_(this,"_state",{});_(this,"_rv",null);_(this,"_err",null);_(this,"_complete",!1);_(this,"_status",null);_(this,"_stateHandler",()=>{});this._startTime=Date.now(),this._handledResult=n,this._target.stateHandler=this._updateState.bind(this),this._result.then(s=>{this._complete=!0,this._status="completed",this._rv=s},s=>{this._complete=!0,s instanceof S?(this._status="killed",this._err=new T("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=s)})}_updateState(t){this._state=t,this._stateHandler(t)}await_result(){return this._result}on_result(t,r){this._handledResult=this._result.then(t),r&&(this._handledResult=this._handledResult.catch(r))}on_error(t){this._handledResult=this._handledResult.catch(t)}on_state_change(t){this._stateHandler=t}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},v=class{constructor(t){_(this,"target");t.startsWith(window.anvilAppMainPackage)||(t=window.anvilAppMainPackage+"."+t);let r=M.replace("{$filename$}",JSON.stringify(t)).replace("self.anvilAppOrigin",JSON.stringify(window.anvilAppOrigin)),n=new Blob([r],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(n)),F(this.target)}launch_task(t,r,n){if(this.target.currentTask!==null)throw new T("BackgroundWorker already has an active task");let[s,o,i]=this.target.launchTask(t,r,n);return new b(s,o,i,this.target)}};var C;(C=window.anvilLabs)!=null||(window.anvilLabs={});window.anvilLabs.Worker=v;window.anvilLabs.WorkerTaskKilled=S;})();
"""  # noqa: E501

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
