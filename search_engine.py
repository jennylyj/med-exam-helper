import sqlite3
import pandas as pd
from rapidfuzz import fuzz # <--- 新增這個
#from db_utils import DB_NAME # 引用我們之前設定好的資料庫名稱

def get_connection(db_path):
    return sqlite3.connect(db_path)

def search_questions(db_path, year=None, teacher=None, keyword=None):
    """
    萬用搜尋功能：
    可以指定年份、老師、或是題目關鍵字。
    參數如果不填 (None)，就代表該條件不設限。
    """
    conn = get_connection(db_path)
    
    # 這是 SQL 的一個小技巧：WHERE 1=1
    # 這樣我們後面就可以一直用 "AND ..." 接下去，不用擔心語法錯誤
    query = "SELECT id, year, teacher, q_type, content, options FROM questions WHERE 1=1"
    params = []

    # 1. 篩選年份
    if year:
        query += " AND year = ?"
        params.append(year)
    
    # 2. 篩選老師 (模糊搜尋，只要名字有包含就算)
    if teacher:
        query += " AND teacher LIKE ?"
        params.append(f"%{teacher}%") # %代表前後可以是任何字
        
    # 3. 篩選關鍵字 (搜尋題目內文)
    if keyword:
        query += " AND content LIKE ?"
        params.append(f"%{keyword}%")

    # 加上排序，讓年份新的在前面
    query += " ORDER BY year DESC"

    # 使用 Pandas 讀取，因為它印出來比較漂亮，之後要轉 PDF 也方便
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

# 新增功能 2-1: 取得所有老師名單 (給下拉選單用)
def get_all_teachers(db_path):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    # DISTINCT 確保同一個老師不會重複出現
    cursor.execute("SELECT DISTINCT teacher FROM questions ORDER BY teacher")
    teachers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return teachers

# 新增功能 3-1: 模糊搜尋重複題目
def find_fuzzy_duplicates(db_path, threshold=85):
    """
    使用模糊比對找出相似的題目
    threshold: 相似度門檻 (0~100)，建議 85 以上
    """
    conn = get_connection(db_path)
    # 撈出所有選擇題
    df = pd.read_sql_query("SELECT id, year, teacher, content FROM questions WHERE q_type='選擇題'", conn)
    conn.close()
    
    if df.empty:
        return pd.DataFrame()

    # 轉成列表比較好處理
    questions = df.to_dict('records')
    duplicates_groups = []
    visited_indices = set()

    # 雙重迴圈比對 (這會比較花時間，但在幾千題的規模下還跑得動)
    for i in range(len(questions)):
        if i in visited_indices:
            continue
            
        current_group = [questions[i]]
        
        for j in range(i + 1, len(questions)):
            if j in visited_indices:
                continue
            
            # 計算兩個字串的相似度 (Ratio)
            similarity = fuzz.ratio(questions[i]['content'], questions[j]['content'])
            
            if similarity >= threshold:
                current_group.append(questions[j])
                visited_indices.add(j)
        
        # 如果這一組超過 1 題，代表有重複
        if len(current_group) > 1:
            # 整理一下資料格式，方便顯示
            summary = {
                "主要題目": current_group[0]['content'],
                "重複次數": len(current_group),
                "出現年份": ", ".join([q['year'] for q in current_group]),
                "相似度": "模糊比對"
            }
            duplicates_groups.append(summary)

    return pd.DataFrame(duplicates_groups)

def find_duplicate_questions(db_path, min_count=2):
    """
    進階功能：找出重複出現的考古題
    邏輯：根據「題目內容 (content)」分組，計算出現次數大於 min_count 的題目
    """
    conn = get_connection(db_path)
    
    # SQL 語法解析：
    # GROUP BY content: 把題目文字一模一樣的歸成同一類
    # HAVING COUNT(*) >= ?: 只留下出現次數大於等於 N 次的
    # GROUP_CONCAT(year): 把出現過的年份串起來 (例如: B10, B12)
    sql = """
    SELECT 
        content, 
        COUNT(*) as frequency, 
        GROUP_CONCAT(year) as years,
        GROUP_CONCAT(teacher) as teachers
    FROM questions
    WHERE q_type = '選擇題'  -- 我們通常只比較選擇題
    GROUP BY content
    HAVING frequency >= ?
    ORDER BY frequency DESC
    """
    
    df = pd.read_sql_query(sql, conn, params=(min_count,))
    conn.close()
    
    return df

# --- 測試區 (讓你在終端機可以直接玩玩看) ---
'''
if __name__ == "__main__":
    print("=== 歡迎使用考古題搜尋引擎 ===")
    
    while True:
        print("\n請選擇功能:")
        print("1. 搜尋題目 (依年份/老師)")
        print("2. 抓出重複的考古題 (必考題!)")
        print("q. 離開")
        
        choice = input("輸入選項: ")
        
        if choice == '1':
            t_input = input("請輸入老師姓名 (直接按 Enter 跳過): ").strip()
            y_input = input("請輸入年份 (例如 B12, 直接按 Enter 跳過): ").strip()
            k_input = input("請輸入關鍵字 (直接按 Enter 跳過): ").strip()
            
            # 轉換空字串為 None
            teacher = t_input if t_input else None
            year = y_input if y_input else None
            keyword = k_input if k_input else None
            
            result = search_questions(year, teacher, keyword)
            
            if not result.empty:
                print(f"\n找到 {len(result)} 筆資料：")
                # 這裡只印出前 3 筆預覽，以免畫面太長
                print(result[['year', 'teacher', 'content']].head(3))
                print("... (更多資料省略)")
            else:
                print("\n找不到符合的題目耶！")

        elif choice == '2':
            print("\n正在分析重複題庫...")
            duplicates = find_duplicate_questions()
            
            if not duplicates.empty:
                print(f"\n發現 {len(duplicates)} 題重複出現的考古題！(高機率考題)")
                # 設定 Pandas 顯示選項，讓長文字不要被截斷
                pd.set_option('display.max_colwidth', 50) 
                print(duplicates)
            else:
                print("目前沒有發現完全重複的題目。")
                
        elif choice == 'q':
            break
        '''