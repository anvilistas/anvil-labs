# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W
import anvil.server

__version__ = "0.0.1"

_script = """
'use strict';
(()=>{function S(r){let{builtin:{BaseException:e},ffi:{toJs:t}}=Sk,a={};r.registerFn=(s,i)=>{a[s]=i};function o(){r.task_state=new Proxy({},{set(s,i,l){return s[i]===l||(s[i]=l,r.postMessage({type:"STATE",state:{...s}})),!0}})}r.onmessage=async s=>{let{data:i}=s;switch(i.type){case"CALL":{o();let{id:l,fn:c,args:f,kws:_}=i;console.debug(`RPC call ${l}:`,c,f);let k=a[c],p,u,d,m;if(r.currentTask={id:l,fn:c},!k)u="RuntimeError",d=[`No handler registered for '${i.fn}'`];else try{p=await k(f,_)}catch(n){n instanceof e?(d=t(n.args),u=n.tp$name,m=n.traceback):(u=n.constructor??"<unknown>",d=[n.message])}r.currentTask=null;try{stopExecution=!1,r.postMessage({type:"RESPONSE",id:i.id,value:p,errorType:u,errorArgs:d,errorTb:m})}catch(n){console.error(n,"Failed to post RPC response:",p,n)}break}case"KILL":stopExecution||(stopExecution=!0);break}}}function W(){let r=document.getElementsByTagName("script");return Array.from(r).find(e=>e.src?.includes("skulpt.min.js")).src}function C(){Sk.configure({output(k){return self.postMessage({type:"OUT",message:k})},yieldLimit:300});let{builtin:{RuntimeError:r},ffi:{toJs:e,toPy:t},misceval:{tryCatch:a,chain:o,Suspension:s,asyncToPromise:i,buildClass:l,callsimArray:c}}=Sk;Sk.builtins.self=t(self);let f=l({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[r]),_={};$compiledmod(_);for(let[k,p]of Object.entries(_))p.tp$call&&self.registerFn(k,(u,d)=>{u=u.map(n=>t(n)),d=Object.entries(d).map(([n,g])=>[n,t(g)]).flat();let m=a(()=>o(p.tp$call(u,d),n=>e(n)),n=>{throw n});return m instanceof s?i(()=>m,{"*":()=>{if(stopExecution){let{id:n,fn:g}=self.currentTask;throw c(f,[`<WorkerTask '${g}' (${n})> Killed`])}}}):m})}var b=`
let stopExecution = false;
const window = self;
self.importScripts([\\'${W()}\\']);
(${S})(self);
Sk.builtinFiles = ${JSON.stringify(Sk.builtinFiles)}; Sk.builtins.worker = Sk.ffi.toPy(self);
{source};
(${C})();
`;function P(){let r={resolve:()=>{},reject:()=>{}};return r.promise=new Promise((e,t)=>{r.resolve=e,r.reject=t}),r}var{misceval:{callsimArray:v,buildClass:R},ffi:{toPy:D},builtin:{RuntimeError:T,str:E,print:$}}=Sk,y=R({__name__:"anvil_labs.web_worker"},()=>{},"WorkerTaskKilled",[T]);function x(r,e,t){let a;if(r==="WorkerTaskKilled")return a=v(y,e),a.traceback=t,a;try{let o=Sk.builtins[r];a=v(o,e.map(s=>D(s))),a.traceback=t??[]}catch{a=new Error(...e)}return a}function O(r){let e={};r.currentTask=null,r.stateHandler=()=>{},r.launchTask=(t,a,o)=>{let s=crypto.randomUUID();return r.currentTask={fn:t,id:s},r.postMessage({type:"CALL",id:s,fn:t,args:a,kws:o}),e[s]=P(),[s,t,new Promise(i=>i(e[s].promise))]},r.onmessage=({data:t})=>{switch(t.type){case"OUT":{let{id:a,fn:o}=r.currentTask;$([`<worker-task '${o}' (${a})>:`,t.message],["end",E.$empty]);break}case"STATE":{r.stateHandler({...t.state});break}case"RESPONSE":{let{id:a,value:o,errorType:s,errorArgs:i,errorTb:l}=t,c=e[t.id];c?s?(console.debug(`RPC error response ${a}:`,s,i),c.reject(x(s,i,l))):(console.debug(`RPC response ${a}:`,o),c.resolve(o)):console.warn(`Got worker response for invalid call ${t.id}`,t),delete e[t.id],r.currentTask=null}}}}var w=class{constructor(e,t,a,o){this._id=e;this._name=t;this._result=a;this._target=o;this._startTime=Date.now(),this._handledResult=a,this._target.stateHandler=this._updateState.bind(this),this._result.then(s=>{this._complete=!0,this._status="completed",this._rv=s},s=>{this._complete=!0,s instanceof y?(this._status="killed",this._err=new T("'"+this._name+"' worker task was killed")):(this._status="failed",this._err=s)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(e){this._state=e,this._stateHandler(e)}await_result(){return this._result}on_result(e,t){this._handledResult=this._result.then(e),t&&(this._handledResult=this._handledResult.catch(t))}on_error(e){this._handledResult=this._handledResult.catch(e)}on_state_change(e){this._stateHandler=e}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){if(this._err)throw this._err;return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._err)throw this._err;return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},h=class{target;constructor(e){e.startsWith(window.anvilAppMainPackage)||(e=window.anvilAppMainPackage+"."+e);let t=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e));t||(Sk.importModule(e,!1,!0),t=Sk.sysmodules.quick$lookup(new Sk.builtin.str(e)));let a=t.$js,o=new Blob([b.replace("{source}",a)],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(o)),O(this.target)}launch_task(e,t,a){if(this.target.currentTask!==null)throw new T("BackgroundWorker already has an active task");let[s,i,l]=this.target.launchTask(e,t,a);return new w(s,i,l,this.target)}};window.anvilLabs={Worker:h,WorkerTaskKilled:y};})();
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
