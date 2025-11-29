import streamlit as st
import os
import pandas as pd
import search_engine
import pdf_generator

# --- 設定網頁基本資訊 ---
st.set_page_config(
    page_title="醫學系考古題神器",
    page_icon="💊",
    layout="wide"
)

# --- 側邊欄：設定與資料庫 ---
with st.sidebar:
    st.header("⚙️ 設定面板")
    
    # 1. 讀取 databases 資料夾下的所有 .db 檔案
    db_folder = "databases"
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        st.error(f"請將 .db 資料庫檔案放入 {db_folder} 資料夾中！")
        db_files = []
    else:
        db_files = [f for f in os.listdir(db_folder) if f.endswith('.db')]

    # 2. 資料庫選擇器
    selected_db = st.selectbox("📂 請選擇考試範圍 (資料庫)", db_files)
    
    # 取得完整路徑
    db_path = os.path.join(db_folder, selected_db) if selected_db else None

    # --- 修改點 2-1: 這裡加入動態老師名單 ---
    teacher_options = ["所有老師"] # 預設選項
    if db_path:
        # 去資料庫撈老師名單
        teachers_in_db = search_engine.get_all_teachers(db_path)
        teacher_options += teachers_in_db


    st.divider() # 分隔線
    
    # 3. 功能模式選擇
    mode = st.radio("功能選擇", ["🔍 搜尋題目", "⚡ 抓重複考題","✨模糊抓題（進階）"])

# --- 主畫面 ---
st.title("💊 醫學系考古題整理神器")
st.markdown("""
> **創作理念**：
> 考古題是醫學系傳承的瑰寶，但分散的 PDF 難以檢索。
> 這個工具希望幫助大家「精準打擊」，不再大海撈針，把時間花在真正重要的觀念上。
""")

# 如果沒有選資料庫，就停止執行
if not db_path:
    st.warning("👈 請先在左側選擇一個資料庫")
    st.stop()

# --- 模式 A: 搜尋題目 ---
if mode == "🔍 搜尋題目":
    st.subheader(f"搜尋範圍：{selected_db}")
    
    # 建立三欄排版
    col1, col2, col3 = st.columns(3)
    with col1:
        year_input = st.text_input("年份 (例如 B12)", "")
    with col2:
        # --- 修改點 2-1: 改用 selectbox ---
        selected_teacher = st.selectbox("出題老師", teacher_options)
        # 如果選「所有老師」，搜尋時就傳入 None
        teacher_query = None if selected_teacher == "所有老師" else selected_teacher
    with col3:
        keyword_input = st.text_input("題目關鍵字", "")

    # 搜尋按鈕
    if st.button("開始搜尋", type="primary"):
        # 呼叫搜尋引擎
        df = search_engine.search_questions(
            db_path, 
            year=year_input if year_input else None,
            teacher=selected_teacher if selected_teacher else None,
            keyword=keyword_input if keyword_input else None
        )
        
        if df.empty:
            st.info("找不到符合條件的題目，換個關鍵字試試看？")
        else:
            st.success(f"找到 {len(df)} 題！")
            st.dataframe(df) # 顯示表格
            
            # 生成 PDF Bytes
            pdf_bytes = pdf_generator.get_pdf_bytes(df)
            
            if pdf_bytes:
                st.download_button(
                    label="📥 下載搜尋結果 PDF",
                    data=pdf_bytes,
                    file_name="search_result.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("無法生成 PDF，請檢查字型檔是否遺失。")

# --- 模式 B: 抓重複題 ---
elif mode == "⚡ 抓重複考題":
    st.subheader("分析結果")
    
    min_count = st.slider("至少重複幾次才顯示？", 2, 6, 2)
    
    if st.button("開始分析"):
        df = search_engine.find_duplicate_questions(db_path, min_count)
        
        if df.empty:
            st.info("目前沒有發現重複的題目。")
        else:
            st.success(f"發現 {len(df)} 組重複題目！這些是必考重點！")
            st.dataframe(df)
            
            # 這裡要注意：find_duplicate_questions 回傳的欄位跟 PDF 生成器需要的欄位不一樣
            # 為了方便，我們暫時不提供重複題的 PDF 下載，或者你可以試著自己修改 pdf_generator 來支援這種格式
            st.caption("目前重複題模式僅提供線上瀏覽，若需下載請至搜尋模式搜尋特定題目。")


elif mode == "✨模糊抓題（進階）":
    st.subheader("🕵️‍♀️ 相似題目分析")
    st.info("這裡使用「模糊搜尋」演算法，就算題目多一個空格或錯字也能抓出來！")
    
    # 設定門檻值的滑桿
    threshold = st.slider("相似度門檻 (越低抓越寬，建議 70~85)", 50, 100, 85)
    
    if st.button("開始分析 (可能會跑一下下)"):
        with st.spinner('正在逐題比對中...'): # 顯示轉圈圈特效
            # ★★★ 關鍵修改在這裡！ ★★★
            # 確保呼叫的是 search_engine 裡的 find_fuzzy_duplicates
            # 並且傳入 db_path 和 threshold
            df = search_engine.find_fuzzy_duplicates(db_path, threshold)
        
        # 顯示結果
        if df.empty:
            st.info("沒有發現相似的題目。")
        else:
            st.success(f"發現 {len(df)} 組相似題目！")
            st.dataframe(df) # 顯示表格
            st.caption("註：這是透過 Python 文字比對算出來的結果。")

            
# --- 頁尾簽名 ---
st.divider()
st.caption("Designed by 李昀臻 | 製作於某個涼爽的午後 🍃")
