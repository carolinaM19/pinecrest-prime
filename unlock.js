/* Pinecrest Prime LLC: unlocks the encrypted data in the browser.
   The data file can only be read with the site password. Nothing is sent anywhere. */
(function(){
  const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
  const enc=new TextEncoder(),dec=new TextDecoder();
  const KEEP='pp-key';
  let resolveDb;const dbReady=new Promise(r=>resolveDb=r);
  const gate=document.getElementById('login'),app=document.getElementById('appwrap'),msg=document.getElementById('loginMsg');
  async function fetchJson(f){const r=await fetch(f+'?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('Could not load '+f);return r.json()}
  async function privFromPassword(pw,keys){
    const pk=keys.privateKey;
    const base=await crypto.subtle.importKey('raw',enc.encode(pw),'PBKDF2',false,['deriveKey']);
    const kek=await crypto.subtle.deriveKey({name:'PBKDF2',hash:'SHA-256',salt:b64(pk.salt),iterations:pk.iterations},base,{name:'AES-GCM',length:256},false,['decrypt']);
    return new Uint8Array(await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(pk.iv)},kek,b64(pk.ciphertext)));
  }
  async function openData(pkcs8){
    const priv=await crypto.subtle.importKey('pkcs8',pkcs8,{name:'RSA-OAEP',hash:'SHA-256'},false,['decrypt']);
    const d=await fetchJson('data.enc.json');
    const raw=await crypto.subtle.decrypt({name:'RSA-OAEP'},priv,b64(d.wrappedKey));
    const k=await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['decrypt']);
    return JSON.parse(dec.decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(d.iv)},k,b64(d.ciphertext))));
  }
  function makeDb(payload){
    window.__publishedAt=payload.publishedAt;
    const C=payload.collections||{};
    const snap=c=>({docs:(C[c]||[]).map(d=>({id:d.id,exists:true,data:()=>d})),size:(C[c]||[]).length,empty:!(C[c]||[]).length});
    const ro=()=>Promise.reject({code:'invalid_argument',message:'This website is view-only.'});
    const ref=(c,id)=>({id,set:ro,update:ro,delete:ro,get:async()=>{const d=(C[c]||[]).find(x=>x.id===id);return{id,exists:!!d,data:()=>d}},
      onSnapshot:fn=>{const d=(C[c]||[]).find(x=>x.id===id);setTimeout(()=>fn({id,exists:!!d,data:()=>d}),0);return()=>{}}});
    return{collection:c=>({doc:id=>ref(c,id),onSnapshot:fn=>{setTimeout(()=>fn(snap(c)),0);return()=>{}}}),doc:p=>{const[c,id]=p.split('/');return ref(c,id)}};
  }
  async function unlockWith(pkcs8){const payload=await openData(pkcs8);gate.hidden=true;app.hidden=false;resolveDb(makeDb(payload))}
  function save(pkcs8,remember){const s=btoa(String.fromCharCode(...pkcs8));try{(remember?localStorage:sessionStorage).setItem(KEEP,s)}catch(e){}}
  function saved(){try{return localStorage.getItem(KEEP)||sessionStorage.getItem(KEEP)}catch(e){return null}}
  function forget(){try{localStorage.removeItem(KEEP);sessionStorage.removeItem(KEEP)}catch(e){}}
  document.getElementById('loginForm').addEventListener('submit',async e=>{
    e.preventDefault();const pw=document.getElementById('loginPw').value;const btn=document.getElementById('loginBtn');
    btn.disabled=true;msg.textContent='Unlocking…';
    try{const keys=await fetchJson('keys.json');const pkcs8=await privFromPassword(pw.trim(),keys);save(pkcs8,document.getElementById('remember').checked);await unlockWith(pkcs8);msg.textContent=''}
    catch(err){console.error(err);msg.textContent=err&&err.name==='OperationError'?'That password isn’t right. Try again.':'Something went wrong loading the data. Reload the page and try again.'}
    btn.disabled=false;
  });
  document.getElementById('signout').addEventListener('click',()=>{forget();location.reload()});
  (async()=>{const s=saved();if(s){try{await unlockWith(b64(s));return}catch(e){forget()}}gate.hidden=false;document.getElementById('loginPw').focus()})();
  window.__openFile=async f=>{
    const w=window.open('','_blank');
    try{const r=await fetch(f.path+'?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('missing');
      const k=await crypto.subtle.importKey('raw',b64(f.key),'AES-GCM',false,['decrypt']);
      const raw=await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(f.iv)},k,await r.arrayBuffer());
      const url=URL.createObjectURL(new Blob([raw],{type:f.type||'application/pdf'}));
      if(w)w.location.href=url;else{const a=document.createElement('a');a.href=url;a.download=f.name||'document';document.body.append(a);a.click();a.remove()}
    }catch(e){console.error(e);if(w)w.close();alert('That document could not be opened. Try again in a minute.')}
  };
  window.claude={use:async n=>{if(n==='db')return dbReady;if(n==='user')return{can:async()=>false,isOwner:()=>false,canEdit:()=>false};return null}};
})();
