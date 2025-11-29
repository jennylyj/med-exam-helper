import sqlite3
import pandas as pd

# 連接資料庫
conn = sqlite3.connect("med_exams.db")

# 讀取前 5 筆資料並用 Pandas 漂亮顯示
df = pd.read_sql_query("SELECT year, teacher, q_type, content FROM questions LIMIT 5", conn)
print(df)

# 統計一下題型分佈
print("\n題型統計:")
print(pd.read_sql_query("SELECT q_type, COUNT(*) as count FROM questions GROUP BY q_type", conn))

conn.close()