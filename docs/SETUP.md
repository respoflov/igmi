# 설치 · 실행 가이드

처음 이 저장소를 받은 사람이 순서대로 따라 하면 실행되도록 적었습니다.
명령어는 **Windows 명령 프롬프트(cmd)** 기준입니다. macOS·Linux 는 경로 구분자(`\` → `/`)와
가상환경 진입 명령(`.venv\Scripts\activate` → `source .venv/bin/activate`)만 다릅니다.

## 0. 준비물

| 항목 | 버전 | 확인 방법 |
| --- | --- | --- |
| Python | 3.12 이상 | `python --version` |
| PostgreSQL | 14 이상 (**선택**) | `psql --version` |

> **PostgreSQL 은 안 깔아도 됩니다.** 접속 주소를 주지 않으면 `backend/banana.db` 라는
> SQLite 파일 하나로 알아서 돕니다. 처음 돌려보는 거라면 3·4단계를 건너뛰고
> 바로 5단계로 가세요. 판별·조리법·상식이 전부 그대로 동작합니다.

## 1. 가상환경 만들기

> **가상환경이란?** 프로젝트 폴더와는 별개로 존재하는, 이 프로젝트 전용 파이썬 패키지 창고입니다.
> 여기에 라이브러리를 담아두면 컴퓨터 전체의 파이썬 환경을 건드리지 않고, 프로젝트마다
> 다른 버전을 쓸 수 있습니다. 창고를 만드는 게 `venv`, 창고를 열어 쓰겠다고 선언하는 게 `activate` 입니다.

저장소 최상위 폴더에서:

```bat
python -m venv .venv
.venv\Scripts\activate
```

프롬프트 앞에 `(.venv)` 가 붙으면 성공입니다.
**앞으로 나오는 모든 `pip` · `python` 명령은 이 상태에서 실행합니다.**

PowerShell 을 쓰는데 `activate` 가 "스크립트를 실행할 수 없습니다" 라며 막히면, 그 창에서만 한 번 풀어줍니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 2. 라이브러리 설치

```bat
pip install -r backend\requirements.txt
```

`ultralytics` 가 PyTorch 를 함께 받아오기 때문에 **수백 MB, 몇 분** 걸립니다. 처음 한 번만 그렇습니다.

## 3. PostgreSQL 데이터베이스 만들기

`banana_db` 라는 빈 데이터베이스만 있으면 됩니다. 테이블은 서버가 처음 뜰 때 알아서 만듭니다.

```bat
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost
```

비밀번호를 입력해 접속한 뒤:

```sql
CREATE DATABASE banana_db;
\q
```

> PostgreSQL 설치 경로는 버전마다 다릅니다. `18` 부분을 설치된 버전 번호로 바꾸세요.

## 4. 환경변수 파일 만들기

```bat
copy backend\.env.example backend\.env
```

만들어진 `backend\.env` 를 열어 `DATABASE_URL` 의 `CHANGE_ME` 자리에 **PostgreSQL 비밀번호**를 넣습니다.

```
DATABASE_URL=postgresql://postgres:내비밀번호@localhost:5432/banana_db
```

> `.env` 는 `.gitignore` 에 등록돼 있어 커밋되지 않습니다.
> 비밀번호를 `.env.example` 쪽에 적지 마세요 — 그 파일은 저장소에 올라갑니다.

## 5. 실행

터미널 두 개를 띄웁니다. **두 창 모두 `.venv\Scripts\activate` 를 먼저 실행**한 상태여야 합니다.

**터미널 1 — 백엔드**

```bat
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

처음 실행하면 이런 로그가 지나갑니다.

```
YOLO 모델 로딩 중...
YOLO 모델 로딩 완료
cooking 테이블을 ..개 행으로 갱신했습니다.
banana_fact 테이블을 ..개 행으로 갱신했습니다.
Uvicorn running on http://127.0.0.1:8000
```

**터미널 2 — 프런트엔드**

```bat
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

브라우저에서 <http://127.0.0.1:5500/index.html> 를 엽니다.

> `file://` 로 `index.html` 을 직접 열면 안 됩니다. 서비스 워커와 `fetch` 가 동작하지 않습니다.
> 반드시 위처럼 http 서버를 통해 열어야 합니다.

## 6. 잘 도는지 확인하기

| 확인할 것 | 방법 | 기대 결과 |
| --- | --- | --- |
| 백엔드 | <http://127.0.0.1:8000/health> | `{"status":"healthy"}` |
| API 문서 | <http://127.0.0.1:8000/docs> | Swagger 화면 |
| 시딩 | <http://127.0.0.1:8000/cooking/> | 숙성도별 조리법 JSON |
| 전체 | 앱에서 바나나 사진 업로드 | 결과 표 + 조리법 카드 |

## 코드를 고치지 않고 동작을 바꾸는 스위치 (환경변수)

`backend/.env` 에 적거나, 배포처의 환경변수 설정에 넣습니다. 전부 선택 항목입니다.

| 이름 | 기본값 | 하는 일 |
| --- | --- | --- |
| `DATABASE_URL` | (없으면 SQLite) | DB 접속 주소 |
| `MODEL_PATH` | `weights/best.pt` | 가중치 경로 (`backend/` 기준) |
| `BANANA_CONF` | `0.15` | 이 값보다 확신이 낮은 탐지는 버림 |
| `BANANA_IOU` | `0.7` | 겹친 박스를 합치는 기준 |
| `BANANA_ALLOW_ORIGINS` | `*` | API 를 호출할 수 있는 화면 주소 |
| `UPLOAD_DIR` / `RESULT_DIR` | `storage/uploads` · `storage/results` | 이미지 저장 위치 |
| `RIPING_XLSX_PATH` | 저장소 최상위의 `banana_riping.xlsx` | 후숙 기간 표 원본 |

## 후숙 기간 표 (`banana_riping.xlsx`)

`/ripening` 기능은 엑셀 파일 하나를 원본으로 씁니다. **이 파일은 저장소에 포함돼 있지 않습니다.**
없어도 서버는 정상적으로 뜨고, 아래 메시지를 한 줄 남긴 뒤 후숙 카드만 비어 있게 됩니다.

```
banana_riping.xlsx 를 찾을 수 없습니다: ...
```

파일을 만들려면 **저장소 최상위**에 `banana_riping.xlsx` 라는 이름으로 두고, 첫 시트를 아래 형태로 채웁니다.
(1행은 머리글이며 내용은 읽지 않습니다. 2행부터가 데이터입니다.)

| A열 (습도) | B열 | C열 | D열 | E열 | F열 |
| --- | --- | --- | --- | --- | --- |
| 습도 | 10℃ 이하 | 13~15℃ | 18~20℃ | 25~30℃ | 35℃ 이상 |
| `85~90%` | `10일` | `14일` | `7일` | `4일` | `2일` |
| `80~85%` | ... | ... | ... | ... | ... |
| `60~70%` | ... | ... | ... | ... | ... |
| `50~60%` | ... | ... | ... | ... | ... |

- A열의 습도 표기에서 **앞의 숫자**를 뽑아 키를 만듭니다 (`85` → `85_90`, `80` → `80_85`, `60` → `60_70`, `50` → `50_60`).
- B~F열 각 칸은 **첫 줄에서 "N일" 또는 "N~M일" 형태를 찾아** 기간으로 읽습니다.
- 첫 줄 아래에 줄바꿈으로 덧붙인 문장이 있으면 **비고(note)** 로 함께 저장돼 화면에 표시됩니다.

파일을 다른 위치에 두고 싶으면 `backend/.env` 에 경로를 지정합니다.

```
RIPING_XLSX_PATH=C:\어딘가\banana_riping.xlsx
```

> 시딩은 **테이블이 비어 있을 때만** 실행됩니다. 엑셀을 고친 뒤 다시 넣으려면
> `DELETE FROM banana_riping;` 을 실행하고 서버를 재시작하세요.

## 자주 막히는 곳

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| 서버 시작 시 `could not connect to server` | PostgreSQL 이 꺼져 있거나 `DATABASE_URL` 이 틀림 | 서비스 실행 여부와 `.env` 의 비밀번호·DB 이름 확인 |
| 서버 시작 시 `database "banana_db" does not exist` | DB 를 안 만듦 | 3단계의 `CREATE DATABASE banana_db;` 실행 |
| 앱에서 "실패: Failed to fetch" | 백엔드가 안 떠 있거나 주소가 다름 | 터미널 1 확인. 화면 아래 "분석 서버 연결"에 주소를 넣으세요 |
| 브라우저 콘솔에 CORS 오류 | `BANANA_ALLOW_ORIGINS` 를 좁혀뒀는데 화면 주소가 그와 다름 | 그 변수를 지우거나(전체 허용), 경로 없는 주소로 고침 |
| 화면을 고쳤는데 옛날 화면이 계속 나옴 | 서비스 워커가 캐시한 껍데기 | `frontend/sw.js` 의 `CACHE_NAME` 버전 숫자를 올리고 새로고침 |
| 후숙 기간 카드가 비어 있음 | `banana_riping.xlsx` 없음 | 위 "후숙 기간 표" 항목 참고 |
| 첫 판별이 유난히 느림 | YOLO 모델을 메모리에 올리는 중 | 정상입니다. 서버당 최초 1회만 그렇습니다 |
