import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.database import Base, engine, SessionLocal

from routers.prediction import router as prediction_router
from routers.history import router as history_router
from routers.ripening import router as ripening_router
from routers.cooking import router as cooking_router
from routers.facts import router as facts_router

from database.seed_banana_riping import seed_banana_riping
from database.seed_cooking import seed_cooking
from database.seed_banana_fact import seed_banana_fact


# DB 테이블 생성
Base.metadata.create_all(
    bind=engine
)


# 초기 데이터 시딩 (최초 1회)
with SessionLocal() as _db:
    seed_banana_riping(_db)
    seed_cooking(_db)
    seed_banana_fact(_db)


app = FastAPI(
    title="Banana Ripeness API",
    description="AI 기반 바나나 숙성도 분석 API",
    version="1.0.0"
)


# CORS
# 화면과 서버의 주소가 다르면 브라우저가 요청을 막는다.
# 배포할 때는 환경변수로 실제 주소를 넘긴다. 쉼표로 여러 개 지정 가능:
#   BANANA_ALLOW_ORIGINS=https://<깃허브아이디>.github.io
# 지정하지 않으면 아래 로컬 개발 주소만 허용한다.
# 기본값은 "*"(전체 허용) 이다. 좁혀두면 배포할 때마다 이 변수를 안 넣어서
# "아무 반응 없음"으로 막히는데, 원인이 화면에 안 드러나 찾기가 가장 어렵다.
# 이 API 는 로그인도 쿠키도 없고, CORS 는 브라우저만 제약할 뿐 curl 은 어차피
# 그냥 부를 수 있으므로 "*" 라고 해서 실제로 열리는 것도 없다.
ALLOW_ORIGINS = [
    o.strip()
    for o in os.getenv("BANANA_ALLOW_ORIGINS", "*").split(",")
    if o.strip()
]


app.add_middleware(

    CORSMiddleware,

    allow_origins=ALLOW_ORIGINS,

    # 쿠키·인증을 쓰지 않는다. True 로 두면 allow_origins="*" 가 무효가 된다.
    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


# 업로드 이미지 접근
app.mount(
    "/storage",
    StaticFiles(
        directory="storage"
    ),
    name="storage"
)


# Router 등록
app.include_router(
    prediction_router
)

app.include_router(
    history_router
)

app.include_router(
    ripening_router
)

app.include_router(
    cooking_router
)

app.include_router(
    facts_router
)


@app.get("/")
def root():

    return {
        "message":
            "Banana Ripeness API is running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }