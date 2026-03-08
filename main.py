import streamlit as st
import base64
from io import BytesIO
from PIL import Image

# ページ設定
st.set_page_config(page_title="賢者の車選びシミュレーター", page_icon="🚗")

# --- 画像を丸く処理する関数 ---
def get_image_base64(img_path):
    try:
        img = Image.open(img_path).convert("RGBA")
        # 正方形にクロップ（中央合わせ）
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2
        img = img.crop((left, top, right, bottom))
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except:
        return None

# アイコンの読み込み
icon_base64 = get_image_base64("賢者アイコン用.png")

# デザイン設定
st.markdown("""
    <style>
    /* 【修正】padding-topを2remから4remに増やし、上部の見切れを解消 */
    .block-container { max-width: 800px; padding-top: 4rem; }
    .stMetric { background-color: rgba(128, 128, 128, 0.1); padding: 15px; border-radius: 10px; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; }
    .streamlit-expanderContent { font-size: 0.85rem; line-height: 1.6; }
    div[role="radiogroup"] label p { font-size: 0.85rem !important; }
    /* メインタイトルのサイズ調整 */
    h1 { font-size: 1.1rem !important; font-weight: bold; }
    
    /* ヘッダーエリアのレイアウト */
    .header-box {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 1.0rem;
    }
    .header-icon {
        width: 65px;
        height: 65px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ff4b4b;
    }
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .header-title {
        font-size: 1.1rem !important;
        font-weight: bold;
        margin: 0;
        line-height: 1.2;
    }
    .youtube-link {
        font-size: 0.85rem;
        color: #ff4b4b;
        text-decoration: none;
        margin-top: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP：アイコン・タイトル・YouTubeリンク ---
if icon_base64:
    header_html = f"""
    <div class="header-box">
        <img src="data:image/png;base64,{icon_base64}" class="header-icon">
        <div class="header-text">
            <div class="header-title">🚗 賢者の車選びシミュレーター</div>
            <a href="https://www.youtube.com/channel/UCAaiMudxwrWJ8aob8j2nr3w" target="_blank" class="youtube-link">▶ YouTube 賢者の回顧録</a>
        </div>
    </div>
    """
else:
    header_html = '<h1 style="font-size: 1.1rem;">🚗 賢者の車選びシミュレーター</h1>'

st.markdown(header_html, unsafe_allow_html=True)
st.write("「軽自動車」と「普通車」の購入費・維持費・リセールを、物理法則と市場データに基づきリアルに比較。")

# アクセスカウンター
st.markdown(
    "![Visitors](https://komarev.com/ghpvc/?username=kenja-car-v11&label=Visitors&color=red&style=flat-square)"
)

# --- 1. 基本条件入力 ---
with st.container(border=True):
    st.markdown("<h3 style='font-size: 1.1rem; margin-bottom: 0.5rem;'>🗓️ シミュレーションの基本条件</h3>", unsafe_allow_html=True)
    
    col_base1, col_base2 = st.columns(2)
    with col_base1:
        years = st.selectbox("保有予定期間 (年)", options=[3, 4, 5, 6, 7, 8, 9, 10], index=2)
        dist = st.number_input("年間走行距離 (km)", value=10000, step=1000, format="%d")
    with col_base2:
        gas = st.selectbox("ガソリン単価 (円/L)", options=list(range(150, 201, 5)), index=5)
        highway_freq = st.selectbox("高速道路の利用頻度", options=["ほぼ使わない", "月1〜2回程度", "週1回以上（頻繁）"], index=1)
    
    st.divider()
    ins_type = st.radio(
        "保険プラン（※全プラン対人対物無制限）", 
        options=["基本（車両なし）", "安心（＋車両エコノミー）", "万全（＋車両一般）"], 
        index=1, horizontal=True
    )

    st.divider()
    col_tire1, col_tire2 = st.columns(2)
    with col_tire1:
        is_winter = st.toggle("スタッドレスタイヤを使用", value=True)
    with col_tire2:
        w_months = st.selectbox("冬タイヤ装着期間 (ヶ月)", options=[1, 2, 3, 4, 5, 6], index=2) if is_winter else 0

# --- 2. 計算ロジック ---

def get_resale_rate(years, is_kei, is_new):
    rates = {
        "kei_new": [0.65, 0.55, 0.50, 0.40, 0.30, 0.20, 0.15, 0.10],
        "kei_used": [0.55, 0.50, 0.45, 0.35, 0.25, 0.15, 0.10, 0.05],
        "std_new": [0.55, 0.45, 0.40, 0.30, 0.20, 0.15, 0.10, 0.05],
        "std_used": [0.55, 0.50, 0.45, 0.35, 0.25, 0.15, 0.10, 0.05]
    }
    key = ("kei" if is_kei else "std") + ("_new" if is_new else "_used")
    idx = max(0, min(len(rates[key]) - 1, years - 3))
    return rates[key][idx]

def calc_all(price, mpg, is_kei, age_label, is_resale_included, t_unit, w_price, change_fee):
    is_new = "新車" in age_label
    resale_val = int(price * get_resale_rate(years, is_kei, is_new))
    actual_dep = (price - resale_val) if is_resale_included else price
    fuel = (dist * years / mpg) * gas
    start_age = 0 if is_new else (4 if "3〜5年" in age_label else (8 if "6〜9年" in age_label else 12))
    total_tax = 0
    for i in range(1, years + 1):
        current_age = start_age + i
        if is_kei:
            annual_tax = 12900 if current_age > 13 else 10800
        else:
            annual_tax = 35000 if current_age > 13 else 30500 
        total_tax += annual_tax
    shaken_base = 60000 if is_kei else 100000
    shaken_count = years // 2
    shaken_total = shaken_count * (shaken_base * 1.2 if (start_age + years) > 13 else shaken_base)
    base_ins = (35000 if is_kei else 45000)
    ins_rate = 0.025 if "万全" in ins_type else (0.015 if "安心" in ins_type else 0.0)
    ins_total = (base_ins + (price * ins_rate)) * years
    highway_factor = 1.0
    if is_kei:
        if highway_freq == "週1回以上（頻繁）": highway_factor = 1.4
        elif highway_freq == "月1〜2回程度": highway_factor = 1.2
    basic_maint = (15000 * years) * highway_factor
    total_mileage = (start_age * 10000) + (dist * years)
    extra_maint = 100000 if (is_kei and total_mileage >= 100000) else (120000 if total_mileage >= 100000 else 0)
    tire_usage = (int(dist * years * 0.7 / 30000) * t_unit) 
    winter_cost = ((t_unit + w_price + (change_fee * years)) if is_winter else 0)
    maint_total = tire_usage + winter_cost + basic_maint + extra_maint
    total = int(actual_dep + fuel + total_tax + shaken_total + ins_total + maint_total)
    return total, resale_val, int(actual_dep), int(fuel), int(total_tax), int(shaken_total), int(ins_total), int(maint_total)

# --- 3. 車両比較入力 ---
st.markdown("<h3 style='font-size: 1.1rem; margin-bottom: 0.5rem;'>🚘 比較する車両の入力</h3>", unsafe_allow_html=True)

resale_help = "【出典：ネクステージ等の市場データを参照】保有期間に応じた一般的な残価率を算出。"
is_resale_included = st.toggle("保有期間後の予想売却価格を計算に含める", value=True, help=resale_help)

col_v1, col_v2 = st.columns(2)
age_options = ["新車（最新モデル）", "中古（3〜5年落ち）", "中古（6〜9年落ち）", "中古（10年落ち〜）"]

with col_v1:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 1.1rem;'>【A】軽自動車</h4>", unsafe_allow_html=True)
        k_age = st.selectbox("車両の状態", age_options, key="k_age")
        k_p = st.number_input("購入価格 (円)", value=2000000 if "新車" in k_age else 1000000, step=100000, key="k_p")
        k_m = st.number_input("実用燃費 (km/L)", value=22.0 if "新車" in k_age else 18.0, step=1.0, key="k_m")
        k_total, k_resale, k_dep, k_fuel, k_tax, k_shaken, k_ins, k_tire = calc_all(k_p, k_m, True, k_age, is_resale_included, 35000, 20000, 6000)
        if is_resale_included: st.info(f"💡 予想売却価格: **{k_resale:,}円**")

with col_v2:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 1.1rem;'>【B】普通車</h4>", unsafe_allow_html=True)
        s_age = st.selectbox("車両の状態", age_options, index=1, key="s_age")
        s_p = st.number_input("購入価格 (円)", value=3500000 if "新車" in s_age else 1800000, step=100000, key="s_p")
        s_m = st.number_input("実用燃費 (km/L)", value=20.0 if "新車" in s_age else 15.0, step=1.0, key="s_m")
        s_tire_size = st.selectbox("タイヤサイズ", ["15インチ以下", "16〜17インチ", "18インチ以上"], index=1)
        if "15" in s_tire_size: s_t_unit, s_w_price, s_c_fee = 40000, 40000, 8000
        elif "16" in s_tire_size: s_t_unit, s_w_price, s_c_fee = 80000, 60000, 10000
        else: s_t_unit, s_w_price, s_c_fee = 120000, 80000, 12000
        s_total, s_resale, s_dep, s_fuel, s_tax, s_shaken, s_ins, s_tire = calc_all(s_p, s_m, False, s_age, is_resale_included, s_t_unit, s_w_price, s_c_fee)
        if is_resale_included: st.info(f"💡 予想売却価格: **{s_resale:,}円**")

# --- 4. 結果表示 ---
st.divider()
st.markdown("<h3 style='font-size: 1.1rem; margin-bottom: 0.5rem;'>📊 算出結果<br>（トータルコスト）</h3>", unsafe_allow_html=True)
res_c1, res_c2 = st.columns(2)
with res_c1:
    st.metric("軽自動車 合計", f"{k_total:,}円")
    with st.expander("🔍 内訳"):
        st.write(f"- 車両実質負担: {k_dep:,}円\n- ガソリン代: {k_fuel:,}円\n- 自動車税等: {k_tax:,}円\n- 車検代: {k_shaken:,}円\n- 任意保険: {k_ins:,}円\n- メンテ・タイヤ: {k_tire:,}円")
with res_c2:
    st.metric("普通車 合計", f"{s_total:,}円")
    with st.expander("🔍 内訳"):
        st.write(f"- 車両実質負担: {s_dep:,}円\n- ガソリン代: {s_fuel:,}円\n- 自動車税等: {s_tax:,}円\n- 車検代: {s_shaken:,}円\n- 任意保険: {s_ins:,}円\n- メンテ・タイヤ: {s_tire:,}円")

diff = s_total - k_total
if diff > 0: st.warning(f"普通車の方が **{diff:,}円** 高くなります。")
elif diff < 0: st.success(f"軽自動車の方が **{abs(diff):,}円** 高くなります。")

# --- 5. 賢者の計算根拠 ---
with st.expander("🧮 賢者の計算根拠・物理法則と市場ファクト"):
    st.markdown("<h3 style='font-size: 1.1rem; margin-top: 0px;'>1. 将来の予想売却価格（残価率）の算定基準</h3>", unsafe_allow_html=True)
    st.write("ネクステージ等の市場データに基づき、一般的な値落ち推移を設定。軽自動車の需要の高さや、中古車購入時の目減りの少なさを反映しています。")
    st.table({"保有期間": ["3年", "5年", "7年", "10年"], "軽(新車)": ["65%", "50%", "30%", "10%"], "軽(中古)": ["55%", "45%", "25%", "5%"], "普通(新車)": ["55%", "40%", "20%", "5%"], "普通(中古)": ["55%", "45%", "25%", "5%"]})
    
    st.markdown("<h3 style='font-size: 1.1rem;'>2. 基本維持費の計算式と単価設定</h3>", unsafe_allow_html=True)
    resale_text = "（購入価格 － 保有期間後の予想売却価格）" if is_resale_included else "（購入価格のみ ※売却なし）"
    st.markdown(f"""
    * **車両実質負担額**: {resale_text} をベースに計算。新車・中古の選択により残価率が異なります。
    * **燃料代**: 走行距離 ÷ 実用燃費 × ガソリン単価（{gas}円）で算出。
    * **自動車税**: 軽自動車 10,800円/年、普通車 30,500円/年（1.5L以下を想定）。
    * **車検代**: 2年に1回（軽: 6万、普通: 10万）と仮定。
    * **任意保険**: プランに応じた料率を購入価格に乗じ、基本料を加算。
    * **タイヤ関連費（消耗＋スタッドレス導入費＋毎年の履き替え工賃）**:
      * **軽自動車**: タイヤ約3.5万 / ホイール約2万 / 工賃年0.6万
      * **普通 15インチ以下**: タイヤ約4万 / ホイール約4万 / 工賃年0.8万
      * **普通 16〜17インチ**: タイヤ約8万 / ホイール約6万 / 工賃年1.0万
      * **普通 18インチ以上**: タイヤ約12万 / ホイール約8万 / 工賃年1.2万
    """)

    st.markdown("<h3 style='font-size: 1.1rem;'>3. 機械的負荷・物理法則による補正</h3>", unsafe_allow_html=True)
    st.markdown("""
    * **高回転による金属疲労**: 660ccの軽自動車は巡航時のエンジン回転数が普通車の1.5〜2倍になります。摩擦回数が多いことによるオイル劣化や駆動系の摩耗を考慮し、整備費を補正しています。
    * **高速道路利用の影響**: 軽自動車は高速走行時の負荷が顕著なため、利用頻度に応じてメンテナンス係数を動的に加算しています。
    """)
    
    st.markdown("<h3 style='font-size: 1.1rem;'>4. 13年超え重課税と10万kmメンテナンスの壁</h3>", unsafe_allow_html=True)
    st.markdown("""
    * **13年超えの重課税**: 新車登録から13年を経過すると、自動車税が約15%、重量税が約40%増税されます。高年式車におけるこの増税分を自動算出しています。
    * **10万km目前の大物パーツ整備**: 累計10万km到達時に発生する「タイミングベルト、ウォーターポンプ、足回り」等の交換費用（軽:10万、普通:12万）を特別整備費として算入しています。
    """)
