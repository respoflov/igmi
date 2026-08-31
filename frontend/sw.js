/* sw.js — Service Worker
 *
 * 하는 일: 앱의 "껍데기"(HTML/CSS/아이콘)를 미리 저장해뒀다가, 다음 접속 때
 * 인터넷 없이도 화면이 뜨게 해준다. 이게 PWA 의 핵심 부품 중 하나다.
 *
 * 주의: 판별(추론)은 백엔드 API 를 부르므로 인터넷이 필요하다.
 *       오프라인에서 뜨는 건 화면까지다 (지침 명시 사항).
 *
 * CACHE_NAME 의 버전(v1)을 올리면 옛 캐시가 지워지고 새 파일을 받는다.
 * 파일을 고쳤는데 브라우저가 옛날 화면을 계속 보여주면 이 숫자를 올릴 것.
 */

const CACHE_NAME = "banana-shell-v11";

const SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_FILES))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
      )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;

  // API 호출(POST /predict 등)은 절대 캐시하지 않는다.
  // 캐시하면 예전 판별 결과가 계속 돌아오는 황당한 버그가 생긴다.
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // 백엔드는 다른 도메인 -> 통과

  // 껍데기 파일은 캐시 우선, 없으면 네트워크
  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request))
  );
});
