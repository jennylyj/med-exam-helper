#創建倉庫，並把貨物搬進去
import sqlite3
import os

# 資料庫檔案名稱
DB_NAME = "med_exams.db"

def init_db():
    """ 初始化資料庫：如果沒有，就建立一個新的，並設定好欄位 """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立一個名為 'questions' 的表格
    # 我們設計了以下欄位：
    # id: 自動編號 (身分證字號)
    # year: 年份 (例如 B12)
    # teacher: 老師 (例如 顏伯勳)
    # q_type: 題型 (選擇題 / 非選擇題)
    # question_id: 題號 (例如 1)
    # content: 題目內容
    # options: 選項內容 (如果是選擇題)
    # full_text: 完整文字 (方便未來搜尋關鍵字用)
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year TEXT,
        teacher TEXT,
        q_type TEXT,
        question_id TEXT,
        content TEXT,
        options TEXT,
        full_text TEXT
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()
    print(f"資料庫 {DB_NAME} 已就緒！")

def insert_question(data):
    """ 把一題資料存入資料庫 """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    sql = """
    INSERT INTO questions (year, teacher, q_type, question_id, content, options, full_text)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.execute(sql, (
        data['year'],
        data['teacher'],
        data['q_type'],
        data['question_id'],
        data['question_text'],
        data['options_text'],
        data['full_text']
    ))
    
    conn.commit()
    conn.close()

def clear_db():
    """ (測試用) 清空資料庫，避免重複匯入一樣的資料 """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions")
    conn.commit()
    conn.close()
    print("資料庫已清空。")