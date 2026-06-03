# EV 充电桩实时监测与空闲状态查询

本项目是一个电动汽车的充电监控与调度系统，采用 FastAPI 微服务、MySQL、Redis、Docker Compose 和单页前端实现。系统支持用户登录、充电站状态查询、充电记录创建、异常状态自动治理、充电记录隔离，以及未来 1 小时站点空闲概率预测。

## 服务端口

| 服务 | 目录 | 对外端口 | 容器端口 | 说明 |
| --- | --- | ---: | ---: | --- |
| 前端页面 | `frontend` | `18080` | `8080` | 单页 HTML + 原生 JS |
| 用户服务 | `services/user_service` | `18010` | `8000` | 注册、登录、JWT 鉴权 |
| 站点服务 | `services/station_service` | `18011` | `8001` | 站点创建、状态查询、异常治理 |
| 充电记录服务 | `services/charging_service` | `18012` | `8002` | 创建和查询个人充电记录 |
| 预测服务 | `services/forecasting_service` | `18013` | `8003` | 负荷预测与空闲概率预测 |
| MySQL | Docker 内部 | 不暴露 | `3306` | 业务数据库 `ev_charging` |
| Redis | Docker 内部 | 不暴露 | `6379` | 站点实时状态缓存 |

## 目录结构

```text
.
├── docker-compose.yml
├── frontend/
│   ├── Dockerfile
│   └── index.html
├── services/
│   ├── user_service/
│   ├── station_service/
│   ├── charging_service/
│   ├── forecasting_service/
│   ├── seed_data.py
│   └── fix_data_times.py
├── api_pytest/
│   ├── conftest.py
│   └── testcases/
└── 系统演示.md
```

## 启动

```bash
docker compose down -v --remove-orphans
docker compose up -d --build --force-recreate
docker compose ps
```

正常情况下应看到：

```text
frontend              0.0.0.0:18080->8080/tcp
user_service          0.0.0.0:18010->8000/tcp
station_service       0.0.0.0:18011->8001/tcp
charging_service      0.0.0.0:18012->8002/tcp
forecasting_service   0.0.0.0:18013->8003/tcp
```

健康检查：

```bash
curl -sS http://localhost:18010/health
```

打开前端：

```text
http://localhost:18080
```

如果项目运行在 WSL 中，Windows 浏览器无法访问 `localhost:18080` 时，可尝试：

```text
http://127.0.0.1:18080
http://<WSL_IP>:18080
```

## 演示流程

完整演示步骤见：

```text
系统演示.md
```

推荐演示主线：

```text
Alice 登录 -> 查询站点 -> 发起充电 -> 查看个人记录 -> 查看空闲概率预测
Bob 登录 -> 验证无法查看 Alice 的充电记录
C 站超时 -> 自动标记为异常
```

## 测试

```bash
source venv/bin/activate
pytest api_pytest/testcases -q
```

生成测试报告：

```bash
pytest api_pytest/testcases \
  --html=api_pytest/reports/EV_Pytest_Report.html \
  --self-contained-html
```
