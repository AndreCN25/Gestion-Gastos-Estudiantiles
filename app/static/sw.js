const CACHE='cuentaclara-shell-v4';
const SHELL=['/','/static/styles.css','/static/app.js','/static/manifest.webmanifest','/static/favicon.svg'];
const SHELL_PATHS=new Set(SHELL);

self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL))));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('cuentaclara-shell-')&&key!==CACHE).map(key=>caches.delete(key))))));
self.addEventListener('fetch',event=>{
  const request=event.request;
  const url=new URL(request.url);
  if(request.method!=='GET'||url.origin!==self.location.origin||!SHELL_PATHS.has(url.pathname))return;
  event.respondWith(fetch(request).then(response=>{
    if(response.ok)caches.open(CACHE).then(cache=>cache.put(request,response.clone()));
    return response;
  }).catch(async()=>await caches.match(request)||Response.error()));
});
