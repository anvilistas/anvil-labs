# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{function b(e){let{builtin:{BaseException:t},ffi:{toJs:r}}=Sk;function s(){let o={resolve:()=>{},reject:()=>{}};return o.promise=new Promise((i,l)=>{o.resolve=i,o.reject=l}),o}let a={};e.registerFn=(o,i)=>{a[o]=i},e.moduleLoaded=s();function n(){e.task_state=new Proxy({},{set(o,i,l){return o[i]===l||(o[i]=l,e.postMessage({type:"STATE",state:{...o}})),!0}})}let c=new Map;e.fetchModule=o=>{let i=crypto.randomUUID();e.postMessage({type:"IMPORT",id:i,filename:o});let l=s();return c.set(i,l),l.promise},e.onmessage=async o=>{let{data:i}=o;switch(i.type){case"CALL":{await e.moduleLoaded.promise,n();let{id:l,fn:d,args:p,kws:h}=i;console.debug(`RPC call ${l}:`,d,p);let k=a[d],_,m,u,y;if(e.currentTask={id:l,fn:d},!k)m="RuntimeError",u=[`No handler registered for '${i.fn}'`];else try{_=await k(p,h)}catch(f){f instanceof t?(u=r(f.args),m=f.tp$name,y=f.traceback):(m=f.constructor?.name??"<unknown>",u=f.message?[f.message]:[])}e.currentTask=null;try{stopExecution=!1,e.postMessage({type:"RESPONSE",id:i.id,value:_,errorType:m,errorArgs:u,errorTb:y})}catch(f){console.error(f,"Failed to post RPC response:",_,f)}break}case"KILL":stopExecution||(stopExecution=!0);break;case"MODULE":{let{id:l,content:d}=i,{resolve:p}=c.get(l);c.delete(l),p(d)}}}}function T(){let{ffi:{proxy:e,toPy:t},abstr:{setUpModuleMethods:r,objectSetItem:s},misceval:{promiseToSuspension:a,chain:n}}=Sk,c={__name__:t("js"),window:e(self)};async function o(i){let l=await new Function("return import("+JSON.stringify(i.toString())+")").call(null);return e(l)}return r("js",c,{await_promise:{$meth(i){let l=i.valueOf();return l instanceof Promise||l&&l.then&&typeof l.then=="function"?n(a(l),d=>t(d,{dictHook:p=>e(p)})):i},$flags:{OneArg:!0}},import_from:{$meth(i){return a(o(i))},$flags:{OneArg:!0}}}),s(Sk.sysmodules,t("anvil.js.window"),c.window),c}function D(){let{ffi:{toPy:e,toJs:t},abstr:{setUpModuleMethods:r}}=Sk,s={__name__:new e("json")};return r("js",s,{dumps:{$meth(a){return new e(JSON.stringify(t(a)))},$flags:{OneArg:!0}},loads:{$meth(a){return e(JSON.parse(a.toString()))},$flags:{OneArg:!0}}}),s}function P(){let e=document.getElementsByTagName("script");return Array.from(e).find(t=>t.src?.includes("skulpt.min.js")).src}function C(){Sk.configure({output(e){return self.postMessage({type:"OUT",message:e})},yieldLimit:300,syspath:["app"],read(e){let t=self.anvilFiles[e];return t!==void 0?t:Sk.misceval.promiseToSuspension(self.fetchModule(e).then(r=>{if(r==null)throw"No module named "+e;return r}))}})}function M(){let{builtin:{RuntimeError:e},ffi:{toJs:t,toPy:r},misceval:{tryCatch:s,chain:a,Suspension:n,asyncToPromise:c,buildClass:o,callsimArray:i}}=Sk;Sk.builtins.self=Sk.builtins.worker=r(self);let l=o({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[e]),d=Sk.sysmodules.quick$lookup(r("__main__")).$d;for(let[p,h]of Object.entries(d))h.tp$call&&self.registerFn(p,(k,_)=>{k=k.map(u=>r(u)),_=Object.entries(_).map(([u,y])=>[u,r(y)]).flat();let m=s(()=>a(h.tp$call(k,_),u=>t(u)),u=>{throw u});return m instanceof n?c(()=>m,{"*":()=>{if(stopExecution){let{id:u,fn:y}=self.currentTask;throw i(l,[`<WorkerTask '${y}' (${u})> Killed`])}}}):m})}var $=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${P()}\\']);
(${b})(self);
const $f = (self.anvilFiles = {});
$f["src/lib/json.js"] = \`var $builtinmodule=${D};\`;
$f["src/lib/anvil/__init__.py"] = "def is_server_side():return False";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${T};\`;
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
(${C})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${M})();
})
`;function O(){let e={resolve:()=>{},reject:()=>{}};return e.promise=new Promise((t,r)=>{e.resolve=t,e.reject=r}),e}var{misceval:{callsimArray:W,buildClass:E},ffi:{toPy:R},builtin:{RuntimeError:S,str:A,print:j}}=Sk,v=E({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[S]);function x(e,t,r){let s;if(e==="WorkerTaskKilled")return s=W(v,t),s.traceback=r,s;try{let a=Sk.builtin[e];s=W(a,t.map(n=>R(n))),s.traceback=r??[]}catch{let a;try{a=new window[e](...t)}catch{a=new Error(...t)}s=new Sk.builtin.ExternalError(a)}return s}function L(e){let t={};e.currentTask=null,e.stateHandler=()=>{},e.launchTask=(r,s,a)=>{let n=crypto.randomUUID();return e.currentTask={fn:r,id:n},e.postMessage({type:"CALL",id:n,fn:r,args:s,kws:a}),t[n]=O(),[n,r,new Promise(c=>c(t[n].promise))]},e.onmessage=async({data:r})=>{switch(r.type){case"OUT":{let{id:s,fn:a}=e.currentTask??{};j([`<worker-task '${a}' (${s})>:`,r.message],["end",A.$empty]);break}case"STATE":{e.stateHandler({...r.state});break}case"RESPONSE":{let{id:s,value:a,errorType:n,errorArgs:c,errorTb:o}=r,i=t[r.id];i?n?(console.debug(`RPC error response ${s}:`,n,c),i.reject(x(n,c,o))):(console.debug(`RPC response ${s}:`,a),i.resolve(a)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete t[r.id],e.currentTask=null;return}case"IMPORT":{let{id:s,filename:a}=r,n=null;try{n=Sk.read(a),typeof n!="string"&&(n=await Sk.misceval.asyncToPromise(()=>n))}catch{if(a.startsWith("app/")){let[c,o,i]=a.split("/");i==="__init__.py"&&o!=="anvil"&&(n="pass")}else n=null}e.postMessage({type:"MODULE",id:s,content:n})}}}}var w=class{constructor(t,r,s,a){this._id=t;this._name=r;this._result=s;this._target=a;this._startTime=Date.now(),this._handledResult=s,this._target.stateHandler=this._updateState.bind(this),this._result.then(n=>{this._complete=!0,this._status="completed",this._rv=n},n=>{this._complete=!0,n instanceof v?(this._status="killed",this._err=new S("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=n)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(t){this._state=t,this._stateHandler(t)}await_result(){return this._result}on_result(t,r){this._handledResult=this._result.then(t),r&&(this._handledResult=this._handledResult.catch(r))}on_error(t){this._handledResult=this._handledResult.catch(t)}on_state_change(t){this._stateHandler=t}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},g=class{target;constructor(t){t.startsWith(window.anvilAppMainPackage)||(t=window.anvilAppMainPackage+"."+t);let r=$.replace("{$filename$}",JSON.stringify(t)).replace("self.anvilAppOrigin",JSON.stringify(window.anvilAppOrigin)),s=new Blob([r],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(s)),L(this.target)}launch_task(t,r,s){if(this.target.currentTask!==null)throw new S("BackgroundWorker already has an active task");let[n,c,o]=this.target.launchTask(t,r,s);return new w(n,c,o,this.target)}};window.anvilLabs??={};window.anvilLabs.Worker=g;window.anvilLabs.WorkerTaskKilled=v;})();
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
