# 바나나 숙성도 판별 API — 배포용 컨테이너
#
# 배포처: Hugging Face Spaces (SDK: Docker). 7860 포트를 기대한다.
#
# 로컬에서 똑같이 띄워보기:
#   docker build -t banana-api backend
#   docker run --rm -p 7860:7860 banana-api
#   -> http://127.0.0.1:7860/docs

FROM python:3.12-slim

# opencv(ultralytics 의존)가 필요로 하는 시스템 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces 는 컨테이너를 uid 1000 으로 돌린다. root 로 만든 파일은
# 쓰기가 막혀서 SQLite 파일 생성과 이미지 저장이 실패한다.
RUN useradd -m -u 1000 user

# YOLO_AUTOINSTALL=false : Ultralytics 가 실행 도중 pip install 을 돌리지
#   못하게 막는다. 컨테이너 안에서 이게 돌면 그 요청은 실패한다.
# 나머지는 캐시·설정 폴더를 쓰기 가능한 곳으로 돌려주는 설정이다.
ENV HOME=/home/user \
    YOLO_CONFIG_DIR=/tmp/Ultralytics \
    MPLCONFIGDIR=/tmp/matplotlib \
    YOLO_AUTOINSTALL=false \
    PYTHONUNBUFFERED=1

WORKDIR /app

# torch 는 CPU 전용 빌드를 따로 먼저 깐다. 일반 설치는 CUDA 포함 버전이라
# 수 GB 를 받아 빌드가 실패하거나 아주 느려진다. YOLO11n 은 가벼워서
# CPU 로도 사진 한 장에 0.2~0.5초면 충분하다.
RUN pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch torchvision

# 의존성을 먼저 깔면 코드만 바뀌었을 때 이 층을 재사용해 빌드가 빨라진다
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY --chown=user:user . /app
RUN chown -R user:user /app

USER user

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
