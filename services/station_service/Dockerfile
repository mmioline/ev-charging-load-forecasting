FROM python:3.12-slim
WORKDIR /app

# 设置国内镜像源环境变量，加速所有 pip 操作
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 复制业务代码
COPY . ./station_service/
# 必须运行 station_service 模块
CMD ["uvicorn", "station_service.main:app", "--host", "0.0.0.0", "--port", "8001"]