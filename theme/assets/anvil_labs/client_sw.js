function a(){let t=document.getElementsByTagName("script");return Array.from(t).find(e=>e.src?.includes("skulpt.min.js")).src}async function o(t){let e=null;try{e=Sk.read(t),typeof e!="string"&&(e=await Sk.misceval.asyncToPromise(()=>e))}catch{if(t.startsWith("app/")){let[i,n,s]=t.split("/");s==="__init__.py"&&n!=="anvil"&&(e="pass")}else e=null}return e}var r;async function c(t){let{data:e}=t;if(!e.ANVIL_LABS||e.type!=="IMPORT")return;let{filename:i,id:n}=e,s=await o(i);r?.postMessage({type:"MODULE",content:s,id:n})}async function l(){let t=await navigator.serviceWorker.register("_/theme/anvil_labs/sw.js",{type:"module"});try{t.update()}catch{}return r=t.active||t.installing||t.waiting||null,r?.postMessage({type:"SKULPT",url:a()}),navigator.serviceWorker.addEventListener("message",c),[r,t]}var g=l;export{g as default,l as init};
