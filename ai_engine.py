import pandas as pd
import numpy as np

# ----------- 1) เก็บข้อมูลจาก chatbot (ชั้นก้ไม่รู้คือไร โง่เลยอันนี้)-------------
records = []

def add_transaction(t):
    """
    t = {
        "Date": "2025-01-01",
        "Category": "Food",
        "Type": "expense",
        "Amount": 120
    }
    """
    records.append(t)

def build_df():
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


# ----------- clean ข้อมูลเเล้ว ----------
def clean_df(df):
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    if 'Amount' in df.columns:
        df['Amount'] = (df['Amount'].astype(str)
                                     .str.replace(',', '')
                                     .str.strip())
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    df['Type_norm'] = df['Type'].astype(str).str.strip().str.lower() if 'Type' in df.columns else ''
    df['Category_norm'] = df['Category'].astype(str).str.strip().str.lower() if 'Category' in df.columns else ''
    return df


# ----------- 3) ฟังก์ชันวิเคราะห์ (เธอเขียนไว้ดีแล้ว) ----------
def get_top_category(df_exp):
    if df_exp.empty:
        return None, 0

    cat_sum = df_exp.groupby('Category_norm')['Amount'].sum()
    top_key = cat_sum.idxmax()
    top_amt = float(cat_sum.max())

    mask = df_exp['Category_norm'] == top_key
    try:
        top_label = df_exp.loc[mask, 'Category'].iloc[0]
    except:
        top_label = top_key

    return top_label, top_amt


def get_daily_average(df_exp):
    if 'Date' not in df_exp.columns:
        return np.nan

    df2 = df_exp[df_exp['Date'].notna()]
    if df2.empty:
        return np.nan

    daily_total = df2.groupby(df2['Date'].dt.date)['Amount'].sum()
    return float(daily_total.mean())

#--------จะใช้ไม่ใช้ก้ได้ ทำมาเผื่อคือvisualisation--------
def get_pie_data(df_exp):
    if df_exp.empty:
        return []

    cat_sum = df_exp.groupby('Category')['Amount'].sum().reset_index()
    cat_sum = cat_sum.sort_values(by='Amount', ascending=False)
    return cat_sum.to_dict(orient='records')

#----------------
def analyze_behavior(df_exp):
    insights = []
    if df_exp.empty:
        return insights

    cat_sum = df_exp.groupby('Category_norm')['Amount'].sum()
    total = cat_sum.sum()
    if total <= 0:
        return insights

    def get_sum_by_keywords(keywords):
        total_amt = 0
        for kw in keywords:
            matches = [idx for idx in cat_sum.index if kw in str(idx)]
            for m in matches:
                total_amt += float(cat_sum[m])
        return total_amt

    food_keys = ['อาหาร', 'food', 'meal', 'eat']
    travel_keys = ['เดินทาง', 'transport', 'travel', 'commute']
    shopping_keys = ['shopping', 'ช้อป', 'ช็อป', 'ซื้อ']

    food_amt = get_sum_by_keywords(food_keys)
    travel_amt = get_sum_by_keywords(travel_keys)
    shop_amt = get_sum_by_keywords(shopping_keys)

    if food_amt / total > 0.40:
        insights.append(f"คุณใช้เงินในหมวดอาหารมากกว่า 40% ({food_amt:.2f} / {total:.2f})")

    if travel_amt / total > 0.25:
        insights.append(f"ค่าเดินทางสูงกว่าปกติ (>25%): {travel_amt:.2f} บาท")

    if shop_amt / total > 0.25:
        insights.append(f"ค่าใช้จ่ายหมวดช้อปปิ้งสูง (>25%): {shop_amt:.2f} บาท")

    daily_avg = get_daily_average(df_exp)
    if not np.isnan(daily_avg) and daily_avg > 300:
        insights.append(f"ค่าใช้จ่ายเฉลี่ยต่อวันค่อนข้างสูง ({daily_avg:.2f} บาท)")

    return insights


# ----------- 4) ทดลองเหมือน chatbot ส่งมา (คืออะไรไม่รู้ chat gen มา)----------
add_transaction({"Date": "2025-01-01", "Category": "Food", "Type": "expense", "Amount": 120})
add_transaction({"Date": "2025-01-01", "Category": "Transport", "Type": "expense", "Amount": 40})
add_transaction({"Date": "2025-01-02", "Category": "Salary", "Type": "income", "Amount": 5000})
add_transaction({"Date": "2025-01-02", "Category": "Shopping", "Type": "expense", "Amount": 900})

df = clean_df(build_df())

df_exp = df[(df['Type_norm'].str.contains('exp', na=False)) & (df['Amount'].notna())]

top_cat, top_amt = get_top_category(df_exp)
avg_daily  = get_daily_average(df_exp)
pie        = get_pie_data(df_exp)
insights   = analyze_behavior(df_exp)

print("Top category:", top_cat, "Amount:", top_amt)
print("Daily average:", avg_daily)
print("Pie:", pie)
print("Insights:", insights)

