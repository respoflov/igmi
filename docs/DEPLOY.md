# 인터넷에 올리기 (배포 가이드)

이 앱은 **화면과 서버가 한 쌍**입니다. 그래서 올릴 곳도 두 군데입니다.

```
[사람]  ──►  GitHub Pages          ──►  Render
             화면(HTML/CSS/JS)           서버(FastAPI + YOLO11n)
             무료 · 항상 켜져 있음        무료 · 안 쓰면 잠듦
```

> **왜 한 곳에 못 올리나?** GitHub Pages 는 파일을 나눠주기만 할 뿐 프로그램을
> 실행하지 못합니다. YOLO 추론은 프로그램 실행이라 서버가 필요합니다.
> 반대로 Render 는 컨테이너를 띄워 프로그램을 실행해 주는 곳입니다.

전체 소요 시간은 **20~30분** 정도이고, 대부분은 서버가 빌드되는 걸 기다리는 시간입니다.

---

## 1단계 — 백엔드를 Render 에 올리기

> **왜 Hugging Face Spaces 가 아닌가 (2026-08-31 확인)**
> HF Spaces 는 **Docker Space 가 유료(PRO) 전용**으로 바뀌었습니다. 무료는
> Static(정적 파일)뿐이라 파이썬을 실행할 수 없습니다. 그래서 Render 로 바꿉니다.
> Render 는 **GitHub 저장소를 그대로 연결**하므로 파일을 따로 올릴 필요도 없어
> 오히려 더 간단합니다.

### 1-1. 가입하고 서비스 만들기

1. <https://render.com> → **Get Started** → **GitHub 계정으로 로그인**
2. 대시보드에서 **New +** → **Web Service**
3. **respoflov/igmi** 저장소를 고릅니다. (처음이면 Render 에 저장소 접근 권한을
   허용하라는 화면이 먼저 나옵니다)

### 1-2. 설정값

| 항목 | 값 |
| --- | --- |
| Name | `banana-api` (주소에 쓰입니다) |
| Region | `Singapore` (한국에서 가장 가까움) |
| Branch | `main` |
| Language / Runtime | **Docker** |
| Dockerfile Path | `./backend/Dockerfile` |
| Docker Build Context Directory | `./backend` |
| Instance Type | **Free** |

> **Dockerfile Path 와 Build Context 를 꼭 바꾸세요.** 기본값은 저장소 최상위인데,
> 우리 Dockerfile 은 `backend/` 안에 있습니다. 이걸 안 바꾸면 빌드가 실패합니다.

### 1-3. 환경변수

같은 화면 아래 **Environment Variables** 에서 **Add Environment Variable**:

| Key | Value |
| --- | --- |
| `BANANA_ALLOW_ORIGINS` | `https://respoflov.github.io` |

> **이게 무슨 설정인가** — 브라우저는 "화면 주소와 서버 주소가 다르면" 기본적으로
> 요청을 막습니다(보안 장치). 서버 쪽에서 "이 주소는 괜찮다"고 명시해야 통과합니다.
> **증상이 '아무 반응 없음'이라 원인을 찾기 가장 어려운 항목**이니 빼먹지 마세요.

### 1-4. 배포와 확인

**Create Web Service** 를 누르면 빌드가 시작됩니다. **10~15분** 걸립니다
(PyTorch 를 받느라 오래 걸립니다). 로그에 아래가 뜨면 성공입니다.

```
YOLO 모델 로딩 완료
cooking 테이블을 19개 행으로 갱신했습니다.
banana_fact 테이블을 100개 행으로 갱신했습니다.
INFO:     Application startup complete.
```

주소는 이 형태입니다 — **적어두세요.**

```
https://banana-api.onrender.com
```

뒤에 `/health` 를 붙여 열어 `{"status":"healthy"}` 가 나오면 서버가 살아 있는 겁니다.
`/docs` 를 열면 사진을 넣어 직접 판별해볼 수 있는 화면이 나옵니다.

### 백엔드를 올릴 다른 곳

Render 에서 막히면 아래도 같은 Dockerfile 을 그대로 씁니다. **파일을 옮길 필요가 없습니다.**

| 곳 | 무료 조건 | 메모 |
| --- | --- | --- |
| **Render** | 월 750시간, 15분 무요청 시 잠듦 | 이 문서의 기본안 |
| **Koyeb** | 서비스 1개, 잠듦 | 설정 방식이 Render 와 비슷 |
| **Google Cloud Run** | 월 200만 요청 | 카드 등록 필요. 잠들지 않게 설정 가능 |
| **Hugging Face Spaces** | **유료(PRO) 전용** | 2026-08-31 기준 Docker Space 는 무료 아님 |

**발표 당일 백업** — 인터넷 배포가 막히면 내 PC 에서 서버를 켜고 터널로 임시 주소를
뚫는 방법이 있습니다. 그 PC 가 켜져 있는 동안만 동작합니다.

```bat
REM 터미널 1 — 백엔드를 컨테이너로 실행
docker run --rm -p 8000:7860 -e BANANA_ALLOW_ORIGINS=https://respoflov.github.io banana-api

REM 터미널 2 — 임시 공개 주소 만들기 (cloudflared 설치 필요)
cloudflared tunnel --url http://127.0.0.1:8000
```

## 2단계 — 프런트엔드를 GitHub Pages 에 올리기

1. <https://github.com/respoflov/igmi/settings/pages> 로 갑니다.
   (저장소 → **Settings** → 왼쪽 메뉴 **Pages**)
2. **Source** 를 `Deploy from a branch` 로 둡니다.
3. **Branch** 를 `main` / `/ (root)` 로 고르고 **Save**.
4. 1~3분 뒤 <https://respoflov.github.io/igmi/> 가 열립니다.

저장소 최상위의 `index.html` 이 `frontend/index.html` 로 넘겨주므로 바로 앱 화면이 뜹니다.

---

## 3단계 — 화면과 서버 연결하기

앱 화면 맨 아래 **🔌 분석 서버 연결** 카드에 1-4 에서 받은 주소를 넣습니다.

```
https://banana-api.onrender.com
```

입력 칸에서 빠져나오면(다른 곳 클릭) 오른쪽 배지가 **연결됨** 으로 바뀌고,
조리법·바나나 상식이 채워집니다. 주소는 그 브라우저에만 저장되므로 한 번만 넣으면 됩니다.

> 주소 뒤에 `/` 를 붙이지 마세요. 붙여도 자동으로 떼어냅니다.

이제 사진을 올리고 **분석하기** 를 누르면 인터넷 너머의 서버가 판별해 줍니다.

---

## 발표·시연 전 체크리스트

- [ ] 시연 **10분 전**에 `https://banana-api.onrender.com/health` 를 한 번 엽니다.
      무료 등급은 한동안 요청이 없으면 잠들고, 깨우는 데 **30초~1분**이 걸립니다.
      미리 깨워두지 않으면 첫 시연에서 그 시간을 그대로 기다리게 됩니다.
- [ ] 판별용 사진을 미리 폰·PC 에 준비해 둡니다.
- [ ] 폰에서 <https://respoflov.github.io/igmi/> 를 열고 브라우저 메뉴 →
      **홈 화면에 추가** 가 되는지 확인합니다 (PWA 동작 확인).

---

## 문제가 생기면

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| 배지가 계속 **연결 안 됨** | 주소 오타, 또는 서버가 잠듦 | 주소를 직접 브라우저로 열어 `/health` 확인. 잠든 거면 30초 기다렸다 다시 |
| 분석 버튼을 눌러도 아무 반응이 없음 | CORS 설정 누락 | Render → Environment 에 `BANANA_ALLOW_ORIGINS` 가 있는지 확인 |
| 브라우저 콘솔에 `CORS policy` 오류 | 같은 원인 | 위와 같음. 주소 끝에 `/` 가 붙어 있지 않은지도 확인 |
| 빌드가 `failed to read dockerfile` 로 실패 | Dockerfile Path / Build Context 를 안 바꿈 | `./backend/Dockerfile` 과 `./backend` 로 설정 |
| Pages 주소가 404 | Pages 를 안 켰거나 아직 빌드 중 | Settings → Pages 에서 초록색 안내문이 뜰 때까지 기다림 |
| 후숙 기간 카드가 비어 있음 | `banana_riping.xlsx` 없음 (알려진 제약) | [SETUP.md](SETUP.md#후숙-기간-표-banana_ripingxlsx) 참고 |
| 판별 기록이 사라짐 | 컨테이너 재시작 시 초기화됨 | 정상입니다. 화면의 기록은 브라우저에 따로 저장돼 남아 있습니다 |

---

## 배포에서 달라지는 것

로컬 개발과 배포는 설정 몇 개만 다릅니다. **코드는 같습니다.**

| 항목 | 로컬 | 배포 (컨테이너) |
| --- | --- | --- |
| 데이터베이스 | PostgreSQL (`.env` 의 `DATABASE_URL`) | SQLite (설정 없으면 자동) |
| 패키지 목록 | `requirements.txt` | `requirements-deploy.txt` (Dockerfile 이 사용) |
| PyTorch | 일반 설치 | CPU 전용 빌드 (Dockerfile 에서 별도 설치) |
| CORS | localhost:5500 등 | `BANANA_ALLOW_ORIGINS` 환경변수 |
| 포트 | 8000 | 호스트가 `PORT` 로 지정 (없으면 7860) |
| 저장 파일 | 계속 남음 | 재시작 시 초기화 |

모델을 새로 학습해 교체할 때는 **`weights/best.pt` 파일만 바꿔 커밋·푸시하면 됩니다.**
Render 가 푸시를 감지해 자동으로 다시 배포합니다. 코드는 파일 경로만 참조하므로 수정할 게 없습니다.
