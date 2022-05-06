# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import datetime

import anvil.js
import anvil.js.window as _W
import anvil.server

_script = """
function f(r){let t={};r.registerFn=(n,s)=>{t[n]=s};function e(){r.task_state=new Proxy({},{set(n,s,a){return n[s]===a||(n[s]=a,r.postMessage({type:"STATE",state:{...n}})),!0}})}r.onmessage=async n=>{let{data:s}=n;switch(s.type){case"CALL":{e(),console.debug(`RPC call ${s.id}:`,s.fn,s.args);let a=t[s.fn],i,o;if(!a)o=`No handler registered for '${s.fn}'`;else try{i=await a(...s.args)}catch(l){o=l.toString()}try{stopExecution=!1,r.postMessage({type:"RESPONSE",id:s.id,value:i,error:o})}catch(l){console.error(l,"Failed to post RPC response:",i,o)}break}case"KILL":stopExecution||(stopExecution=!0);break}}}var c;function y(){if(c!==void 0)return c;for(let r of document.getElementsByTagName("script"))if(r.src.includes("skulpt.min.js")){c=r.src;break}return c}function S(){Sk.configure({output(l){return self.postMessage({type:"OUT",message:l})},yieldLimit:300});let{builtin:{RuntimeError:r},ffi:{toJs:t,toPy:e},misceval:{tryCatch:n,chain:s,Suspension:a,asyncToPromise:i}}=Sk;Sk.builtins.self=e(self);let o={};$compiledmod(o);for(let[l,h]of Object.entries(o))h.tp$call&&self.registerFn(l,(...p)=>{p=p.map(u=>e(u));let k=n(()=>s(h.tp$call(p),u=>t(u)),u=>{throw u});return k instanceof a?i(()=>k,{"*":()=>{if(stopExecution)throw new r("killed")}}):k})}var _=`
let stopExecution = false;
(${f})(self);
self.importScripts(['${y()}']); Sk.builtinFiles = ${JSON.stringify(Sk.builtinFiles)}; Sk.builtins.worker = Sk.ffi.toPy(self);
{source};
(${S})();
`;var{builtin:{str:w,RuntimeError:g,print:v}}=Sk;function b(r){let t={};r.currentTask=null,r.stateHandler=()=>{},r.launchTask=(e,...n)=>{let s=crypto.randomUUID();return r.currentTask={fn:e,id:s},r.postMessage({type:"CALL",id:s,fn:e,args:n}),t[s]=window.RSVP.defer(),[s,e,new Promise(a=>a(t[s].promise))]},r.onmessage=({data:e})=>{switch(e.type){case"OUT":{let{id:n,fn:s}=r.currentTask;v([`<worker-task '${s}' (${n})>:`,e.message],["end",w.$empty]);break}case"STATE":{r.stateHandler({...e.state});break}case"RESPONSE":{let n=t[e.id];n?e.error?(console.debug(`RPC error response ${e.id}:`,e.error),n.reject(e.error)):(console.debug(`RPC response ${e.id}:`,e.value),n.resolve(e.value)):console.warn(`Got worker response for invalid call ${e.id}`,e),delete t[e.id],r.currentTask=null}}}}var m=class{constructor(t,e,n,s){this._id=t;this._name=e;this._result=n;this._target=s;this._startTime=Date.now(),this._handledResult=n,this._target.stateHandler=this._updateState.bind(this),this._result.then(a=>{this._complete=!0,this._status="completed",this._rv=a},a=>{a&&a.includes("RuntimeError: killed")?this._status="killed":(this._status="failed",this._complete=!0,this._err=a)})}_handledResult;_startTime;_state={};_rv=null;_err=null;_complete=!1;_status=null;_stateHandler=()=>{};_updateState(t){this._state=t,this._stateHandler(t)}await_result(){return this._result}on_result(t,e){this._handledResult=this._result.then(t),e&&(this._handledResult=this._handledResult.catch(e))}on_error(t){this._handledResult=this._handledResult.catch(t)}on_state_change(t){this._stateHandler=t}get_state(){return this._state}get_id(){return this._id}get_task_name(){return this._name}get_termination_status(){return this._status}get_return_value(){return this._rv}get_error(){if(this._err!==null)throw this._err}get_start_time(){return this._startTime}is_completed(){if(this._status==="killed")throw new g("'"+this._name+"' worker task was killed");return this._complete}is_running(){return!this._complete}kill(){this._complete||this._target.postMessage({type:"KILL",id:this._id})}},d=class{target;constructor(t){t.startsWith(window.anvilAppMainPackage)||(t=window.anvilAppMainPackage+"."+t);let e=Sk.sysmodules.quick$lookup(new Sk.builtin.str(t));e||(Sk.importModule(t,!1,!0),e=Sk.sysmodules.quick$lookup(new Sk.builtin.str(t)));let n=e.$js,s=new Blob([_.replace("{source}",n)],{type:"text/javascript"});this.target=new Worker(URL.createObjectURL(s)),b(this.target)}launch_task(t,...e){if(this.target.currentTask!==null)throw new g("BackgroundWorker already has an active task");let[s,a,i]=this.target.launchTask(t,...e);return new m(s,a,i,this.target)}};window._BgWorker=d;
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

_Worker = anvil.js.window._BgWorker


class Worker:
    def __init__(self, module):
        self._worker = _Worker(module)

    def launch_task(self, fn, *args):
        task = self._worker.launch_task(fn, *args)
        return Task(task)


class Task:
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
