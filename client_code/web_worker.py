# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W
import anvil.server

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{function b(t){let{builtin:{BaseException:e},ffi:{toJs:r}}=Sk;function s(){let i={resolve:()=>{},reject:()=>{}};return i.promise=new Promise((a,l)=>{i.resolve=a,i.reject=l}),i}let o={};t.registerFn=(i,a)=>{o[i]=a},t.moduleLoaded=s();function n(){t.task_state=new Proxy({},{set(i,a,l){return i[a]===l||(i[a]=l,t.postMessage({type:"STATE",state:{...i}})),!0}})}let u=new Map;t.fetchModule=i=>{let a=crypto.randomUUID();t.postMessage({type:"IMPORT",id:a,filename:i});let l=s();return u.set(a,l),l.promise},t.onmessage=async i=>{let{data:a}=i;switch(a.type){case"CALL":{await t.moduleLoaded.promise,n();let{id:l,fn:d,args:m,kws:y}=a;console.debug(`RPC call ${l}:`,d,m);let _=o[d],k,f,c,h;if(t.currentTask={id:l,fn:d},!_)f="RuntimeError",c=[`No handler registered for '${a.fn}'`];else try{k=await _(m,y)}catch(p){p instanceof e?(c=r(p.args),f=p.tp$name,h=p.traceback):(f=p.constructor??"<unknown>",c=[p.message])}t.currentTask=null;try{stopExecution=!1,t.postMessage({type:"RESPONSE",id:a.id,value:k,errorType:f,errorArgs:c,errorTb:h})}catch(p){console.error(p,"Failed to post RPC response:",k,p)}break}case"KILL":stopExecution||(stopExecution=!0);break;case"MODULE":{let{id:l,content:d}=a,{resolve:m}=u.get(l);u.delete(l),m(d)}}}}function T(){let{ffi:{proxy:t,toPy:e},abstr:{setUpModuleMethods:r,objectSetItem:s},misceval:{promiseToSuspension:o,chain:n}}=Sk,u={__name__:e("js"),window:t(self)};async function i(a){let l=await new Function("return import("+JSON.stringify(a.toString())+")").call(null);return t(l)}return r("js",u,{await_promise:{$meth(a){let l=a.valueOf();return l instanceof Promise||l&&l.then&&typeof l.then=="function"?n(o(l),d=>e(d,{dictHook:m=>t(m)})):a},$flags:{OneArg:!0}},import_from:{$meth(a){return o(i(a))},$flags:{OneArg:!0}}}),s(Sk.sysmodules,e("anvil.js.window"),u.window),u}function D(){let{abstr:{setUpModuleMethods:t},ffi:{toPy:e}}=Sk,r={__name__:e("server")};return t("server",r,{get_api_origin:{$meth(){return e(self.anvilLabsEndpoint)},$flags:{NoArgs:!0}}}),r}function $(){let t=document.getElementsByTagName("script");return Array.from(t).find(e=>e.src?.includes("skulpt.min.js")).src}function C(){let t=new Map(Object.entries({"src/lib/anvil/__init__.py":"","src/lib/anvil/js.js":`var $builtinmodule=${T};`,"src/lib/anvil/server.js":`var $builtinmodule=${D};`}));Sk.configure({output(e){return self.postMessage({type:"OUT",message:e})},yieldLimit:300,syspath:["app"],read(e){let r=t.get(e);return r!==void 0?r:Sk.misceval.promiseToSuspension(self.fetchModule(e).then(s=>{if(s==null)throw"No module named "+e;return s}))}})}function M(){let{builtin:{RuntimeError:t},ffi:{toJs:e,toPy:r},misceval:{tryCatch:s,chain:o,Suspension:n,asyncToPromise:u,buildClass:i,callsimArray:a}}=Sk;Sk.builtins.self=Sk.builtins.worker=r(self);let l=i({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[t]),d=Sk.sysmodules.quick$lookup(r("__main__")).$d;for(let[m,y]of Object.entries(d))y.tp$call&&self.registerFn(m,(_,k)=>{_=_.map(c=>r(c)),k=Object.entries(k).map(([c,h])=>[c,r(h)]).flat();let f=s(()=>o(y.tp$call(_,k),c=>e(c)),c=>{throw c});return f instanceof n?u(()=>f,{"*":()=>{if(stopExecution){let{id:c,fn:h}=self.currentTask;throw a(l,[`<WorkerTask '${h}' (${c})> Killed`])}}}):f})}var P=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${$()}\\']);
self.anvilLabsEndpoint={$endpoints$};
(${b})(self);
(${C})();
Sk.misceval.asyncToPromise(() => Sk.importMain({$filename$}, false, true)).then(() => {
  self.moduleLoaded.resolve();
  (${M})();
})
`;function R(){let t={resolve:()=>{},reject:()=>{}};return t.promise=new Promise((e,r)=>{t.resolve=e,t.reject=r}),t}var{misceval:{callsimArray:W,buildClass:E},ffi:{toPy:O},builtin:{RuntimeError:S,str:x,print:L}}=Sk,v=E({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[S]);function j(t,e,r){let s;if(t==="WorkerTaskKilled")return s=W(v,e),s.traceback=r,s;try{let o=Sk.builtins[t];s=W(o,e.map(n=>O(n))),s.traceback=r??[]}catch{s=new Error(...e)}return s}function I(t){let e={};t.currentTask=null,t.stateHandler=()=>{},t.launchTask=(r,s,o)=>{let n=crypto.randomUUID();return t.currentTask={fn:r,id:n},t.postMessage({type:"CALL",id:n,fn:r,args:s,kws:o}),e[n]=R(),[n,r,new Promise(u=>u(e[n].promise))]},t.onmessage=async({data:r})=>{switch(r.type){case"OUT":{let{id:s,fn:o}=t.currentTask??{};L([`<worker-task '${o}' (${s})>:`,r.message],["end",x.$empty]);break}case"STATE":{t.stateHandler({...r.state});break}case"RESPONSE":{let{id:s,value:o,errorType:n,errorArgs:u,errorTb:i}=r,a=e[r.id];a?n?(console.debug(`RPC error response ${s}:`,n,u),a.reject(j(n,u,i))):(console.debug(`RPC response ${s}:`,o),a.resolve(o)):console.warn(`Got worker response for invalid call ${r.id}`,r),delete e[r.id],t.currentTask=null;return}case"IMPORT":{let{id:s,filename:o}=r,n=null;try{n=Sk.read(o),typeof n!="string"&&(n=await Sk.misceval.asyncToPromise(()=>n))}catch{if(o.startsWith("app/")){let[u,i,a]=o.split("/");a==="__init__.py"&&i!=="anvil"&&(n="pass")}else n=null}t.postMessage({type:"MODULE",id:s,content:n})}}}}var w=class{constructor(e,r,s,o){this._id=e;this._name=r;this._result=s;this._target=o;this._startTime=Date.now(),this._handledResult=s,this._target.stateHandler=this._updateState.bind(this),this._result.then(n=>{this._complete=!0,this._status="completed",this._rv=n},n=>{this._complete=!0,n instanceof v?(this._status="killed",this._err=new S("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=n)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(e){this._state=e,this._stateHandler(e)}await_result(){return this._result}on_result(e,r){this._handledResult=this._result.then(e),r&&(this._handledResult=this._handledResult.catch(r))}on_error(e){this._handledResult=this._handledResult.catch(e)}on_state_change(e){this._stateHandler=e}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},g=class{target;constructor(e){e.startsWith(window.anvilAppMainPackage)||(e=window.anvilAppMainPackage+"."+e);let r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e));if(r||(Sk.importModule(e,!1,!0),r=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e))),r===void 0)throw new Sk.builtin.RuntimeError("Problem importing module '"+e+"'");let s=P.replace("{$filename$}",JSON.stringify(e)),o=new Blob([s],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(o)),I(this.target)}launch_task(e,r,s){if(this.target.currentTask!==null)throw new S("BackgroundWorker already has an active task");let[n,u,i]=this.target.launchTask(e,r,s);return new w(n,u,i,this.target)}};window.anvilLabs={Worker:g,WorkerTaskKilled:v};})();
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
