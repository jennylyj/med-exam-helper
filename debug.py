import sqlite3
import pandas as pd

# 請確認這裡的檔名跟你資料夾裡的一模一樣
db_path = "databases/大二上生化二段.db"

conn = sqlite3.connect(db_path)

# 隨機抓出 10 題選擇題來看看
df = pd.read_sql_query("SELECT year, content FROM questions WHERE q_type='選擇題' LIMIT 10", conn)

print("=== 資料庫題目預覽 ===")
for index, row in df.iterrows():
    # 使用 repr() 可以把隱藏的符號（如換行 \n）印出來
    print(f"[{row['year']}] {repr(row['content'])}")

conn.close()