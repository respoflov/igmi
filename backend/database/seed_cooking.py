from sqlalchemy.orm import Session

from models.cooking import Cooking


# 도메인_서치.docx의 '④ 맛있게 먹는 방법(영양정보)' 항목을 바탕으로 정리
DEFAULT_COOKING_ROWS = [
    {
        "ripeness_class": "unripe",
        "title": "아직은 조금 더 기다려주세요",
        "description": "실온에서 조금 더 숙성한 뒤 섭취하는 것을 권장합니다.",
    },
    {
        "ripeness_class": "unripe",
        "title": "삶아서 먹기",
        "description": "껍질째 씻어 물에 15~30분 삶은 뒤 껍질을 벗겨 먹습니다.",
    },
    {
        "ripeness_class": "unripe",
        "title": "쪄서 먹기",
        "description": "껍질째 찜기에 20~30분 찌면 더 부드럽고 담백해집니다.",
    },
    {
        "ripeness_class": "unripe",
        "title": "에어프라이어·오븐 구이",
        "description": "껍질을 벗기거나 반으로 갈라 180도에서 15~25분 익힙니다.",
    },
    {
        "ripeness_class": "unripe",
        "title": "팬에 구워 먹기",
        "description": "삶거나 찐 바나나를 잘라 팬에 구우면 더 맛있습니다.",
    },
    {
        "ripeness_class": "unripe",
        "title": "그린바나나 가루 활용",
        "description": "말린 그린바나나 가루를 우유·요거트·오트밀·스무디에 타 먹습니다.",
    },
    {
        "ripeness_class": "unripe",
        "title": "바나나 튀김",
        "description": "얇게 썰어 소금을 뿌린 뒤 170~180도 기름에 노릇하게 튀깁니다.",
    },
    {
        "ripeness_class": "ripe",
        "title": "생과일로 바로 섭취",
        "description": "바로 섭취하거나 스무디·샌드위치에 활용하기 좋습니다.",
    },
    {
        "ripeness_class": "ripe",
        "title": "초콜릿 바나나",
        "description": "잘 익은 바나나에 초콜릿을 곁들여 간단한 디저트로 즐길 수 있습니다.",
    },
    {
        "ripeness_class": "ripe",
        "title": "바나나 포스터",
        "description": "버터와 설탕에 졸여내는 바나나 플랑베 디저트입니다.",
    },
    {
        "ripeness_class": "ripe",
        "title": "바나나 포스터 프렌치토스트",
        "description": "바나나 포스터를 프렌치토스트에 올려 먹는 브런치 메뉴입니다.",
    },
    {
        "ripeness_class": "ripe",
        "title": "바나나 크림 파이",
        "description": "잘 익은 바나나와 크림을 층층이 쌓아 만드는 대표 디저트입니다.",
    },
    {
        "ripeness_class": "ripe",
        "title": "바나나 열대과일 샐러드",
        "description": "다른 열대과일과 함께 썰어 상큼한 샐러드로 즐길 수 있습니다.",
    },
    {
        "ripeness_class": "overripe",
        "title": "바나나 오트밀 구이",
        "description": "으깬 바나나를 오트밀과 섞어 오븐에 구워 먹는 요리입니다.",
    },
    {
        "ripeness_class": "overripe",
        "title": "호박 바나나빵",
        "description": "단호박과 으깬 바나나를 함께 넣어 굽는 빵입니다.",
    },
    {
        "ripeness_class": "overripe",
        "title": "바나나 머그 케이크",
        "description": "머그컵에 재료를 담아 전자레인지로 간단히 만드는 케이크입니다.",
    },
    {
        "ripeness_class": "overripe",
        "title": "바나나 머핀",
        "description": "으깬 바나나를 반죽에 섞어 굽는 머핀입니다.",
    },
    {
        "ripeness_class": "overripe",
        "title": "땅콩버터 바나나 쿠키",
        "description": "땅콩버터와 으깬 바나나를 섞어 구운 쿠키입니다.",
    },
    {
        "ripeness_class": "rotten",
        "title": "섭취를 피해주세요",
        "description": "부패 상태가 의심되면 섭취하지 않는 것이 안전합니다.",
    },
]


def seed_cooking(db: Session):

    existing = [
        (row.ripeness_class, row.title, row.description)
        for row in db.query(Cooking).all()
    ]

    target = [
        (row["ripeness_class"], row["title"], row["description"])
        for row in DEFAULT_COOKING_ROWS
    ]

    if sorted(existing) == sorted(target):
        return

    db.query(Cooking).delete()

    for row in DEFAULT_COOKING_ROWS:

        db.add(Cooking(**row))

    db.commit()

    print(f"cooking 테이블을 {len(DEFAULT_COOKING_ROWS)}개 행으로 갱신했습니다.")
