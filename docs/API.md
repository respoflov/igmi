# API 레퍼런스

| 어디서 도는가 | 기본 주소 |
| --- | --- |
| 내 컴퓨터 | `http://127.0.0.1:8000` |
| 배포된 서버 | `https://igmi.onrender.com` |

주소 뒤에 `/docs` 를 붙이면 브라우저에서 직접 호출해볼 수 있는 화면이 나옵니다.

- 모든 응답은 JSON 입니다.
- 인증은 없습니다. 누구나 호출할 수 있으므로 로컬·내부망 전제로 사용하세요.
- CORS 는 기본적으로 **모든 주소를 허용**합니다. 좁히려면 `BANANA_ALLOW_ORIGINS` 환경변수에 주소를 넣으세요 (쉼표로 여러 개, 경로 없이 주소만).

---

## 판별

### `POST /predict/`

이미지를 올리면 YOLO11n 이 바나나를 찾아 숙성도를 판별하고, 결과를 DB와 파일로 남깁니다.

**요청** — `multipart/form-data`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `file` | 파일 | `.jpg` `.jpeg` `.png` `.webp` 만 허용 |

추론은 **confidence 0.15 / IoU 0.7** 로 돕니다. 팀에서 실측으로 확정한 값이며 근거는 `backend/config.py` 주석에 있습니다. `BANANA_CONF` · `BANANA_IOU` 환경변수로 바꿀 수 있습니다.

```bash
curl -X POST http://127.0.0.1:8000/predict/ -F "file=@banana.jpg"
```

**응답 `200`**

```json
{
  "success": true,
  "prediction_id": 12,
  "predicted_class": "ripe",
  "confidence": 0.9312,
  "detections": [
    { "class_id": 1, "class_name": "ripe",     "confidence": 0.9312 },
    { "class_id": 2, "class_name": "overripe", "confidence": 0.8047 }
  ],
  "image_path": "storage/uploads/3a88...b3a.jpg",
  "result_image_path": "storage/results/0f7f...b11.jpg"
}
```

| 필드 | 설명 |
| --- | --- |
| `predicted_class` | `detections` 중 confidence 가 가장 높은 것의 클래스 |
| `confidence` | 그 탐지의 confidence (0~1) |
| `detections` | 찾아낸 바나나 **전부**. 화면의 결과 표는 이 배열을 그립니다 |
| `image_path` | 업로드 원본. 서버 주소 뒤에 붙여 이미지로 열 수 있습니다 |
| `result_image_path` | 박스가 그려진 결과 이미지. 탐지가 0건이면 `null` |

**바나나를 못 찾은 경우** — 오류가 아니라 `200` 으로 아래처럼 돌아옵니다.

```json
{
  "success": true, "prediction_id": 13,
  "predicted_class": "unknown", "confidence": 0.0,
  "detections": [], "result_image_path": null,
  "image_path": "storage/uploads/....jpg"
}
```

**오류**

| 코드 | 언제 | 응답 |
| --- | --- | --- |
| `400` | 허용하지 않는 확장자 | `{"detail":"이미지 파일만 업로드할 수 있습니다."}` |
| `500` | 추론 또는 DB 저장 실패 | `{"detail":"<예외 메시지>"}` |

> **알아둘 점** — 파일 저장이 추론보다 먼저 일어납니다. 추론이 실패해 `500` 이 나도
> 업로드된 원본은 `storage/uploads/` 에 남습니다. 자동으로 지우지 않습니다.

---

## 판별 기록

브라우저 사이드바에 보이는 기록은 localStorage 에 저장된 것이고, 아래 API 는 **서버 DB** 쪽 기록입니다. 둘은 별개입니다.

### `GET /history/`

전체 기록을 최신순으로 돌려줍니다.

```json
[
  {
    "id": 12,
    "original_filename": "banana.jpg",
    "image_path": "storage/uploads/3a88...b3a.jpg",
    "result_image_path": "storage/results/0f7f...b11.jpg",
    "predicted_class": "ripe",
    "confidence": 0.9312,
    "created_at": "2026-08-31T09:14:22.104512"
  }
]
```

### `GET /history/{prediction_id}`

기록 1건. 없으면 `404` `{"detail":"기록을 찾을 수 없습니다."}`

### `DELETE /history/{prediction_id}`

DB 행과 함께 **업로드 원본·결과 이미지 파일도 디스크에서 삭제**합니다. 되돌릴 수 없습니다.

```json
{ "success": true, "message": "분석 기록이 삭제되었습니다." }
```

---

## 후숙 예상 기간

### `GET /ripening/options`

고를 수 있는 습도·온도 목록입니다. 습도는 DB(`banana_riping` 테이블)에서, 온도는 코드에 고정된 5구간에서 옵니다.

```json
{
  "humidity_options": [ { "key": "85_90", "label": "85~90%" } ],
  "temp_options": [
    { "key": "under_10", "label": "10°C 이하" },
    { "key": "13_15",    "label": "13°C ~ 15°C (최적)" },
    { "key": "18_20",    "label": "18°C ~ 20°C (실온)" },
    { "key": "25_30",    "label": "25°C ~ 30°C" },
    { "key": "over_35",  "label": "35°C 이상" }
  ]
}
```

> `banana_riping.xlsx` 를 넣지 않았다면 `humidity_options` 가 빈 배열로 옵니다.
> 준비 방법은 [SETUP.md](SETUP.md#후숙-기간-표-banana_ripingxlsx) 를 보세요.

### `GET /ripening/estimate`

| 쿼리 | 필수 | 값 |
| --- | --- | --- |
| `humidity_key` | ✅ | `/ripening/options` 의 `humidity_options[].key` |
| `temp_key` | ✅ | 위 5개 중 하나 |

```
GET /ripening/estimate?humidity_key=60_70&temp_key=18_20
```

```json
{
  "humidity_key": "60_70",
  "humidity_label": "60~70%",
  "temp_key": "18_20",
  "temp_label": "18°C ~ 20°C (실온)",
  "min_days": 5.0,
  "max_days": 7.0,
  "note": "에틸렌 발생이 활발해집니다",
  "raw_text": "5~7일\n• 에틸렌 발생이 활발해집니다"
}
```

- 엑셀 칸이 `5일` 처럼 한 값이면 `min_days` 와 `max_days` 가 같습니다.
- 기간을 못 읽어내면 두 값 모두 `null` 이고 `raw_text` 만 채워집니다.
- 조건에 맞는 데이터가 없으면 `404` `{"detail":"해당 보관 조건에 대한 데이터를 찾을 수 없습니다."}`

---

## 조리 · 섭취 방법

### `GET /cooking/`

숙성도를 키로 묶어 전부 돌려줍니다.

```json
{
  "unripe": [ { "title": "삶아서 먹기", "description": "껍질째 씻어 물에 15~30분 삶은 뒤 껍질을 벗겨 먹습니다." } ],
  "ripe":   [ { "title": "생과일로 바로 섭취", "description": "바로 섭취하거나 스무디·샌드위치에 활용하기 좋습니다." } ]
}
```

프런트엔드는 이 응답을 페이지 로딩 때 한 번 받아두고, 판별 결과에 해당하는 항목 중 하나를 무작위로 골라 보여줍니다.

### `GET /cooking/{ripeness_class}`

`unripe` · `ripe` · `overripe` · `rotten` 중 하나. 배열로 돌려주며, 없으면 `404`.

```json
[ { "title": "삶아서 먹기", "description": "..." } ]
```

---

## 바나나 상식

### `GET /facts/random`

| 쿼리 | 기본값 | 범위 | 설명 |
| --- | --- | --- | --- |
| `max_chars` | `50` | 10 ~ 500 | 돌려줄 문장들의 **글자 수 합** 상한 |

무작위로 뽑은 문장을 글자 수 합이 `max_chars` 를 넘지 않는 선까지 담아 돌려줍니다.
그래서 개수는 매번 다릅니다. 상한이 너무 작아 하나도 못 담으면 한 문장만 넣어 보냅니다.

```json
{ "facts": ["마트 바나나는 대부분 캐번디시 품종입니다."] }
```

---

## 기타

| 경로 | 응답 |
| --- | --- |
| `GET /` | `{"message":"Banana Ripeness API is running"}` |
| `GET /health` | `{"status":"healthy"}` |
| `GET /storage/...` | 업로드·결과 이미지 정적 서빙 |

> `/storage` 는 **상대 경로**로 마운트돼 있습니다(`StaticFiles(directory="storage")`).
> 반드시 `backend/` 폴더 안에서 uvicorn 을 실행해야 이미지가 열립니다.

---

## 아직 연결되지 않은 엔드포인트

`routers/auth.py` 에 `POST /auth/signup` 이 구현돼 있지만 `main.py` 에서 라우터를 등록하지 않아
**현재는 호출할 수 없습니다.** `users` 테이블도 생성되지 않습니다.

쓰려면 `main.py` 에 두 줄을 추가하면 됩니다.

```python
from routers.auth import router as auth_router
...
app.include_router(auth_router)
```

이때 `models/user.py` 가 import 되면서 `users` 테이블이 함께 만들어집니다.
필요한 라이브러리(`pydantic[email]`, `pwdlib[argon2]`)는 이미 `requirements.txt` 에 들어 있습니다.
