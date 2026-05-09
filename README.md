# 电动汽车（EV）充电负荷预测系统

本系统旨在实现针对不同充电站节点精准用电负荷预判的全链路闭环。
系统支持从分布式数据采集、时序特征清洗到深度学习模型预测的全生命周期管理。具备完整的 OAuth2 权限隔离，确保每个站点的负荷数据不被越权访问。

## 基础设施部署
系统依赖 Docker 与 Docker Compose。克隆仓库后，在根目录执行一键编排：
```bash
# 启动微服务集群与 MySQL 数据库
docker-compose up -d --build

# 检查 5 个核心容器是否均处于 Up 状态
docker-compose ps

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install pytest pytest-html requests

# 执行全链路测试
pytest api_pytest/testcases/ \
    --html=api_pytest/reports/EV_Pytest_Report.html \
    --self-contained-html \
    -v
