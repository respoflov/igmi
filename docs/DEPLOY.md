# 인터넷에 올리기 (배포 가이드)

이 앱은 **화면과 서버가 한 쌍**입니다. 그래서 올릴 곳도 두 군데입니다.

```
[사람]  ──►  GitHub Pages          ──►  Hugging Face Spaces
             화면(HTML/CSS/JS)           서버(FastAPI + YOLO11n)
             무료 · 항상 켜져 있음        무료 · 안 쓰면 잠듦
```

> **왜 한 곳에 못 올리나?** GitHub Pages 는 파일을 나눠주기만 할 뿐 프로그램을
> 실행하지 못합니다. YOLO 추론은 프로그램 실행이라 서버가 필요합니다.
> 반대로 Hugging Face Spaces 는 프로그램을 실행해 주는 곳입니다.

전체 소요 시간은 **20~30분** 정도이고, 대부분은 서버가 빌드되는 걸 기다리는 시간입니다.

---

## 1단계 — 백엔드를 Hugging Face Spaces 에 올리기

### 1-1. 계정과 Space 만들기

1. <https://huggingface.co/join> 에서 가입합니다. **신용카드는 필요 없습니다.**
2. 오른쪽 위 프로필 → **New Space**
3. 아래처럼 채웁니다.

   | 항목 | 값 |
   | --- | --- |
   | Space name | `banana-api` |
   | License | `agpl-3.0` |
   | Select the Space SDK | **Docker** → **Blank** |
   | Space hardware | `CPU basic · Free` |
   | Visibility | `Public` |

4. **Create Space** 를 누릅니다.

### 1-2. 파일 올리기

만들어진 Space 화면에서 **Files** 탭 → **Add file** → **Upload files** 를 누르고,
바탕화면의 **`hf_space` 폴더 안의 내용물 전부**를 끌어다 놓습니다.

폴더 구조가 그대로 유지돼야 합니다. 웹에서 폴더째 올리는 게 잘 안 되면,
`Add file → Create a new file` 로 경로에 `database/database.py` 처럼 슬래시를 넣어
만들 수도 있지만 파일이 30개라 번거롭습니다. **끌어다 놓기를 먼저 시도하세요.**

올려야 할 것 (총 5.4MB):

```
Dockerfile              README.md               requirements-deploy.txt
main.py                 config.py
database/  models/  routers/  schemas/  services/     (파이썬 파일들)
weights/best.pt         (5.2MB — Git LFS 없이 그냥 올라갑니다)
```

맨 아래 **Commit changes to main** 을 누르면 빌드가 시작됩니다.

### 1-3. CORS 설정

빌드가 도는 동안 해두면 됩니다. **Settings** 탭 → **Variables and secrets** →
**New variable**:

| Name | Value |
| --- | --- |
| `BANANA_ALLOW_ORIGINS` | `https://respoflov.github.io` |

> **이게 무슨 설정인가** — 브라우저는 "화면 주소와 서버 주소가 다르면" 기본적으로
> 요청을 막습니다(보안 장치). 서버 쪽에서 "이 주소는 괜찮다"고 명시해야 통과합니다.
> **증상이 '아무 반응 없음'이라 원인을 찾기 가장 어려운 항목**이니 빼먹지 마세요.

변수를 추가하면 Space 가 자동으로 재시작됩니다.

### 1-4. 빌드 확인

**Logs** 탭에서 진행 상황이 보입니다. **5~10분** 걸립니다 (torch 를 받느라 오래 걸림).
`Application startup complete` 가 뜨면 성공입니다.

주소는 이 형태입니다 — **이 주소를 적어두세요.**

```
https://<계정이름>-banana-api.hf.space
```

브라우저에서 뒤에 `/health` 를 붙여 열어보고 아래가 나오면 서버가 살아 있는 겁니다.

```json
{"status":"healthy"}
```

`/docs` 를 열면 API 를 직접 호출해볼 수 있는 화면이 나옵니다. 여기서 사진을 넣어
`POST /predict/` 를 눌러보면 화면 없이도 판별이 되는지 확인할 수 있습니다.

---

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
https://<계정이름>-banana-api.hf.space
```

입력 칸에서 빠져나오면(다른 곳 클릭) 오른쪽 배지가 **연결됨** 으로 바뀌고,
조리법·바나나 상식이 채워집니다. 주소는 그 브라우저에만 저장되므로 한 번만 넣으면 됩니다.

> 주소 뒤에 `/` 를 붙이지 마세요. 붙여도 자동으로 떼어냅니다.

이제 사진을 올리고 **분석하기** 를 누르면 인터넷 너머의 서버가 판별해 줍니다.

---

## 발표·시연 전 체크리스트

- [ ] 시연 **10분 전**에 `https://<계정>-banana-api.hf.space/health` 를 한 번 엽니다.
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
| 분석 버튼을 눌러도 아무 반응이 없음 | CORS 설정 누락 | HF Space → Settings → Variables 에 `BANANA_ALLOW_ORIGINS` 가 있는지 확인 |
| 브라우저 콘솔에 `CORS policy` 오류 | 같은 원인 | 위와 같음. 주소 끝에 `/` 가 붙어 있지 않은지도 확인 |
| HF 빌드가 `No such file: weights/best.pt` 로 실패 | 가중치를 안 올렸거나 경로가 틀림 | Files 탭에서 `weights/best.pt` 가 있는지 확인 |
| Pages 주소가 404 | Pages 를 안 켰거나 아직 빌드 중 | Settings → Pages 에서 초록색 안내문이 뜰 때까지 기다림 |
| 후숙 기간 카드가 비어 있음 | `banana_riping.xlsx` 없음 (알려진 제약) | [SETUP.md](SETUP.md#후숙-기간-표-banana_ripingxlsx) 참고 |
| 판별 기록이 사라짐 | 컨테이너 재시작 시 초기화됨 | 정상입니다. 화면의 기록은 브라우저에 따로 저장돼 남아 있습니다 |

---

## 배포에서 달라지는 것

로컬 개발과 배포는 설정 몇 개만 다릅니다. **코드는 같습니다.**

| 항목 | 로컬 | 배포 (HF Spaces) |
| --- | --- | --- |
| 데이터베이스 | PostgreSQL (`.env` 의 `DATABASE_URL`) | SQLite (설정 없으면 자동) |
| 패키지 목록 | `requirements.txt` | `requirements-deploy.txt` (Dockerfile 이 사용) |
| PyTorch | 일반 설치 | CPU 전용 빌드 (Dockerfile 에서 별도 설치) |
| CORS | localhost:5500 등 | `BANANA_ALLOW_ORIGINS` 환경변수 |
| 포트 | 8000 | 7860 (HF Spaces 규약) |
| 저장 파일 | 계속 남음 | 재시작 시 초기화 |

모델을 새로 학습해 교체할 때는 **`weights/best.pt` 파일만 바꿔 올리면 됩니다.**
코드는 파일 경로만 참조하므로 수정할 게 없습니다.
