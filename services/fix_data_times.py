import pymysql
from datetime import datetime, timedelta

conn = pymysql.connect(host='localhost', user='root', password='root', database='intelli_shop')
cursor = conn.cursor()
cursor.execute("SELECT id FROM charging_records")
ids = [row[0] for row in cursor.fetchall()]

for i, record_id in enumerate(ids):
    # 每条记录分配到不同的日期
    new_date = datetime.now() - timedelta(days=(i % 30))
    cursor.execute("UPDATE charging_records SET created_at = %s WHERE id = %s", (new_date, record_id))

conn.commit()
conn.close()