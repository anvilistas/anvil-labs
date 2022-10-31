# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{function b(e){let{builtin:{BaseException:t},ffi:{toJs:r}}=Sk;function a(){let o={resolve:()=>{},reject:()=>{}};return o.promise=new Promise((n,i)=>{o.resolve=n,o.reject=i}),o}let l={};e.registerFn=(o,n)=>{l[o]=n},e.moduleLoaded=a();function s(){e.task_state=new Proxy({},{set(o,n,i){return o[n]===i||(o[n]=i,e.postMessage({type:"STATE",state:{...o}})),!0}})}let c=new Map;e.fetchModule=o=>{let n=crypto.randomUUID();e.postMessage({type:"IMPORT",id:n,filename:o});let i=a();return c.set(n,i),i.promise},e.onmessage=async o=>{let{data:n}=o;switch(n.type){case"CALL":{await e.moduleLoaded.promise,s();let{id:i,fn:d,args:f,kws:h}=n;console.debug(`RPC call ${i}:`,d,f);let y=l[d],k,m,u,_;if(e.currentTask={id:i,fn:d},!y)m="RuntimeError",u=[`No handler registered for '${n.fn}'`];else try{k=await y(f,h)}catch(p){p instanceof t?(u=r(p.args),m=p.tp$name,_=p.traceback):(m=p.constructor??"<unknown>",u=[p.message])}e.currentTask=null;try{stopExecution=!1,e.postMessage({type:"RESPONSE",id:n.id,value:k,errorType:m,errorArgs:u,errorTb:_})}catch(p){console.error(p,"Failed to post RPC response:",k,p)}break}case"KILL":stopExecution||(stopExecution=!0);break;case"MODULE":{let{id:i,content:d}=n,{resolve:f}=c.get(i);c.delete(i),f(d)}}}}function T(){let{ffi:{proxy:e,toPy:t},abstr:{setUpModuleMethods:r,objectSetItem:a},misceval:{promiseToSuspension:l,chain:s}}=Sk,c={__name__:t("js"),window:e(self)};async function o(n){let i=await new Function("return import("+JSON.stringify(n.toString())+")").call(null);return e(i)}return r("js",c,{await_promise:{$meth(n){let i=n.valueOf();return i instanceof Promise||i&&i.then&&typeof i.then=="function"?s(l(i),d=>t(d,{dictHook:f=>e(f)})):n},$flags:{OneArg:!0}},import_from:{$meth(n){return l(o(n))},$flags:{OneArg:!0}}}),a(Sk.sysmodules,t("anvil.js.window"),c.window),c}function P(){let e=document.getElementsByTagName("script");return Array.from(e).find(t=>t.src?.includes("skulpt.min.js")).src}function C(){Sk.configure({output(e){return self.postMessage({type:"OUT",message:e})},yieldLimit:300,syspath:["app"],read(e){let t=self.anvilFiles[e];return t!==void 0?t:Sk.misceval.promiseToSuspension(self.fetchModule(e).then(r=>{if(r==null)throw"No module named "+e;return r}))}})}function $(){let{builtin:{RuntimeError:e},ffi:{toJs:t,toPy:r},misceval:{tryCatch:a,chain:l,Suspension:s,asyncToPromise:c,buildClass:o,callsimArray:n}}=Sk;Sk.builtins.self=Sk.builtins.worker=r(self);let i=o({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[e]),d=Sk.sysmodules.quick$lookup(r("__main__")).$d;for(let[f,h]of Object.entries(d))h.tp$call&&self.registerFn(f,(y,k)=>{y=y.map(u=>r(u)),k=Object.entries(k).map(([u,_])=>[u,r(_)]).flat();let m=a(()=>l(h.tp$call(y,k),u=>t(u)),u=>{throw u});return m instanceof s?c(()=>m,{"*":()=>{if(stopExecution){let{id:u,fn:_}=self.currentTask;throw n(i,[`<WorkerTask '${_}' (${u})> Killed`])}}}):m})}var D=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${P()}\\']);
(${b})(self);
const $f = (self.anvilFiles = {});
$f["src/lib/anvil/__init__.py"] = "";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${T};\`;
$f["src/lib/anvil/server.py"] = "";
(${C})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${$})();
})
`;function M(){let e={resolve:()=>{},reject:()=>{}};return e.promise=new Promise((t,r)=>{e.resolve=t,e.reject=r}),e}var{misceval:{callsimArray:W,buildClass:R},ffi:{toPy:E},builtin:{RuntimeError:S,str:O,print:x}}=Sk,w=R({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[S]);function L(e,t,r){let a;if(e==="WorkerTaskKilled")return a=W(w,t),a.traceback=r,a;try{let l=Sk.builtins[e];a=W(l,t.map(s=>E(s))),a.traceback=r??[]}catch{a=new Error(...t)}return a}function j(e){let t={};e.currentTask=null,e.stateHandler=()=>{},e.launchTask=(r,a,l)=>{let s=crypto.randomUUID();return e.currentTask={fn:r,id:s},e.postMessage({type:"CALL",id:s,fn:r,args:a,kws:l}),t[s]=M(),[s,r,new Promise(c=>c(t[s].promise))]},e.onmessage=async({data:r})=>{switch(r.type){case"OUT":{let{id:a,fn:l}=e.currentTask??{};x([`<worker-task '${l}' (${a})>:`,r.message],["end",O.$empty]);break}case"STATE":{e.stateHandler({...r.state});break}case"RESPONSE":{let{id:a,value:l,errorType:s,errorArgs:c,errorTb:o}=r,n=t[r.id];n?s?(console.debug(`RPC error response ${a}:`,s,c),n.reject(L(s,c,o))):(console.debug(`RPC response ${a}:`,l),n.resolve(l)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete t[r.id],e.currentTask=null;return}case"IMPORT":{let{id:a,filename:l}=r,s=null;try{s=Sk.read(l),typeof s!="string"&&(s=await Sk.misceval.asyncToPromise(()=>s))}catch{if(l.startsWith("app/")){let[c,o,n]=l.split("/");n==="__init__.py"&&o!=="anvil"&&(s="pass")}else s=null}e.postMessage({type:"MODULE",id:a,content:s})}}}}var v=class{constructor(t,r,a,l){this._id=t;this._name=r;this._result=a;this._target=l;this._startTime=Date.now(),this._handledResult=a,this._target.stateHandler=this._updateState.bind(this),this._result.then(s=>{this._complete=!0,this._status="completed",this._rv=s},s=>{this._complete=!0,s instanceof w?(this._status="killed",this._err=new S("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=s)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(t){this._state=t,this._stateHandler(t)}await_result(){return this._result}on_result(t,r){this._handledResult=this._result.then(t),r&&(this._handledResult=this._handledResult.catch(r))}on_error(t){this._handledResult=this._handledResult.catch(t)}on_state_change(t){this._stateHandler=t}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},g=class{target;constructor(t){t.startsWith(window.anvilAppMainPackage)||(t=window.anvilAppMainPackage+"."+t);let r=D.replace("{$filename$}",JSON.stringify(t)),a=new Blob([r],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(a)),j(this.target)}launch_task(t,r,a){if(this.target.currentTask!==null)throw new S("BackgroundWorker already has an active task");let[s,c,o]=this.target.launchTask(t,r,a);return new v(s,c,o,this.target)}};window.anvilLabs??={};window.anvilLabs.Worker=g;window.anvilLabs.WorkerTaskKilled=w;})();
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
