var f=(t,n)=>()=>(t&&(n=t(t=0)),n);var T=(t,n)=>()=>(n||t((n={exports:{}}).exports,n),n.exports);function p(){let{ffi:{proxy:t,toPy:n},abstr:{setUpModuleMethods:r,objectSetItem:i},misceval:{promiseToSuspension:o,chain:l}}=Sk,c={__name__:n("js"),window:t(self)};async function h(a){let s=await new Function("return import("+JSON.stringify(a.toString())+")").call(null);return t(s)}return r("js",c,{await_promise:{$meth(a){let s=a.valueOf();return s instanceof Promise||s&&s.then&&typeof s.then=="function"?l(o(s),L=>n(L,{dictHook:E=>t(E)})):a},$flags:{OneArg:!0}},import_from:{$meth(a){return o(h(a))},$flags:{OneArg:!0}}}),i(Sk.sysmodules,n("anvil.js.window"),c.window),c}var y=f(()=>{});var g,m=f(()=>{y();g=new Map([["src/lib/anvil/__init__.py",""],["src/lib/anvil/js.js",`var $builtinmodule=${p};`],["src/lib/anvil/server.js",""]])});function S(){let t={resolve:()=>{},reject:()=>{}};return t.promise=new Promise((n,r)=>{t.resolve=n,t.reject=r}),t}function j(t){let n=crypto.randomUUID();postMessage({type:"IMPORT",id:n,filename:t});let r=S();return d.set(n,r),r.promise}function v(){Sk.configure({output(t){return self.postMessage({type:"OUT",message:t})},yieldLimit:300,syspath:["app"],read(t){let n=g.get(t);return n!==void 0?n:Sk.misceval.promiseToSuspension(j(t).then(r=>{if(r==null)throw"No module named "+t;return r}))}}),Sk.builtins.self=Sk.ffi.proxy(self),u.resolve(!0)}function D(t){let{data:n}=t;if(n.type==="MODULE"){let{id:r,content:i}=n,{resolve:o}=d.get(r);d.delete(r),o(i)}}var u,d,w=f(()=>{m();u=S();d=new Map;self.addEventListener("message",D)});var x=T((_,b)=>{w();self.window=self;self.addEventListener("sync",t=>{k("sync",{tag:t.tag})});function O(){function t(n,r=[]){if(n.length!==1)throw new Sk.builtin.TypeError("Expeceted one arg to raise_event");let i={};for(let o=0;o<r.length;o+=2){let l=r[o],c=r[o+1];i[l]=Sk.ffi.toJs(c)}k(n[0].toString(),r)}t.co_fastcall=!0,self.raise_event=new Sk.builtin.func(t)}self.onmessage=async e=>{let data=e.data,{type}=data;switch(type){case"SKULPT":{let skMod=await fetch(data.url);eval(await skMod.text()),v(),O();break}case"INIT":{await u.promise;let{name:t}=data;Sk.misceval.asyncToPromise(()=>Sk.importMain(t,!1,!0));break}}};async function M(t){t.ANVIL_LABS=!0;let n=await self.clients.matchAll({includeUncontrolled:!0,type:"window"});for(let r of n)r.postMessage(t)}self.postMessage=M;function k(t,n={}){n.event_name=t,M({type:"EVENT",name:t,kws:n})}});export default x();
