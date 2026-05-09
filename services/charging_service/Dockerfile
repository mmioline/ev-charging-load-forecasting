FROM python:3.12-slim
WORKDIR /app

# 设置国内镜像源加速
ENV PYTHONPATH=/app

# 确保 Python 能在容器内找到以文件夹命名的包
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


COPY . ./charging_service/
CMD ["uvicorn", "charging_service.main:app", "--host", "0.0.0.0", "--port", "8002"]