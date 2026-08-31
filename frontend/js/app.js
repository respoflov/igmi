const DEFAULT_API = "http://127.0.0.1:8000";
const HISTORY_KEY = "bananaInferenceHistoryV1";
const KO = { unripe:"미숙성", ripe:"숙성", overripe:"과숙성", rotten:"상함" };
let COOKING = {};

const $ = id => document.getElementById(id);
const $file=$("file"), $go=$("go"), $status=$("status"), $preview=$("preview");
const $previewCard=$("previewCard"), $resultCard=$("resultCard"), $rows=$("rows");
const $summary=$("summary"), $filelabel=$("filelabel"), $process=$("process");
const $tips=$("tips"), $tipCard=$("tipCard"), $tipToggle=$("tipToggle"), $tipCaution=$("tipCaution"), $historyList=$("historyList");
const $ripingCard=$("ripingCard"), $ripingBody=$("ripingBody"), $ripingToggle=$("ripingToggle");
const $humiditySelect=$("humiditySelect"), $tempSelect=$("tempSelect"), $ripingResult=$("ripingResult");
const $factList=$("factList");
const $apiInput=$("apiInput"), $apiStatus=$("apiStatus");
const steps=[$("stepUpload"),$("stepModel"),$("stepResult")];

function getApiBase(){
  const fromQuery=new URLSearchParams(location.search).get("api");
  if(fromQuery) localStorage.setItem("bananaApi",fromQuery);
  return localStorage.getItem("bananaApi")||DEFAULT_API;
}

function setStatus(msg,isError=false){$status.textContent=msg||"";$status.className="status"+(isError?" err":"")}
function setStep(index){
  $process.hidden=false;
  steps.forEach((el,i)=>el.className="process-step "+(i<index?"done":i===index?"active":""));
}
function resetProcess(){steps.forEach(el=>el.className="process-step");$process.hidden=true}

$file.addEventListener("change",()=>{
  const f=$file.files[0]; if(!f)return;
  $filelabel.textContent=f.name; $preview.src=URL.createObjectURL(f);
  $previewCard.hidden=false;$resultCard.hidden=true;$tipCard.hidden=true;$ripingCard.hidden=true;ripingEligible=false;$go.disabled=false;
  resetProcess();setStatus("");
});

$go.addEventListener("click",async()=>{
  const f=$file.files[0];if(!f)return;
  $go.disabled=true;setStep(0);setStatus("이미지를 준비하고 있습니다...");
  await sleep(180);setStep(1);setStatus("🤖 YOLO11n 모델로 객체를 탐지하고 있습니다...");
  const form=new FormData();form.append("file",f);
  try{
    const res=await fetch(getApiBase()+"/predict/",{method:"POST",body:form});
    if(!res.ok){const text=await res.text();throw new Error("서버가 "+res.status+" 를 돌려줬습니다. "+text.slice(0,200))}
    const data=await res.json();setStep(2);setStatus("분석 결과를 정리하고 있습니다...");
    render(data);await saveHistory(f,data);applyRipingVisibility(data);loadFacts();setStatus("분석이 완료되었습니다.");
    setTimeout(resetProcess,700);
  }catch(e){
    resetProcess();setStatus("실패: "+e.message+"  (백엔드 주소와 서버 상태를 확인하세요)",true);
  }finally{$go.disabled=false}
});
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function dominantClass(detections){
  if(!detections.length)return null;
  const counts={};detections.forEach(d=>counts[d.class_name]=(counts[d.class_name]||0)+1);
  return Object.entries(counts).sort((a,b)=>b[1]-a[1])[0][0];
}
function render(data){
  $rows.innerHTML="";const detections=data.detections||[];
  if(!detections.length){$summary.textContent="바나나를 찾지 못했습니다.";$resultCard.hidden=false;$tipCard.hidden=true;return}
  const counts={};detections.forEach(d=>counts[d.class_name]=(counts[d.class_name]||0)+1);
  const parts=Object.entries(counts).map(([k,v])=>`<span class="pill">${KO[k]||escapeHtml(k)} ${v}개</span>`).join(" ");
  $summary.innerHTML=`총 <b>${detections.length}</b>개 탐지 &nbsp; ${parts}`;
  detections.forEach((d,i)=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${i+1}</td><td>${KO[d.class_name]||escapeHtml(d.class_name)}</td><td>${(Number(d.confidence)*100).toFixed(1)}%</td>`;$rows.appendChild(tr)});
  const classes=[...new Set(detections.map(d=>d.class_name))];
  $tips.innerHTML=classes.map(c=>{
    const items=COOKING[c]&&COOKING[c].length?COOKING[c]:[{title:KO[c]||c,description:"분석된 숙성 상태에 맞춰 상태를 확인하세요."}];
    const tip=items[Math.floor(Math.random()*items.length)];
    return `<div class="tip"><span class="pill">${escapeHtml(KO[c]||c)}</span><h3>${escapeHtml(tip.title)}</h3><p>${escapeHtml(tip.description)}</p></div>`;
  }).join("");
  $tips.classList.add("collapsed");$tipToggle.setAttribute("aria-expanded","false");
  const resultClass=dominantClass(detections)||data.predicted_class;
  $tipCaution.hidden=resultClass!=="unripe";
  $resultCard.hidden=false;$tipCard.hidden=false;
}

async function loadCookingTips(){
  try{
    const res=await fetch(getApiBase()+"/cooking/");
    if(!res.ok)return;
    COOKING=await res.json();
  }catch(e){console.warn("조리 방법을 불러오지 못했습니다.",e)}
}
loadCookingTips();

$tipToggle.addEventListener("click",()=>{
  const collapsed=$tips.classList.toggle("collapsed");
  $tipToggle.setAttribute("aria-expanded",String(!collapsed));
});

$ripingToggle.addEventListener("click",()=>{
  const collapsed=$ripingBody.classList.toggle("collapsed");
  $ripingToggle.setAttribute("aria-expanded",String(!collapsed));
});

async function loadFacts(){
  try{
    const res=await fetch(getApiBase()+"/facts/random?max_chars=50");
    if(!res.ok)return;
    const data=await res.json();
    $factList.innerHTML=(data.facts||[]).map(f=>`<li>${escapeHtml(f)}</li>`).join("");
  }catch(e){console.warn("바나나 상식을 불러오지 못했습니다.",e)}
}
loadFacts();

const NO_RIPING_CLASSES=new Set(["overripe","rotten"]);
let ripingEligible=false;
function isRipingEligible(data){
  const detections=data.detections||[];
  const cls=dominantClass(detections)||data.predicted_class;
  return !!cls&&cls!=="unknown"&&!NO_RIPING_CLASSES.has(cls);
}
function applyRipingVisibility(data){
  ripingEligible=isRipingEligible(data);
  if(ripingEligible)loadRipingEstimate();
  else $ripingCard.hidden=true;
}

async function loadRipingOptions(){
  try{
    const res=await fetch(getApiBase()+"/ripening/options");
    if(!res.ok)return;
    const data=await res.json();
    $humiditySelect.innerHTML=data.humidity_options.map(o=>`<option value="${o.key}">${escapeHtml(o.label)}</option>`).join("");
    $tempSelect.innerHTML=data.temp_options.map(o=>`<option value="${o.key}">${escapeHtml(o.label)}</option>`).join("");
    if(data.humidity_options.some(o=>o.key==="60_70"))$humiditySelect.value="60_70";
    if(data.temp_options.some(o=>o.key==="18_20"))$tempSelect.value="18_20";
  }catch(e){console.warn("보관 조건 목록을 불러오지 못했습니다.",e)}
}
async function loadRipingEstimate(){
  if(!ripingEligible||!$humiditySelect.value||!$tempSelect.value)return;
  $ripingCard.hidden=false;$ripingResult.textContent="후숙 예상 기간을 계산하고 있습니다...";
  try{
    const params=new URLSearchParams({humidity_key:$humiditySelect.value,temp_key:$tempSelect.value});
    const res=await fetch(getApiBase()+"/ripening/estimate?"+params.toString());
    if(!res.ok)throw new Error("서버가 "+res.status+" 를 돌려줬습니다.");
    const d=await res.json();
    const range=(d.min_days===d.max_days)?`${d.min_days}일`:`${d.min_days}~${d.max_days}일`;
    const headline=(d.temp_key==="under_10")
      ?`저온 장애로 인해 <b>${range} 전후</b>로 갈변이 시작됩니다.`
      :`<b>${range}</b> 후 갈변됩니다.`;
    $ripingResult.innerHTML=`${headline}<small>${escapeHtml(d.humidity_label)} · ${escapeHtml(d.temp_label)}${d.note?" — "+escapeHtml(d.note):""}</small>`;
  }catch(e){
    $ripingResult.textContent="후숙 예상 기간을 불러오지 못했습니다: "+e.message;
  }
}
$humiditySelect.addEventListener("change",loadRipingEstimate);
$tempSelect.addEventListener("change",loadRipingEstimate);
loadRipingOptions();

function readHistory(){try{return JSON.parse(localStorage.getItem(HISTORY_KEY)||"[]")}catch{return[]}}
function writeHistory(items){localStorage.setItem(HISTORY_KEY,JSON.stringify(items.slice(0,20)))}
async function fileToDataURL(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsDataURL(file)})}
async function saveHistory(file,data){
  try{
    const image=await fileToDataURL(file);
    const detections=data.detections||[];
    const item={id:crypto.randomUUID?crypto.randomUUID():String(Date.now()),createdAt:new Date().toISOString(),name:file.name,image,data,summary:dominantClass(detections)};
    const items=readHistory();items.unshift(item);writeHistory(items);renderHistory();
  }catch(e){console.warn("기록 저장 실패",e)}
}
function renderHistory(){
  const items=readHistory();
  if(!items.length){$historyList.innerHTML='<p class="empty-history">아직 분석 기록이 없습니다.</p>';return}
  $historyList.innerHTML="";
  items.forEach(item=>{
    const el=document.createElement("div");el.className="history-item";
    el.innerHTML=`<img src="${item.image}" alt="기록 이미지"><button class="history-meta"><strong>${KO[item.summary]||item.summary||"분석 결과"}</strong><small>${new Date(item.createdAt).toLocaleString("ko-KR")}</small></button><button class="history-delete" title="삭제">✕</button>`;
    el.querySelector(".history-meta").addEventListener("click",()=>openHistory(item.id));
    el.querySelector(".history-delete").addEventListener("click",()=>deleteHistory(item.id));
    $historyList.appendChild(el);
  });
}
function openHistory(id){
  const item=readHistory().find(v=>v.id===id);if(!item)return;
  $preview.src=item.image;$previewCard.hidden=false;render(item.data);applyRipingVisibility(item.data);loadFacts();setStatus("저장된 분석 결과를 불러왔습니다.");window.scrollTo({top:0,behavior:"smooth"});
}
function deleteHistory(id){writeHistory(readHistory().filter(v=>v.id!==id));renderHistory()}
$("clearHistory").addEventListener("click",()=>{if(confirm("모든 분석 기록을 삭제할까요?")){localStorage.removeItem(HISTORY_KEY);renderHistory()}})
renderHistory();

// ---- 분석 서버 연결 ----------------------------------------------------
// 화면(GitHub Pages)과 서버(HF Spaces)는 주소가 다르다. 어느 서버를 부를지
// 사용자가 직접 넣을 수 있게 하고, 넣은 값은 이 브라우저에만 저장한다.
function setApiBase(value){
  const v=String(value||"").trim().replace(/\/+$/,"");
  if(v) localStorage.setItem("bananaApi",v); else localStorage.removeItem("bananaApi");
}
function setApiState(state,label){$apiStatus.dataset.state=state;$apiStatus.textContent=label}
async function pingApi(timeoutMs){
  const ctrl=new AbortController();
  const timer=setTimeout(()=>ctrl.abort(),timeoutMs);
  try{
    const res=await fetch(getApiBase()+"/health",{cache:"no-store",signal:ctrl.signal});
    return res.ok;
  }catch(e){return false}
  finally{clearTimeout(timer)}
}
// 무료 서버는 한동안 요청이 없으면 잠든다. 깨어나는 데 1분쯤 걸리는데, 그동안
// 그냥 "연결 안 됨"이라고만 보여주면 고장난 줄 알게 된다. 그래서 한 번 실패하면
// "깨우는 중"으로 바꾸고 1분간 더 두드려본다.
async function checkApi(){
  setApiState("checking","확인 중");
  if(await pingApi(8000)){setApiState("ok","연결됨");return true}
  setApiState("waking","깨우는 중");
  for(let i=0;i<10;i++){
    await sleep(6000);
    if(await pingApi(8000)){setApiState("ok","연결됨");return true}
  }
  setApiState("down","연결 안 됨");
  return false;
}
async function refreshFromApi(){
  if(!await checkApi())return;
  await loadCookingTips(); loadFacts(); loadRipingOptions();
}
$apiInput.value=localStorage.getItem("bananaApi")||"";
$apiInput.placeholder=DEFAULT_API;
$apiInput.addEventListener("change",()=>{setApiBase($apiInput.value);refreshFromApi()});
$apiStatus.addEventListener("click",()=>{if($apiStatus.dataset.state!=="waking")refreshFromApi()});
$apiStatus.title="눌러서 다시 확인";
refreshFromApi();

if("serviceWorker" in navigator && location.protocol.startsWith("http")){
  window.addEventListener("load",()=>navigator.serviceWorker.register("./sw.js").catch(e=>console.warn("Service Worker 등록 실패:",e)));
}
