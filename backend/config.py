import os
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# 접속 주소가 없으면 SQLite 파일 하나로 떨어진다.
# 배포(컨테이너)에서는 PostgreSQL 을 따로 띄우지 않으므로 이 경로를 쓴다.
# 로컬에서는 .env 의 DATABASE_URL(PostgreSQL)이 그대로 우선한다.
DATABASE_URL = os.getenv("DATABASE_URL") or (
    "sqlite:///" + os.path.join(BASE_DIR, "banana.db")
)


# 가중치 경로. 상대경로로 주면 이 파일이 있는 폴더(backend/) 기준으로 푼다.
# 절대경로로 박아두지 않았으므로 폴더를 옮기거나 컨테이너에 넣어도 그대로 동작한다.
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "weights/best.pt"
)

if not os.path.isabs(MODEL_PATH):
    MODEL_PATH = os.path.join(
        BASE_DIR,
        MODEL_PATH
    )


UPLOAD_DIR = os.path.join(
    BASE_DIR,
    os.getenv(
        "UPLOAD_DIR",
        "storage/uploads"
    )
)


RESULT_DIR = os.path.join(
    BASE_DIR,
    os.getenv(
        "RESULT_DIR",
        "storage/results"
    )
)


# 추론 임계값.
#
# 0.15 는 눈대중이 아니라 실측으로 정한 값이다
# (banana_4class_v2_epoch50 / valid 1,525장, experiments.md
#  "개선 실험 1 사후 점검 - 점검 A"):
#
#   conf   ripe R  overripe R  rotten R  |  rotten precision
#   0.25    0.957     0.979      0.881   |      0.758
#   0.15    0.972     0.982      0.912   |      0.687   <- 채택
#   0.10    0.977     0.984      0.923   |      0.636
#
# 프로젝트 지침이 "ripe recall 최우선, precision 희생 허용"이라 이 교환은
# 정당하다. 0.10 까지 내리지 않은 이유는 rotten precision 이 0.636 까지
# 떨어져 사진 한 장에 오탐 박스가 눈에 띄게 늘기 때문이다.
#
# 주의: valid set 에서 정한 값이다. test set 으로 다시 튜닝하지 말 것.
DEFAULT_CONF = float(os.getenv("BANANA_CONF", "0.15"))
DEFAULT_IOU = float(os.getenv("BANANA_IOU", "0.7"))


RIPING_XLSX_PATH = os.getenv(
    "RIPING_XLSX_PATH",
    os.path.join(
        BASE_DIR,
        "..",
        "banana_riping.xlsx"
    )
)


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)