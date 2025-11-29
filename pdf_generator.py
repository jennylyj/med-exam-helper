from fpdf import FPDF
import pandas as pd
import os

# --- 設定區 ---
# 請確認這裡的檔名跟你剛剛複製進來的字型檔名一樣
FONT_PATH = 'msjh.ttf'  
FONT_NAME = 'MicrosoftJhengHei'

class ExamPDF(FPDF):
    def header(self):
        # 設定標題字型 (粗體)
        self.set_font(FONT_NAME, '', 16)
        # 標題文字
        self.cell(0, 10, '醫學系考古題彙編', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5) # 空行

    def footer(self):
        # 設定頁尾位置 (距離底部 1.5cm)
        self.set_y(-15)
        self.set_font(FONT_NAME, '', 8)
        # 頁碼
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_exam_pdf(questions_df, filename="output/exam_paper.pdf"):
    """
    接收一個 Pandas DataFrame (搜尋結果)，生成 PDF。
    """
    
    # 檢查字型檔是否存在
    if not os.path.exists(FONT_PATH):
        print(f"錯誤：找不到字型檔 '{FONT_PATH}'！請將中文字型檔複製到專案資料夾中。")
        return

    # 初始化 PDF
    pdf = ExamPDF()
    
    # 註冊中文字型
    pdf.add_font(FONT_NAME, '', FONT_PATH)
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font(FONT_NAME, '', 11)

    print(f"正在生成 PDF: {filename} ...")

    # 遍歷每一題
    # enumerate(..., 1) 讓我們可以重新編號 (1, 2, 3...)
    for index, row in enumerate(questions_df.itertuples(), 1):
        
        # 1. 題目資訊 (年份/老師/類型)
        # 設定灰色、小字
        pdf.set_text_color(100, 100, 100)
        pdf.set_font_size(9)
        meta_info = f"[{row.year}] {row.teacher} ({row.q_type})"
        pdf.cell(0, 6, meta_info, new_x="LMARGIN", new_y="NEXT")
        
        # 2. 題目內容
        # 恢復黑色、正常字
        pdf.set_text_color(0, 0, 0)
        pdf.set_font_size(12)
        
        # 題目文字 (加上題號)
        question_content = f"{index}. {row.content}"
        # multi_cell 可以自動換行
        pdf.multi_cell(0, 7, question_content)
        
        # 3. 選項 (如果是選擇題)
        if row.q_type == '選擇題' and row.options:
            pdf.set_font_size(11)
            # 稍微縮排
            pdf.set_x(20) 
            # 處理選項換行
            pdf.multi_cell(0, 6, row.options)
        
        # 每一題之間空一行
        pdf.ln(8)

    # 輸出檔案
    pdf.output(filename)
    print(f"PDF 產出完成！路徑：{filename}")

# --- 測試區 ---
if __name__ == "__main__":
    # 假裝有一筆資料來測試
    data = {
        'year': ['B12', 'B12'],
        'teacher': ['顏老師', '顏老師'],
        'q_type': ['選擇題', '選擇題'],
        'content': ['下列關於 DNA 的敘述何者正確？', '測試題目二'],
        'options': ['(A) 選項一\n(B) 選項二', '(A) A\n(B) B']
    }
    df = pd.DataFrame(data)
    
    generate_exam_pdf(df, "test_exam.pdf")

def get_pdf_bytes(questions_df):
    """
    生成 PDF 並回傳二進位資料 (bytes)，供 Streamlit 下載按鈕使用
    """
    if not os.path.exists(FONT_PATH):
        return None

    pdf = ExamPDF()
    pdf.add_font(FONT_NAME, '', FONT_PATH)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font(FONT_NAME, '', 11)

    # 遍歷每一題
    # enumerate(..., 1) 讓我們可以重新編號 (1, 2, 3...)
    for index, row in enumerate(questions_df.itertuples(), 1):
        
        # 1. 題目資訊 (年份/老師/類型)
        # 設定灰色、小字
        pdf.set_text_color(100, 100, 100)
        pdf.set_font_size(9)
        meta_info = f"[{row.year}] {row.teacher} ({row.q_type})"
        pdf.cell(0, 6, meta_info, new_x="LMARGIN", new_y="NEXT")
        
        # 2. 題目內容
        # 恢復黑色、正常字
        pdf.set_text_color(0, 0, 0)
        pdf.set_font_size(12)
        
        # 題目文字 (加上題號)
        question_content = f"{index}. {row.content}"
        # multi_cell 可以自動換行
        pdf.multi_cell(0, 7, question_content)
        
        # 3. 選項 (如果是選擇題)
        if row.q_type == '選擇題' and row.options:
            pdf.set_font_size(11)
            # 稍微縮排
            pdf.set_x(20) 
            # 處理選項換行
            pdf.multi_cell(0, 6, row.options)
        
        # 每一題之間空一行
        pdf.ln(8)

    # === 修改這行 ===
    # 原本是: return pdf.output()
    # 請改成下面這樣，用 bytes() 包起來：
    return bytes(pdf.output())

