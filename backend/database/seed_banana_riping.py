import os

from sqlalchemy.orm import Session

from config import RIPING_XLSX_PATH
from models.banana_riping import BananaRiping


# 엑셀 행(습도) 라벨 -> DB 키 매핑
HUMIDITY_KEY_MAP = {
    "85": "85_90",
    "80": "80_85",
    "60": "60_70",
    "50": "50_60",
}

# 엑셀 열(온도) 순서 -> BananaRiping 컬럼명 매핑
TEMP_COLUMNS = [
    "temp_under_10",
    "temp_13_15",
    "temp_18_20",
    "temp_25_30",
    "temp_over_35",
]


def _humidity_key(label: str) -> str:

    digits = "".join(
        ch for ch in label.split("%")[0]
        if ch.isdigit()
    )

    return HUMIDITY_KEY_MAP.get(digits, digits)


def _clean_label(label: str) -> str:

    return " ".join(label.split())


def load_rows_from_xlsx(xlsx_path: str):

    import openpyxl

    wb = openpyxl.load_workbook(
        xlsx_path,
        data_only=True
    )

    ws = wb.worksheets[0]

    rows = []

    for row in ws.iter_rows(min_row=2, values_only=True):

        humidity_label = row[0]

        if not humidity_label:
            continue

        rows.append(
            {
                "humidity_key": _humidity_key(str(humidity_label)),
                "humidity_label": _clean_label(str(humidity_label)),
                "temp_under_10": row[1],
                "temp_13_15": row[2],
                "temp_18_20": row[3],
                "temp_25_30": row[4],
                "temp_over_35": row[5],
            }
        )

    return rows


def seed_banana_riping(db: Session):

    already_seeded = (
        db.query(BananaRiping.id).first()
        is not None
    )

    if already_seeded:
        return

    xlsx_path = os.path.abspath(RIPING_XLSX_PATH)

    if not os.path.exists(xlsx_path):
        print(f"banana_riping.xlsx 를 찾을 수 없습니다: {xlsx_path}")
        return

    rows = load_rows_from_xlsx(xlsx_path)

    for row in rows:

        db.add(BananaRiping(**row))

    db.commit()

    print(f"banana_riping 테이블에 {len(rows)}개 행을 저장했습니다.")
