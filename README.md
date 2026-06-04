# 智能电动车充电桩业务管理与时序监测系统

本项目是一套面向分布式物联网场景的智能充电桩业务监控、调度与负荷预测系统。系统采用轻量化分布式微服务架构进行解耦，通过 Docker 容器化实现一键式敏捷部署，并构建了基于 Pytest 的全链路自动化质量保障工程。

## 1. 系统架构与技术栈
* **后端核心**：FastAPI (异步高性能 Web 框架) + SQLAlchemy (ORM)
* **时序推理**：PyTorch / LSTM (深度学习时序负荷预测)
* **存储治理**：MySQL 8.0 (持久化业务数据)
* **交付运维**：Docker / Docker Compose (微服务容器化编排)
* **质量保证**：Pytest + Requests (接口自动化测试框架)

## 2. 目录工程规范
```text
├── api_pytest/               # 独立端到端/全链路接口自动化测试工程
│   ├── conftest.py           # Pytest 全局配置及 JWT Token 动态注入 Fixture
│   └── testcases/            # 场景化自动化测试用例集
├── services/                 # 分布式微服务核心代码域
│   ├── user_service/         # 用户鉴权服务 (基于 OAuth2 / JWT 规范)
│   ├── station_service/      # 充电站点状态监控服务 (提供秒级状态流转)
│   ├── charging_service/     # 充电流水采集与调度业务服务
│   ├── forecasting_service/  # 基于 LSTM 模型的智能时序推理微服务
│   └── integration_test.py   # 跨服务全链路集成测试脚本
├── docker-compose.yml        # 生产/测试环境一键式容器编排引擎
└── requirements.txt          # 项目全局依赖规范
