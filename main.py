import streamlit as st

# ページ設定
st.set_page_config(page_title="賢者の車選びシミュレーター", page_icon="🚗")

# デザイン設定
st.markdown("""
    <style>
    .block-container { max-width: 800px; padding-top: 2rem; }
    .stMetric { background-color: rgba(128, 128, 128, 0.1); padding: 15px; border-radius: 10px; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; }
    /* 内訳の文字サイズを少し調整 */
    .streamlit-expanderContent { font-size: 0.9rem; }
    /* ラジオボタンの文字サイズをスマホで1行に収まるよう調整 */
    div[role="radiogroup"] label p { font-size: 0.85rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 賢者の車選びシミュレーター")
st.write("「軽自動車」と「普通車」の維持費をリアルに比較。")

# --- 1. 基本条件 ---
with st.container(border=True):
    # フォントサイズを1.2remに固定し、1行に収める
    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 0.5rem;'>🗓️ シミュレーションの基本条件</h3>", unsafe_allow_html=True)
    
    col_base1, col_base2 = st.columns(2)
    
    with col_base1:
        years = st.selectbox("保有予定期間 (年)", options=[3, 4, 5, 6, 7, 8, 9, 10], index=2)
        dist = st.number_input("年間走行距離 (km)", value=10000, step=1000, format="%d")
        
    with col_base2:
        gas = st.selectbox("ガソリン単価 (円/L)", options=list(range(150, 201, 5)), index=5)
        
    st.divider()
    
    # 【修正】セレクトボックスからラジオボタンに変更し、横幅いっぱいを使って縦に並べる
    ins_type = st.radio(
        "保険プラン", 
        options=[
            "基本プラン（対人対物無制限）", 
            "安心プラン（対人対物無制限 ＋ 車両保険エコノミー）", 
            "万全プラン（対人対物無制限 ＋ 車両保険一般）"
        ], 
        index=1
    )

    st.divider()
    col_tire1, col_tire2 = st.columns(2)
    with col_tire1:
        is_winter = st.toggle("スタッドレスタイヤを使用", value=True)
    with col_tire2:
        w_months = st.selectbox("冬タイヤ装着期間 (ヶ月)", options=[1, 2, 3, 4, 5, 6], index=2) if is_winter else 0

# --- 計算ロジック ---
def get_resale_price(p, y, is_new):
    r = {3:0.6, 4:0.5, 5:0.4, 6:0.3, 7:0.2, 8:0.15, 9:0.1, 10:0.05} if is_new else {3:0.45, 4:0.35, 5:0.25, 6:0.2, 7:0.15, 8:0.1, 9:0.05, 10:0.03}
    return int(p * r.get(y, 0.05))

def calc_all(price, mpg, is_kei, is_new, is_resale_included, t_unit, w_price, change_fee):
    resale_val = get_resale_price(price, years, is_new)
    actual_dep = (price - resale_val) if is_resale_included else price
    
    fuel = (dist * years / mpg) * gas
    tax = (10800 if is_kei else 30500) * years
    shaken = (years // 2) * (60000 if is_kei else 100000)
    
    base_ins = (35000 if is_kei else 45000)
    ins_rate = 0.025 if "万全" in ins_type else (0.015 if "安心" in ins_type else 0.0)
    ins_total = (base_ins + (price * ins_rate)) * years
    
    tire_usage = (int(dist * years * 0.7 / 30000) * t_unit) 
    winter_cost = ((t_unit + w_price + (change_fee * years)) if is_winter else 0)
    tire_total = tire_usage + winter_cost
    
    total = int(actual_dep + fuel + tax + shaken + ins_total + tire_total)
    
    return total, resale_val, int(actual_dep), int(fuel), int(tax), int(shaken), int(ins_total), int(tire_total)

# --- 2. 車両比較 ---
# フォントサイズを1.2remに固定し、1行に収める
st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 0.5rem;'>🚘 比較する車両の入力</h3>", unsafe_allow_html=True)

resale_help = """
**予想売却価格（残価）の計算根拠:**
保有期間に応じた一般的な残価率を車両価格に乗じて算出しています。

**【残価率の目安（新車 / 中古）】**
- **3年**: 60% / 45%
- **5年**: 40% / 25%
- **7年**: 20% / 15%
- **10年**: 5% / 3%
"""
is_resale_included = st.toggle("保有期間後の予想売却価格を計算に含める", value=True, help=resale_help)

col_v1, col_v2 = st.columns(2)

with col_v1:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 1.1rem; margin-bottom: 0.5rem;'>【A】軽自動車</h4>", unsafe_allow_html=True)
        
        k_age = st.selectbox("車両の状態・年式", ["新車（最新モデル）", "中古（3〜5年落ち程度）", "中古（10年落ち程度）"], key="k_age")
        if "新車" in k_age:
            k_is_new = True; k_default_p = 2000000; k_default_m = 22.0
        elif "3〜5年" in k_age:
            k_is_new = False; k_default_p = 1200000; k_default_m = 18.0
        else:
            k_is_new = False; k_default_p = 500000; k_default_m = 14.0
            
        k_p = st.number_input("購入価格 (円)", value=k_default_p, step=100000, format="%d", key="k_p")
        k_m = st.number_input("実用燃費 (km/L)", value=k_default_m, step=1.0, key="k_m")
        
        st.markdown("<div style='height: 70px;'>※タイヤは軽自動車標準サイズを想定</div>", unsafe_allow_html=True)
        
        k_total, k_resale, k_dep, k_fuel, k_tax, k_shaken, k_ins, k_tire = calc_all(k_p, k_m, True, k_is_new, is_resale_included, 35000, 20000, 6000)
        if is_resale_included:
            st.info(f"💡 {years}年後の予想売却価格: **{k_resale:,}円**")

with col_v2:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 1.1rem; margin-bottom: 0.5rem;'>【B】普通車</h4>", unsafe_allow_html=True)
        
        s_age = st.selectbox("車両の状態・年式", ["新車（最新モデル）", "中古（3〜5年落ち程度）", "中古（10年落ち程度）"], index=1, key="s_age")
        if "新車" in s_age:
            s_is_new = True; s_default_p = 3500000; s_default_m = 20.0
        elif "3〜5年" in s_age:
            s_is_new = False; s_default_p = 2000000; s_default_m = 15.0
        else:
            s_is_new = False; s_default_p = 800000; s_default_m = 10.0
            
        s_p = st.number_input("購入価格 (円)", value=s_default_p, step=100000, format="%d", key="s_p")
        s_m = st.number_input("実用燃費 (km/L)", value=s_default_m, step=1.0, key="s_m")
        
        s_tire_size = st.selectbox("タイヤサイズ", [
            "15インチ以下（コンパクトカー等）", 
            "16〜17インチ（ミドルクラス等）", 
            "18インチ以上（SUV・高級車等）"
        ], index=1)
        
        if "15" in s_tire_size:
            s_t_unit = 40000; s_w_price = 40000; s_c_fee = 8000
        elif "16" in s_tire_size:
            s_t_unit = 80000; s_w_price = 60000; s_c_fee = 10000
        else:
            s_t_unit = 120000; s_w_price = 80000; s_c_fee = 12000
            
        s_total, s_resale, s_dep, s_fuel, s_tax, s_shaken, s_ins, s_tire = calc_all(s_p, s_m, False, s_is_new, is_resale_included, s_t_unit, s_w_price, s_c_fee)
        if is_resale_included:
            st.info(f"💡 {years}年後の予想売却価格: **{s_resale:,}円**")

# --- 3. 結果発表 ---
st.divider()
# フォントサイズを1.2remに固定し、1行に収める
st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 0.5rem;'>📊 算出結果（トータルコスト）</h3>", unsafe_allow_html=True)

res_c1, res_c2 = st.columns(2)

with res_c1:
    st.metric("軽自動車 合計", f"{k_total:,}円")
    with st.expander("🔍 内訳を見る"):
        st.write(f"- 車両実質負担額: {k_dep:,}円")
        st.write(f"- ガソリン代: {k_fuel:,}円")
        st.write(f"- 自動車税: {k_tax:,}円")
        st.write(f"- 車検代: {k_shaken:,}円")
        st.write(f"- 任意保険: {k_ins:,}円")
        st.write(f"- タイヤ関連費: {k_tire:,}円")

with res_c2:
    st.metric("普通車 合計", f"{s_total:,}円")
    with st.expander("🔍 内訳を見る"):
        st.write(f"- 車両実質負担額: {s_dep:,}円")
        st.write(f"- ガソリン代: {s_fuel:,}円")
        st.write(f"- 自動車税: {s_tax:,}円")
        st.write(f"- 車検代: {s_shaken:,}円")
        st.write(f"- 任意保険: {s_ins:,}円")
        st.write(f"- タイヤ関連費: {s_tire:,}円")

diff = s_total - k_total

if diff > 0:
    st.warning(f"普通車の方が **{diff:,}円** 高くなります。")
elif diff < 0:
    st.success(f"軽自動車の方が **{abs(diff):,}円** 高くなります。")
else:
    st.info("両者のトータルコストは同じです。")

# --- 4. 計算根拠 ---
with st.expander("🧮 賢者の計算根拠・前提条件"):
    resale_text = f"（購入価格 ー {years}年後の予想売却価格）" if is_resale_included else "（購入価格のみ ※売却なし）"
    st.markdown(f"""
    本シミュレーターは以下の条件で算出しています。
    
    * **車両実質負担額**: {resale_text} をベースに計算。新車・中古の選択により残価率が異なります。
    * **燃料代**: 走行距離 ÷ 実用燃費 × ガソリン単価 で算出。
    * **自動車税**: 軽自動車 10,800円/年、普通車 30,500円/年。
    * **車検代**: 2年に1回（軽: 6万、普通: 10万）と仮定。
    * **任意保険**: プランに応じた料率を購入価格に乗じ、基本料を加算。
    * **タイヤ関連費（消耗＋スタッドレス導入費＋毎年の履き替え工賃）**:
      * **軽自動車**: タイヤ約3.5万円 / ホイール約2万円 / 履き替え工賃 6,000円(年2回分)
      * **普通 15インチ以下**: タイヤ約4万円 / ホイール約4万円 / 履き替え工賃 8,000円(年2回分)
      * **普通 16〜17インチ**: タイヤ約8万円 / ホイール約6万円 / 履き替え工賃 10,000円(年2回分)
      * **普通 18インチ以上**: タイヤ約12万円 / ホイール約8万円 / 履き替え工賃 12,000円(年2回分)
    """)
