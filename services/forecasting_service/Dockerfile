FROM python:3.12-slim
WORKDIR /app

# 设置国内镜像源环境变量，加速所有 pip 操作
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu

# 1. 复制 requirements.txt (这一层会被缓存)
COPY requirements.txt .

# 2. 安装依赖 (只要 requirements.txt 不变，下次构建只需 1 秒)
RUN pip install --no-cache-dir -r requirements.txt

# 3. 复制业务代码
COPY . ./forecasting_service/

CMD ["uvicorn", "forecasting_service.main:app", "--host", "0.0.0.0", "--port", "8003"]