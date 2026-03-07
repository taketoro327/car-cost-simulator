import streamlit as st

# ページ設定
st.set_page_config(page_title="賢者の車選びシミュレーター", page_icon="🚗")

# デザイン設定
st.markdown("""
    <style>
    .block-container { max-width: 800px; padding-top: 2rem; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 賢者の車選びシミュレーター")
st.write("「軽自動車」と「普通車」の維持費をリアルに比較。")

# --- 1. 基本条件 ---
with st.container(border=True):
    st.subheader("🗓️ シミュレーションの基本条件")
    col_base1, col_base2 = st.columns(2)
    
    with col_base1:
        years = st.selectbox("保有予定期間 (年)", options=[3, 4, 5, 6, 7, 8, 9, 10], index=2)
        dist = st.number_input("年間走行距離 (km)", value=10000, step=1000, format="%d")
        
    with col_base2:
        gas = st.selectbox("ガソリン単価 (円/L)", options=list(range(150, 201, 5)), index=5)
        ins_type = st.selectbox("保険プラン", [
            "基本プラン（対人対物無制限）", 
            "安心プラン（対人対物無制限＋車両保険エコノミー）", 
            "万全プラン（対人対物無制限＋車両保険一般）"
        ], index=1)

    st.divider()
    col_tire1, col_tire2 = st.columns(2)
    with col_tire1:
        is_winter = st.toggle("スタッドレスタイヤを使用", value=True)
    with col_tire2:
        w_months = st.selectbox("冬タイヤ装着期間 (ヶ月)", options=[1, 2, 3, 4, 5, 6], index=2) if is_winter else 0

# --- 計算ロジック ---
def get_resale_price(p, y, is_new):
    # 保有期間に応じた残価率のテーブル
    r = {3:0.6, 4:0.5, 5:0.4, 6:0.3, 7:0.2, 8:0.15, 9:0.1, 10:0.05} if is_new else {3:0.45, 4:0.35, 5:0.25, 6:0.2, 7:0.15, 8:0.1, 9:0.05, 10:0.03}
    return int(p * r.get(y, 0.05))

def calc_all(price, mpg, is_kei, is_new, is_resale_included):
    resale_val = get_resale_price(price, years, is_new)
    actual_dep = (price - resale_val) if is_resale_included else price
    
    fuel = (dist * years / mpg) * gas
    tax = (10800 if is_kei else 30500) * years
    shaken = (years // 2) * (60000 if is_kei else 100000)
    
    base_ins = (35000 if is_kei else 45000)
    ins_rate = 0.025 if "万全プラン" in ins_type else (0.015 if "安心プラン" in ins_type else 0.0)
    ins_total = (base_ins + (price * ins_rate)) * years
    
    t_unit = 35000 if is_kei else 80000
    tire_usage = (int(dist * years * 0.7 / 30000) * t_unit)
    winter_cost = ((t_unit + 40000 + 8000 * years) if is_winter else 0)
    
    total = int(actual_dep + fuel + tax + shaken + ins_total + (tire_usage + winter_cost))
    return total, resale_val

# --- 2. 車両比較 ---
st.header("🚘 比較する車両の入力")

# 【修正】ヘルプテキストを現在のロジックに完全一致させました
resale_help = """
**予想売却価格（残価）の計算根拠:**
保有期間に応じた一般的な残価率を車両価格に乗じて算出しています。

**【残価率の目安（新車 / 中古）】**
- **3年**: 60% / 45%
- **5年**: 40% / 25%
- **7年**: 20% / 15%
- **10年**: 5% / 3%

※走行距離や市場ニーズにより変動しますが、本ツールでは標準的な下取り相場を採用しています。
"""
is_resale_included = st.toggle("保有期間後の予想売却価格を計算に含める", value=True, help=resale_help)

col_v1, col_v2 = st.columns(2)

with col_v1:
    with st.container(border=True):
        st.subheader("【A】軽自動車")
        k_p = st.number_input("購入価格 (円)", value=2000000, step=100000, format="%d", key="k_p")
        k_m = st.number_input("実用燃費 (km/L)", value=20.0, step=1.0, key="k_m")
        k_total, k_resale = calc_all(k_p, k_m, True, True, is_resale_included)
        if is_resale_included:
            st.info(f"💡 {years}年後の予想売却価格: **{k_resale:,}円**")

with col_v2:
    with st.container(border=True):
        st.subheader("【B】普通車")
        s_p = st.number_input("購入価格 (円)", value=3000000, step=100000, format="%d", key="s_p")
        s_m = st.number_input("実用燃費 (km/L)", value=15.0, step=1.0, key="s_m")
        s_total, s_resale = calc_all(s_p, s_m, False, False, is_resale_included)
        if is_resale_included:
            st.info(f"💡 {years}年後の予想売却価格: **{s_resale:,}円**")

# --- 3. 結果発表 ---
st.divider()
st.header("📊 算出結果（トータルコスト）")
res_c1, res_c2 = st.columns(2)

res_c1.metric("軽自動車 合計", f"{k_total:,}円")
res_c2.metric("普通車 合計", f"{s_total:,}円")

diff = s_total - k_total
if diff > 0:
    st.error(f"普通車の方が **{diff:,}円** 高くなります。")
else:
    st.success(f"普通車の方が **{abs(diff):,}円** お得です！")

# --- 4. 計算根拠 ---
with st.expander("🧮 賢者の計算根拠・前提条件"):
    resale_text = f"（購入価格 ー {years}年後の予想売却価格）" if is_resale_included else "（購入価格のみ ※売却なし）"
    st.markdown(f"""
    本シミュレーターは以下の条件で算出しています。
    
    * **車両実質負担額**: {resale_text} をベースに計算。
    * **燃料代**: 走行距離 ÷ 実用燃費 × ガソリン単価 で算出。
    * **自動車税**: 軽自動車 10,800円/年、普通車 30,500円/年。
    * **車検代**: 2年に1回（軽: 6万、普通: 10万）と仮定。
    * **任意保険**: プランに応じた料率を購入価格に乗じ、基本料を加算。
    * **タイヤ代**: 走行3万kmごとの交換費用と、スタッドレス維持費を含む。
    """)
