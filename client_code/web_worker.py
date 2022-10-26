# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W
import anvil.server

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{function b(e){let{builtin:{BaseException:t},ffi:{toJs:r}}=Sk;function a(){let i={resolve:()=>{},reject:()=>{}};return i.promise=new Promise((n,l)=>{i.resolve=n,i.reject=l}),i}let o={};e.registerFn=(i,n)=>{o[i]=n},e.moduleLoaded=a();function s(){e.task_state=new Proxy({},{set(i,n,l){return i[n]===l||(i[n]=l,e.postMessage({type:"STATE",state:{...i}})),!0}})}let u=new Map;e.fetchModule=i=>{let n=crypto.randomUUID();e.postMessage({type:"IMPORT",id:n,filename:i});let l=a();return u.set(n,l),l.promise},e.onmessage=async i=>{let{data:n}=i;switch(n.type){case"CALL":{await e.moduleLoaded.promise,s();let{id:l,fn:d,args:f,kws:y}=n;console.debug(`RPC call ${l}:`,d,f);let _=o[d],k,m,c,h;if(e.currentTask={id:l,fn:d},!_)m="RuntimeError",c=[`No handler registered for '${n.fn}'`];else try{k=await _(f,y)}catch(p){p instanceof t?(c=r(p.args),m=p.tp$name,h=p.traceback):(m=p.constructor??"<unknown>",c=[p.message])}e.currentTask=null;try{stopExecution=!1,e.postMessage({type:"RESPONSE",id:n.id,value:k,errorType:m,errorArgs:c,errorTb:h})}catch(p){console.error(p,"Failed to post RPC response:",k,p)}break}case"KILL":stopExecution||(stopExecution=!0);break;case"MODULE":{let{id:l,content:d}=n,{resolve:f}=u.get(l);u.delete(l),f(d)}}}}function T(){let{ffi:{proxy:e,toPy:t},abstr:{setUpModuleMethods:r,objectSetItem:a},misceval:{promiseToSuspension:o,chain:s}}=Sk,u={__name__:t("js"),window:e(self)};async function i(n){let l=await new Function("return import("+JSON.stringify(n.toString())+")").call(null);return e(l)}return r("js",u,{await_promise:{$meth(n){let l=n.valueOf();return l instanceof Promise||l&&l.then&&typeof l.then=="function"?s(o(l),d=>t(d,{dictHook:f=>e(f)})):n},$flags:{OneArg:!0}},import_from:{$meth(n){return o(i(n))},$flags:{OneArg:!0}}}),a(Sk.sysmodules,t("anvil.js.window"),u.window),u}function D(){let{abstr:{setUpModuleMethods:e},ffi:{toPy:t}}=Sk,r={__name__:t("server")};return e("server",r,{get_api_origin:{$meth(){return t(self.anvilLabsEndpoint)},$flags:{NoArgs:!0}}}),r}function W(){let e=document.getElementsByTagName("script");return Array.from(e).find(t=>t.src?.includes("skulpt.min.js")).src}function C(){Sk.configure({output(e){return self.postMessage({type:"OUT",message:e})},yieldLimit:300,syspath:["app"],read(e){let t=self.anvilFiles[e];return t!==void 0?t:Sk.misceval.promiseToSuspension(self.fetchModule(e).then(r=>{if(r==null)throw"No module named "+e;return r}))}})}function M(){let{builtin:{RuntimeError:e},ffi:{toJs:t,toPy:r},misceval:{tryCatch:a,chain:o,Suspension:s,asyncToPromise:u,buildClass:i,callsimArray:n}}=Sk;Sk.builtins.self=Sk.builtins.worker=r(self);let l=i({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[e]),d=Sk.sysmodules.quick$lookup(r("__main__")).$d;for(let[f,y]of Object.entries(d))y.tp$call&&self.registerFn(f,(_,k)=>{_=_.map(c=>r(c)),k=Object.entries(k).map(([c,h])=>[c,r(h)]).flat();let m=a(()=>o(y.tp$call(_,k),c=>t(c)),c=>{throw c});return m instanceof s?u(()=>m,{"*":()=>{if(stopExecution){let{id:c,fn:h}=self.currentTask;throw n(l,[`<WorkerTask '${h}' (${c})> Killed`])}}}):m})}var $=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${W()}\\']);
self.anvilLabsEndpoint={$endpoints$};
(${b})(self);
const $f = (self.anvilFiles = {});
$f["src/lib/anvil/__init__.py"] = "";
$f["src/lib/anvil/js.js"] = \`var $builtinmodule=${T};\`;
$f["src/lib/anvil/server.js"] = \`var $builtinmodule=${D};\`;
(${C})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${M})();
})
`;function R(){let e={resolve:()=>{},reject:()=>{}};return e.promise=new Promise((t,r)=>{e.resolve=t,e.reject=r}),e}var{misceval:{callsimArray:P,buildClass:E},ffi:{toPy:O},builtin:{RuntimeError:S,str:x,print:L}}=Sk,v=E({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[S]);function j(e,t,r){let a;if(e==="WorkerTaskKilled")return a=P(v,t),a.traceback=r,a;try{let o=Sk.builtins[e];a=P(o,t.map(s=>O(s))),a.traceback=r??[]}catch{a=new Error(...t)}return a}function I(e){let t={};e.currentTask=null,e.stateHandler=()=>{},e.launchTask=(r,a,o)=>{let s=crypto.randomUUID();return e.currentTask={fn:r,id:s},e.postMessage({type:"CALL",id:s,fn:r,args:a,kws:o}),t[s]=R(),[s,r,new Promise(u=>u(t[s].promise))]},e.onmessage=async({data:r})=>{switch(r.type){case"OUT":{let{id:a,fn:o}=e.currentTask??{};L([`<worker-task '${o}' (${a})>:`,r.message],["end",x.$empty]);break}case"STATE":{e.stateHandler({...r.state});break}case"RESPONSE":{let{id:a,value:o,errorType:s,errorArgs:u,errorTb:i}=r,n=t[r.id];n?s?(console.debug(`RPC error response ${a}:`,s,u),n.reject(j(s,u,i))):(console.debug(`RPC response ${a}:`,o),n.resolve(o)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete t[r.id],e.currentTask=null;return}case"IMPORT":{let{id:a,filename:o}=r,s=null;try{s=Sk.read(o),typeof s!="string"&&(s=await Sk.misceval.asyncToPromise(()=>s))}catch{if(o.startsWith("app/")){let[u,i,n]=o.split("/");n==="__init__.py"&&i!=="anvil"&&(s="pass")}else s=null}e.postMessage({type:"MODULE",id:a,content:s})}}}}var w=class{constructor(t,r,a,o){this._id=t;this._name=r;this._result=a;this._target=o;this._startTime=Date.now(),this._handledResult=a,this._target.stateHandler=this._updateState.bind(this),this._result.then(s=>{this._complete=!0,this._status="completed",this._rv=s},s=>{this._complete=!0,s instanceof v?(this._status="killed",this._err=new S("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=s)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(t){this._state=t,this._stateHandler(t)}await_result(){return this._result}on_result(t,r){this._handledResult=this._result.then(t),r&&(this._handledResult=this._handledResult.catch(r))}on_error(t){this._handledResult=this._handledResult.catch(t)}on_state_change(t){this._stateHandler=t}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},g=class{target;constructor(t){t.startsWith(window.anvilAppMainPackage)||(t=window.anvilAppMainPackage+"."+t);let r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(t));if(r||(Sk.importModule(t,!1,!0),r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(t))),r===void 0)throw new Sk.builtin.RuntimeError("Problem importing module '"+t+"'");let a=$.replace("{$filename$}",JSON.stringify(t)),o=new Blob([a],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(o)),I(this.target)}launch_task(t,r,a){if(this.target.currentTask!==null)throw new S("BackgroundWorker already has an active task");let[s,u,i]=this.target.launchTask(t,r,a);return new w(s,u,i,this.target)}};window.anvilLabs={Worker:g,WorkerTaskKilled:v};})();
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
