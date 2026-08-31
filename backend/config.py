import os
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


DATABASE_URL = os.getenv("DATABASE_URL")


MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "../models/best.pt"
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