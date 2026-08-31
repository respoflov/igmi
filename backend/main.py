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
app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],

    allow_credentials=True,

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