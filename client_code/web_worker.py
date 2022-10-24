# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W
import anvil.server

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{function v(t){let{builtin:{BaseException:e},ffi:{toJs:r}}=Sk,n={};t.registerFn=(s,a)=>{n[s]=a};function i(){t.task_state=new Proxy({},{set(s,a,o){return s[a]===o||(s[a]=o,t.postMessage({type:"STATE",state:{...s}})),!0}})}t.onmessage=async s=>{let{data:a}=s;switch(a.type){case"CALL":{i();let{id:o,fn:l,args:p,kws:m}=a;console.debug(`RPC call ${o}:`,l,p);let h=n[l],_,k,d,f;if(t.currentTask={id:o,fn:l},!h)k="RuntimeError",d=[`No handler registered for '${a.fn}'`];else try{_=await h(p,m)}catch(u){u instanceof e?(d=r(u.args),k=u.tp$name,f=u.traceback):(k=u.constructor??"<unknown>",d=[u.message])}t.currentTask=null;try{stopExecution=!1,t.postMessage({type:"RESPONSE",id:a.id,value:_,errorType:k,errorArgs:d,errorTb:f})}catch(u){console.error(u,"Failed to post RPC response:",_,u)}break}case"KILL":stopExecution||(stopExecution=!0);break}}}function T(){let{ffi:{proxy:t,toPy:e},abstr:{setUpModuleMethods:r},misceval:{promiseToSuspension:n,chain:i}}=Sk,s={__name__:e("js"),window:t(self)};async function a(o){let l=await new Function("return import("+JSON.stringify(o.toString())+")").call(null);return t(l)}return r("js",s,{await_promise:{$meth(o){let l=o.valueOf();return l instanceof Promise||l&&l.then&&typeof l.then=="function"?i(n(l),p=>e(p,{dictHook:m=>t(m)})):o},$flags:{OneArg:!0}},import_from:{$meth(o){return n(a(o))},$flags:{OneArg:!0}}}),s.window=Sk.builtins.self,s}function $(){let{abstr:{setUpModuleMethods:t},ffi:{toPy:e}}=Sk,r={__name__:e("server")};return t("server",r,{get_api_origin:{$meth(){return e(self.anvilLabsEndpoint)},$flags:{NoArgs:!0}}}),r}function P(){let t=document.getElementsByTagName("script");return Array.from(t).find(e=>e.src?.includes("skulpt.min.js")).src}function R(){Sk.configure({output(t){return self.postMessage({type:"OUT",message:t})},yieldLimit:300,syspath:["app"]})}function D(){let{builtin:{RuntimeError:t,str:e},ffi:{toJs:r,toPy:n},misceval:{tryCatch:i,chain:s,Suspension:a,asyncToPromise:o,buildClass:l,callsimArray:p}}=Sk;Sk.builtins.self=n(self);let m=l({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[t]),h=Sk.sysmodules.quick$lookup(new e("__main__")).$d;for(let[_,k]of Object.entries(h))k.tp$call&&self.registerFn(_,(d,f)=>{d=d.map(c=>n(c)),f=Object.entries(f).map(([c,S])=>[c,n(S)]).flat();let u=i(()=>s(k.tp$call(d,f),c=>r(c)),c=>{throw c});return u instanceof a?o(()=>u,{"*":()=>{if(stopExecution){let{id:c,fn:S}=self.currentTask;throw p(m,[`<WorkerTask '${S}' (${c})> Killed`])}}}):u})}var W=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${P()}\\']);
self.anvilLabsEndpoint={$endpoints$};
(${v})(self);
Sk.builtinFiles = {$files$}; Sk.builtins.worker = Sk.ffi.toPy(self);
const $f = Sk.builtinFiles.files;
$f["src/lib/anvil/__init__.py"] = "";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${T};\`;
$f["src/lib/anvil/server.js"] = \`var $builtinmodule=${$};\`;
(${R})();
Sk.importMain({$filename$}, false, true);
(${D})();
`;function E(){let t={resolve:()=>{},reject:()=>{}};return t.promise=new Promise((e,r)=>{t.resolve=e,t.reject=r}),t}var{misceval:{callsimArray:C,buildClass:x},ffi:{toPy:O},builtin:{RuntimeError:w,str:A,print:H}}=Sk,g=x({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[w]);function M(t,e,r){let n;if(t==="WorkerTaskKilled")return n=C(g,e),n.traceback=r,n;try{let i=Sk.builtins[t];n=C(i,e.map(s=>O(s))),n.traceback=r??[]}catch{n=new Error(...e)}return n}function K(t){let e={};t.currentTask=null,t.stateHandler=()=>{},t.launchTask=(r,n,i)=>{let s=crypto.randomUUID();return t.currentTask={fn:r,id:s},t.postMessage({type:"CALL",id:s,fn:r,args:n,kws:i}),e[s]=E(),[s,r,new Promise(a=>a(e[s].promise))]},t.onmessage=({data:r})=>{switch(r.type){case"OUT":{let{id:n,fn:i}=t.currentTask;H([`<worker-task '${i}' (${n})>:`,r.message],["end",A.$empty]);break}case"STATE":{t.stateHandler({...r.state});break}case"RESPONSE":{let{id:n,value:i,errorType:s,errorArgs:a,errorTb:o}=r,l=e[r.id];l?s?(console.debug(`RPC error response ${n}:`,s,a),l.reject(M(s,a,o))):(console.debug(`RPC response ${n}:`,i),l.resolve(i)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete e[r.id],t.currentTask=null}}}}var b=class{constructor(e,r,n,i){this._id=e;this._name=r;this._result=n;this._target=i;this._startTime=Date.now(),this._handledResult=n,this._target.stateHandler=this._updateState.bind(this),this._result.then(s=>{this._complete=!0,this._status="completed",this._rv=s},s=>{this._complete=!0,s instanceof g?(this._status="killed",this._err=new w("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=s)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(e){this._state=e,this._stateHandler(e)}await_result(){return this._result}on_result(e,r){this._handledResult=this._result.then(e),r&&(this._handledResult=this._handledResult.catch(r))}on_error(e){this._handledResult=this._handledResult.catch(e)}on_state_change(e){this._stateHandler=e}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},y=class{target;constructor(e){e.startsWith(window.anvilAppMainPackage)||(e=window.anvilAppMainPackage+"."+e);let r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e));if(r||(Sk.importModule(e,!1,!0),r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e))),r===void 0)throw new Sk.builtin.RuntimeError("Problem importing module '"+e+"'");let n=W.replace("{$filename$}",JSON.stringify(e)).replace("{$files$}",JSON.stringify(Sk.builtinFiles)),i=new Blob([n],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(i)),K(this.target)}launch_task(e,r,n){if(this.target.currentTask!==null)throw new w("BackgroundWorker already has an active task");let[s,a,o]=this.target.launchTask(e,r,n);return new b(s,a,o,this.target)}};window.anvilLabs={Worker:y,WorkerTaskKilled:g};})();
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
