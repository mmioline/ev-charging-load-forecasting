#!/bin/bash

# 确保脚本只要有一行报错就立刻停止执行（工业级 Shell 脚本规范）
set -e

USER_URL="http://localhost:28010"
STATION_URL="http://localhost:28011"
FORECAST_URL="http://localhost:28013"

echo "=================================================="
echo "[QA Pipeline] 开始执行一键式容器化全链路测试流..."
echo "=================================================="

echo "[1/5] 正在清理旧容器环境，重置网络与卷..."
docker compose down -v --remove-orphans

echo "[2/5] 正在构建并拉起多物理微服务节点..."
docker compose up -d --build

echo "等待用户服务健康检查就绪..."
for i in {1..40}; do
  if curl -fsS "${USER_URL}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS "${USER_URL}/health" >/dev/null

echo "[3/5] 正在创建测试账号与演示站点..."
curl -fsS -X POST "${USER_URL}/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"pytest_admin","email":"pytest_admin@ev.com","password":"password_123"}' \
  >/dev/null || true

curl -fsS -X POST "${USER_URL}/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"manual_tester","email":"manual_tester@ev.com","password":"password123"}' \
  >/dev/null || true

TOKEN=$(curl -fsS -X POST "${USER_URL}/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=manual_tester&password=password123" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# 实时抓取系统分配的真实自增主键 ID，消除因多微服务启动时间差导致的主键错位隐患
A_ID=$(curl -fsS -X POST "${STATION_URL}/stations" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pipeline A站","location":"自动化测试区域A","capacity":60.0,"slots":6}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')

B_ID=$(curl -fsS -X POST "${STATION_URL}/stations" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pipeline B站","location":"自动化测试区域B","capacity":160.0,"slots":16}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')

echo "[4/5] 正在直接注入预测所需的历史充电记录 (对齐当前站点的真实ID: A=${A_ID}, B=${B_ID})..."
docker exec ev_charging_db mysql -uroot -proot ev_charging -e "
INSERT INTO charging_records (user_id, station_id, kwh_consumed, duration_minutes, created_at)
SELECT 'manual_tester', ${A_ID}, 10 + (n % 40), 30 + (n % 90), DATE_SUB(NOW(), INTERVAL (n % 30) DAY)
FROM (
  SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
  UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
  UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15
  UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20
  UNION ALL SELECT 21 UNION ALL SELECT 22 UNION ALL SELECT 23 UNION ALL SELECT 24 UNION ALL SELECT 25
  UNION ALL SELECT 26 UNION ALL SELECT 27 UNION ALL SELECT 28 UNION ALL SELECT 29 UNION ALL SELECT 30
) nums;
INSERT INTO charging_records (user_id, station_id, kwh_consumed, duration_minutes, created_at)
SELECT 'manual_tester', ${B_ID}, 12 + (n % 35), 35 + (n % 80), DATE_SUB(NOW(), INTERVAL (n % 30) DAY)
FROM (
  SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
  UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
  UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15
  UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20
  UNION ALL SELECT 21 UNION ALL SELECT 22 UNION ALL SELECT 23 UNION ALL SELECT 24 UNION ALL SELECT 25
  UNION ALL SELECT 26 UNION ALL SELECT 27 UNION ALL SELECT 28 UNION ALL SELECT 29 UNION ALL SELECT 30
) nums;
" >/dev/null

echo "正在训练预测模型..."
docker exec forecasting_service python3 -m forecasting_service.train ${A_ID} ${B_ID} --epochs 20 >/dev/null
curl -fsS "${FORECAST_URL}/predict/${A_ID}" >/dev/null

echo "[5/5] 激活 Pytest 框架，执行端到端场景断言与全流程业务验证..."
PYTHONPATH=. pytest api_pytest/ -v --tb=short

echo "=================================================="
echo "[QA Pipeline] 自动化质量保障测试全部通过！亮绿灯放行交付！"
echo "=================================================="