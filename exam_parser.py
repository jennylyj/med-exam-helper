import pdfplumber
import re
import os
# 引入我們剛剛寫的資料庫工具
import db_utils 

PDF_PATH = 'pdfs/B13生化二段考古題本_全.pdf' 

def parse_and_save_exam(pdf_path):
    # 1. 先初始化資料庫 (確保表格存在)
    db_utils.init_db()
    
    # 2. 清空舊資料 (開發階段我們先這樣做，以免你跑兩次變兩倍資料)
    db_utils.clear_db()

    current_year = "Unknown"
    current_teacher = "Unknown"
    current_question = None 
    count = 0

    print(f"開始處理: {pdf_path} 並存入資料庫...")

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line: continue

                # 規則 1: 抓年份
                year_match = re.search(r"生*化*\s*(B\d+)", line)
                if year_match:
                    current_year = year_match.group(1)
                    continue

                # 規則 2: 抓老師
                if line.startswith('➢'):
                    current_teacher = line.replace('➢', '').replace('老師', '').strip()
                    continue

                # 規則 3: 抓題目開頭
                question_match = re.match(r'^(\d+)\.\s+(.*)', line)
                
                if question_match:
                    # 如果有上一題，先存上一題
                    if current_question:
                        save_single_question(current_question)
                        count += 1
                    
                    # 開始新的一題
                    current_question = {
                        "year": current_year,
                        "teacher": current_teacher,
                        "question_id": question_match.group(1),
                        "question_text": question_match.group(2),
                        "options_text": "",
                        "full_text": question_match.group(2)
                    }
                
                # 規則 4: 處理選項或內容
                else:
                    if current_question:
                        current_question["full_text"] += "\n" + line
                        # 簡單判斷是否為選項格式
                        if re.search(r'\([A-E]\)', line):
                            current_question["options_text"] += line + "\n"
                        else:
                            # ★ 關鍵修正：如果不是選項，就代表它是題目的一部分（第二行）！
                            # 我們把它加回 question_text，中間補個空白
                            current_question["question_text"] += " " + line

    # 迴圈結束，存最後一題
    if current_question:
        save_single_question(current_question)
        count += 1

    print(f"\n成功！共將 {count} 題存入 SQLite 資料庫。")

def save_single_question(q_data):
    """ 輔助函數：判斷題型並呼叫資料庫寫入 """

    # 修改 1-2: 過濾「亡佚」題目
    # strip() 會去掉前後空白，確保 " 亡佚 " 也能被抓到
    if q_data["question_text"].strip() == "亡佚":
        print(f"跳過無效題目: {q_data['question_id']} (亡佚)")
        return
    
    # 邏輯判斷：如果 options_text 是空的，或是太短，就當作非選擇題
    # 這裡設定 > 5 個字才算有選項，避免誤判
    if len(q_data["options_text"].strip()) > 5:
        q_data["q_type"] = "選擇題"
    else:
        q_data["q_type"] = "非選擇題"
        
    # 呼叫 db_utils 寫入
    db_utils.insert_question(q_data)

if __name__ == "__main__":
    if os.path.exists(PDF_PATH):
        parse_and_save_exam(PDF_PATH)
    else:
        print(f"找不到檔案: {PDF_PATH}，請確認路徑。")