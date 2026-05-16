# EV Charging System 操作指南

## 1. 项目简要说明

本项目是一个基于 FastAPI 的电动车充电系统微服务项目，使用 MySQL 作为共享数据库，并通过 Docker Compose 编排运行。

核心服务：

| 服务 | 目录 | 端口 | 说明 |
| --- | --- | ---: | --- |
| 用户服务 | `services/user_service` | `8000` | 注册、登录、JWT 鉴权 |
| 充电站服务 | `services/station_service` | `8001` | 创建和查询充电站 |
| 充电记录服务 | `services/charging_service` | `8002` | 创建充电记录 |
| 预测服务 | `services/forecasting_service` | `8003` | 基于充电记录进行 LSTM 负荷预测 |
| 数据库 | MySQL 8.0 | `3306` | 存储业务数据 |

项目主要目录：

```text
myshop/
├── docker-compose.yml
├── requirements.txt
├── services/
│   ├── user_service/
│   ├── station_service/
│   ├── charging_service/
│   ├── forecasting_service/
│   ├── seed_data.py
│   └── fix_data_times.py
└── api_pytest/
    ├── conftest.py
    └── testcases/
```

## 2. 安装准备

推荐环境：

- Python 3.12
- Docker
- Docker Compose

检查环境：

```bash
python --version
docker --version
docker compose version
```

安装本地测试依赖：

```bash
cd ~/myshop
source venv/bin/activate
pip install -r requirements.txt
pip install pytest requests httpx pytest-html pymysql
```

## 3. Docker 方式运行项目

推荐使用 Docker Compose 一次性启动全部服务。

```bash
cd ~/myshop
docker compose up --build -d
docker compose ps
```

查看日志：

```bash
docker compose logs --tail=80 user_service
docker compose logs --tail=80 station_service
docker compose logs --tail=80 charging_service
docker compose logs --tail=80 forecasting_service
```

健康检查：

```bash
curl -sS http://localhost:8000/health
```

停止服务并保留数据库数据：

```bash
docker compose down
```

清空数据库数据，谨慎执行：

```bash
docker compose down -v
```

## 4. 本地开发方式运行项目

本地开发时，只建议 Docker 启动数据库，然后本地运行四个 FastAPI 服务。不要同时执行完整的 `docker compose up --build -d`，否则会端口冲突。

启动数据库：

```bash
cd ~/myshop
docker compose up -d db
```

安装依赖：

```bash
cd ~/myshop
source venv/bin/activate
pip install -r services/user_service/requirements.txt
pip install -r services/station_service/requirements.txt
pip install -r services/charging_service/requirements.txt
pip install -r services/forecasting_service/requirements.txt
```

四个终端分别启动：

```bash
cd ~/myshop
source venv/bin/activate
python -m uvicorn services.user_service.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd ~/myshop
source venv/bin/activate
python -m uvicorn services.station_service.main:app --host 0.0.0.0 --port 8001 --reload
```

```bash
cd ~/myshop
source venv/bin/activate
python -m uvicorn services.charging_service.main:app --host 0.0.0.0 --port 8002 --reload
```

```bash
cd ~/myshop
source venv/bin/activate
python -m uvicorn services.forecasting_service.main:app --host 0.0.0.0 --port 8003 --reload
```

接口文档地址：

```text
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
```

## 5. 常用接口操作命令

注册测试用户：

```bash
curl -sS -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "manual_tester", "email": "manual_tester@ev.com", "password": "password123"}'
```

登录并保存 Token：

```bash
TOKEN=$(curl -sS -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=manual_tester&password=password123' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
```

创建充电站：

```bash
curl -sS -X POST http://localhost:8001/stations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "科技园超级充电站", "location": "深南大道", "capacity": 120.0, "slots": 10}'
```

查询充电站：

```bash
curl -sS http://localhost:8001/stations \
  -H "Authorization: Bearer $TOKEN"
```

创建充电记录：

```bash
curl -sS -X POST http://localhost:8002/charging \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"station_id": 1, "duration_minutes": 60, "kwh_consumed": 25.5}'
```

预测 1 号充电站负荷：

```bash
curl -sS http://localhost:8003/predict/1
```

## 6. 准备预测数据与训练模型

`seed_data.py` 默认使用 `manual_tester/password123` 登录并注入充电记录，所以请先注册该用户。

注入模拟数据：

```bash
cd ~/myshop
source venv/bin/activate
python services/seed_data.py
```

把记录时间分散到过去 30 天：

```bash
python services/fix_data_times.py
```

训练 1 号站点模型：

```bash
docker exec forecasting_service python3 -m forecasting_service.train
```

当前项目中 `train.py` 保存 `station_1.pth`，但 `processor.py` 加载 `product_1.pth`。在修改代码前，可临时同步文件名：

```bash
docker exec forecasting_service sh -c 'cp /app/forecasting_service/models/station_1.pth /app/forecasting_service/models/product_1.pth'
```

调用预测：

```bash
curl -sS http://localhost:8003/predict/1
```

## 7. 运行测试

测试前请确认四个服务已经启动：

```bash
docker compose ps
curl -sS http://localhost:8000/health
```

安装测试依赖：

```bash
cd ~/myshop
source venv/bin/activate
pip install pytest requests httpx anyio pytest-html
```

`api_pytest/conftest.py` 是 pytest 的公共夹具文件：

- `env_urls` 统一提供用户服务、充电站服务、预测服务的基础地址。
- `auth_headers` 会在测试开始时尝试注册 `pytest_admin`，随后登录并提取 JWT Token，最后返回带 `Authorization` 的请求头。

建议运行测试前手动注册 pytest 专用账号，避免单独运行 `test_01_user.py` 时因账号不存在导致登录失败：

```bash
curl -sS -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "pytest_admin", "email": "pytest_admin@ev.com", "password": "password_123"}'
```

如果返回 `Email already registered`，说明账号已存在，可以继续测试。

说明：`test_login_success` 只依赖 `env_urls`，不会触发 `auth_headers` 自动注册流程。因此首次单独运行该测试时，如果数据库里没有 `pytest_admin`，可能出现 `400 != 200`。这不是登录接口本身的 bug，而是测试用例依赖了预置账号。解决方式是先执行上面的注册命令，或先运行会使用 `auth_headers` 的接口测试。

运行全部接口测试：

```bash
cd ~/myshop
source venv/bin/activate
pytest api_pytest/testcases -q
```

运行指定测试：

```bash
pytest api_pytest/testcases/test_01_user.py -q
pytest api_pytest/testcases/test_02_station.py -q
pytest api_pytest/testcases/test_03_forecast.py -q
```

运行集成测试：

```bash
pip install httpx anyio
pytest services/integration_test.py -q
```

生成 HTML 报告：

```bash
pytest api_pytest/testcases \
  --html=api_pytest/reports/EV_Pytest_Report.html \
  --self-contained-html
```

报告位置：

```text
api_pytest/reports/EV_Pytest_Report.html
```

## 8. 常见错误处理

### 8.1 Docker 拉取镜像超时

错误示例：

```text
failed to resolve reference "docker.io/library/mysql:8.0"
i/o timeout
```

处理方式：

```bash
sudo mkdir -p /etc/docker
sudo nano /etc/docker/daemon.json
```

写入：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://mirror.baidubce.com"
  ],
  "dns": ["223.5.5.5", "119.29.29.29", "8.8.8.8"]
}
```

重启 Docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

预拉取镜像：

```bash
docker pull mysql:8.0
docker pull python:3.12-slim
```

### 8.2 端口被占用

检查端口：

```bash
ss -lntp
```

常用端口：

```text
8000 用户服务
8001 充电站服务
8002 充电记录服务
8003 预测服务
3306 MySQL
```

如果已经使用 Docker Compose 启动了全部服务，不要再本地启动四个 `uvicorn`。

### 8.3 登录失败

`/login` 必须使用 form data，不能使用 JSON：

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=manual_tester&password=password123'
```

### 8.4 接口返回 401

需要添加请求头：

```text
Authorization: Bearer <access_token>
```

示例：

```bash
curl -sS http://localhost:8001/stations \
  -H "Authorization: Bearer $TOKEN"
```

### 8.5 数据库连接失败

检查数据库容器：

```bash
docker compose ps db
docker compose logs --tail=100 db
```

如果需要重启：

```bash
docker compose restart db
docker compose restart user_service station_service charging_service forecasting_service
```

### 8.6 预测接口提示数据不足

先注入数据并修正时间：

```bash
cd ~/myshop
source venv/bin/activate
python services/seed_data.py
python services/fix_data_times.py
```

然后重新训练并预测：

```bash
docker exec forecasting_service python3 -m forecasting_service.train
docker exec forecasting_service sh -c 'cp /app/forecasting_service/models/station_1.pth /app/forecasting_service/models/product_1.pth'
curl -sS http://localhost:8003/predict/1
```
