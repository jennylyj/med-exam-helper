import search_engine
import pdf_generator
import os
import time

def main():
    while True:
        print("\n" + "="*30)
        print("  醫學系考古題神器 v1.0")
        print("="*30)
        print("1. 搜尋題目並匯出 PDF")
        print("2. 抓出重複考題並匯出 PDF")
        print("q. 離開")
        
        choice = input("\n請選擇功能: ")
        
        if choice == '1':
            print("\n--- 搜尋模式 ---")
            teacher = input("老師姓名 (Enter跳過): ").strip() or None
            year = input("年份 (Enter跳過): ").strip() or None
            keyword = input("關鍵字 (Enter跳過): ").strip() or None
            
            # 執行搜尋
            df = search_engine.search_questions(year, teacher, keyword)
            
            if df.empty:
                print("找不到資料耶！")
            else:
                print(f"找到 {len(df)} 題！")
                # 詢問是否匯出
                if input("要匯出成 PDF 嗎？(y/n): ").lower() == 'y':
                    filename = f"output/exam_{int(time.time())}.pdf"
                    pdf_generator.generate_exam_pdf(df, filename)
                    # 自動打開檔案 (Mac用 open, Windows用 start)
                    try:
                        if os.name == 'nt': # Windows
                            os.startfile(filename)
                        else: # Mac / Linux
                            os.system(f"open {filename}")
                    except:
                        pass

        elif choice == '2':
            print("\n--- 抓題模式 ---")
            df = search_engine.find_duplicate_questions()
            
            if df.empty:
                print("沒發現重複題目。")
            else:
                print(f"發現 {len(df)} 組重複題目！")
                if input("要匯出成 PDF 嗎？(y/n): ").lower() == 'y':
                    filename = f"output/duplicate_questions.pdf"
                    pdf_generator.generate_exam_pdf(df, filename)

        elif choice == 'q':
            print("祝考試順利！加油！")
            break

if __name__ == "__main__":
    # 確保輸出資料夾存在
    if not os.path.exists('output'):
        os.makedirs('output')
        
    main()