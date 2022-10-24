# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W
import anvil.server

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{function v(t){let{builtin:{BaseException:e},ffi:{toJs:r}}=Sk;function s(){let i={resolve:()=>{},reject:()=>{}};return i.promise=new Promise((a,o)=>{i.resolve=a,i.reject=o}),i}let l={};t.registerFn=(i,a)=>{l[i]=a},t.moduleLoaded=s();function n(){t.task_state=new Proxy({},{set(i,a,o){return i[a]===o||(i[a]=o,t.postMessage({type:"STATE",state:{...i}})),!0}})}t.onmessage=async i=>{let{data:a}=i;switch(a.type){case"CALL":{await t.moduleLoaded.promise,n();let{id:o,fn:c,args:k,kws:g}=a;console.debug(`RPC call ${o}:`,c,k);let _=l[c],p,d,f,m;if(t.currentTask={id:o,fn:c},!_)d="RuntimeError",f=[`No handler registered for '${a.fn}'`];else try{p=await _(k,g)}catch(u){u instanceof e?(f=r(u.args),d=u.tp$name,m=u.traceback):(d=u.constructor??"<unknown>",f=[u.message])}t.currentTask=null;try{stopExecution=!1,t.postMessage({type:"RESPONSE",id:a.id,value:p,errorType:d,errorArgs:f,errorTb:m})}catch(u){console.error(u,"Failed to post RPC response:",p,u)}break}case"KILL":stopExecution||(stopExecution=!0);break}}}function T(){let{ffi:{proxy:t,toPy:e},abstr:{setUpModuleMethods:r},misceval:{promiseToSuspension:s,chain:l}}=Sk,n={__name__:e("js"),window:t(self)};async function i(a){let o=await new Function("return import("+JSON.stringify(a.toString())+")").call(null);return t(o)}return r("js",n,{await_promise:{$meth(a){let o=a.valueOf();return o instanceof Promise||o&&o.then&&typeof o.then=="function"?l(s(o),c=>e(c,{dictHook:k=>t(k)})):a},$flags:{OneArg:!0}},import_from:{$meth(a){return s(i(a))},$flags:{OneArg:!0}}}),n}function $(){let{abstr:{setUpModuleMethods:t},ffi:{toPy:e}}=Sk,r={__name__:e("server")};return t("server",r,{get_api_origin:{$meth(){return e(self.anvilLabsEndpoint)},$flags:{NoArgs:!0}}}),r}function C(){let t=document.getElementsByTagName("script");return Array.from(t).find(e=>e.src?.includes("skulpt.min.js")).src}function D(){Sk.configure({output(t){return self.postMessage({type:"OUT",message:t})},yieldLimit:300,syspath:["app"]})}function R(){let{builtin:{RuntimeError:t,str:e},ffi:{toJs:r,toPy:s},misceval:{tryCatch:l,chain:n,Suspension:i,asyncToPromise:a,buildClass:o,callsimArray:c}}=Sk;Sk.builtins.self=s(self);let k=o({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[t]),g=Sk.sysmodules.quick$lookup(new e("__main__")).$d;for(let[_,p]of Object.entries(g))p.tp$call&&self.registerFn(_,(d,f)=>{d=d.map(u=>s(u)),f=Object.entries(f).map(([u,S])=>[u,s(S)]).flat();let m=l(()=>n(p.tp$call(d,f),u=>r(u)),u=>{throw u});return m instanceof i?a(()=>m,{"*":()=>{if(stopExecution){let{id:u,fn:S}=self.currentTask;throw c(k,[`<WorkerTask '${S}' (${u})> Killed`])}}}):m})}var W=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${C()}\\']);
self.anvilLabsEndpoint={$endpoints$};
(${v})(self);
Sk.builtinFiles = JSON.parse({$files$});
Sk.builtins.worker = Sk.ffi.toPy(self);
const $f = Sk.builtinFiles.files;
$f["src/lib/anvil/__init__.py"] = "";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${T};\`;
$f["src/lib/anvil/server.js"] = \`var $builtinmodule=${$};\`;
(${D})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${R})();
})
`;function E(){let t={resolve:()=>{},reject:()=>{}};return t.promise=new Promise((e,r)=>{t.resolve=e,t.reject=r}),t}var{misceval:{callsimArray:P,buildClass:O},ffi:{toPy:x},builtin:{RuntimeError:w,str:L,print:j}}=Sk,y=O({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[w]);function A(t,e,r){let s;if(t==="WorkerTaskKilled")return s=P(y,e),s.traceback=r,s;try{let l=Sk.builtins[t];s=P(l,e.map(n=>x(n))),s.traceback=r??[]}catch{s=new Error(...e)}return s}function H(t){let e={};t.currentTask=null,t.stateHandler=()=>{},t.launchTask=(r,s,l)=>{let n=crypto.randomUUID();return t.currentTask={fn:r,id:n},t.postMessage({type:"CALL",id:n,fn:r,args:s,kws:l}),e[n]=E(),[n,r,new Promise(i=>i(e[n].promise))]},t.onmessage=({data:r})=>{switch(r.type){case"OUT":{let{id:s,fn:l}=t.currentTask??{};j([`<worker-task '${l}' (${s})>:`,r.message],["end",L.$empty]);break}case"STATE":{t.stateHandler({...r.state});break}case"RESPONSE":{let{id:s,value:l,errorType:n,errorArgs:i,errorTb:a}=r,o=e[r.id];o?n?(console.debug(`RPC error response ${s}:`,n,i),o.reject(A(n,i,a))):(console.debug(`RPC response ${s}:`,l),o.resolve(l)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete e[r.id],t.currentTask=null}}}}var b=class{constructor(e,r,s,l){this._id=e;this._name=r;this._result=s;this._target=l;this._startTime=Date.now(),this._handledResult=s,this._target.stateHandler=this._updateState.bind(this),this._result.then(n=>{this._complete=!0,this._status="completed",this._rv=n},n=>{this._complete=!0,n instanceof y?(this._status="killed",this._err=new w("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=n)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(e){this._state=e,this._stateHandler(e)}await_result(){return this._result}on_result(e,r){this._handledResult=this._result.then(e),r&&(this._handledResult=this._handledResult.catch(r))}on_error(e){this._handledResult=this._handledResult.catch(e)}on_state_change(e){this._stateHandler=e}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},h=class{target;constructor(e){e.startsWith(window.anvilAppMainPackage)||(e=window.anvilAppMainPackage+"."+e);let r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e));if(r||(Sk.importModule(e,!1,!0),r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e))),r===void 0)throw new Sk.builtin.RuntimeError("Problem importing module '"+e+"'");let s=W.replace("{$filename$}",JSON.stringify(e)).replace("{$files$}",JSON.stringify(Sk.builtinFiles)),l=new Blob([s],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(l)),H(this.target)}launch_task(e,r,s){if(this.target.currentTask!==null)throw new w("BackgroundWorker already has an active task");let[n,i,a]=this.target.launchTask(e,r,s);return new b(n,i,a,this.target)}};window.anvilLabs={Worker:h,WorkerTaskKilled:y};})();
"""

_script = _script.replace("{$endpoints$}", repr(anvil.server.get_api_origin()))

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
