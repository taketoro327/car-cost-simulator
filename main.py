import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import re
import time  # アクセスカウンターのキャッシュ対策用

# ページ設定
st.set_page_config(page_title="賢者の車選びシミュレーター", page_icon="🚗")

# --- 画像を丸く処理する関数（キャッシュ＆例外処理強化） ---
@st.cache_data
def get_image_base64(img_path, crop_circle=True):
    try:
        img = Image.open(img_path).convert("RGBA")
        
        if crop_circle:
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
    
    except FileNotFoundError:
        print(f"【警告】画像ファイルが見つかりません: {img_path}")
        return None
    except Exception as e:
        print(f"【エラー】画像処理中に問題が発生しました ({img_path}): {e}")
        return None

# 画像の読み込み
icon_base64 = get_image_base64("賢者アイコン用.png", crop_circle=True)
sub_icon_base64 = get_image_base64("チャンネル登録アイコン.png", crop_circle=False) 

# デザイン設定
st.markdown("""
    <style>
    .block-container { max-width: 800px; padding-top: 100px; } 
    .stMetric { background-color: rgba(128, 128, 128, 0.1); padding: 15px; border-radius: 10px; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; }
    .streamlit-expanderContent { font-size: 0.85rem; line-height: 1.6; }
    div[role="radiogroup"] label p { font-size: 0.85rem !important; }
    h1 { font-size: 1.1rem !important; font-weight: bold; }
    
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 1.0rem; }
    .header-icon { width: 65px; height: 65px; border-radius: 50%; object-fit: cover; border: 2px solid #ff4b4b; }
    .header-text { display: flex; flex-direction: column; justify-content: center; }
    .header-title { font-size: 1.1rem !important; font-weight: bold; margin: 0; line-height: 1.2; }
    .youtube-link-area { display: flex; align-items: center; gap: 10px; margin-top: 5px; }
    .youtube-link { font-size: 0.85rem; color: #ff4b4b; text-decoration: none; font-weight: bold; }
    .sub-btn-img { height: 41px; border-radius: 4px; transition: transform 0.2s; }
    .sub-btn-img:hover { transform: scale(1.05); }

    @media (max-width: 768px) {
        .block-container { padding-top: 60px; } 
        [data-testid="stMetricValue"] { font-size: 1.5rem !important; } 
        .header-box { gap: 10px; }
        .header-icon { width: 55px; height: 55px; } 
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP：アイコン・タイトル・YouTubeリンク ---
channel_url = "https://www.youtube.com/channel/UCAaiMudxwrWJ8aob8j2nr3w"
sub_url = f"{channel_url}?sub_confirmation=1" 

if sub_icon_base64:
    sub_html = f'<a href="{sub_url}" target="_blank"><img src="data:image/png;base64,{sub_icon_base64}" class="sub-btn-img" alt="チャンネル登録"></a>'
else:
    sub_html = f'<a href="{sub_url}" target="_blank" style="font-size: 0.8rem; background-color: #ff0000; color: white; padding: 2px 8px; border-radius: 4px; text-decoration: none;">登録</a>'

if icon_base64:
    header_html = f"""
    <div class="header-box">
        <img src="data:image/png;base64,{icon_base64}" class="header-icon">
        <div class="header-text">
            <div class="header-title">🚗 賢者の車選びシミュレーター</div>
            <div class="youtube-link-area">
                <a href="{channel_url}" target="_blank" class="youtube-link">▶ YouTube 賢者の回顧録</a>
                {sub_html}
            </div>
        </div>
    </div>
    """
else:
    header_html = f"""
    <h1 style="font-size: 1.1rem;">🚗 賢者の車選びシミュレーター</h1>
    <div class="youtube-link-area">
        <a href="{channel_url}" target="_blank" class="youtube-link">▶ YouTube 賢者の回顧録</a>
        {sub_html}
    </div>
    """

st.markdown(header_html, unsafe_allow_html=True)
st.write("「軽自動車」と「普通車」の購入費・維持費・リセールを、物理法則と市場データに基づきリアルに比較。")

# 【修正】PV重視のアクセスカウンター（リロードのたびにカウント、左が今日・右が累計）
st.markdown(
    f"![PV Counter](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=kenja-car-simulator-v12&count_bg=%23FF4B4B&title_bg=%23555555&title=PV&edge_flat=true&t={int(time.time())})"
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
    st.markdown("<h4 style='font-size: 1.0rem;'>🛡️ 任意保険の基本設定（ネット型ベース）</h4>", unsafe_allow_html=True)
    driver_grade = st.radio(
        "現在の運転者の等級レベル（目安）",
        options=["新規・若年層（6等級前後）", "平均的なドライバー（10〜14等級程度）", "優良・ベテラン（20等級）"],
        index=1, horizontal=True,
        help="等級に応じてベースとなる保険料金が変動します（新規は約1.8倍、優良は約半額）。"
    )

    st.divider()
    col_tire1, col_tire2 = st.columns(2)
    with col_tire1:
        is_winter = st.toggle("スタッドレスタイヤを使用", value=True)
    with col_tire2:
        w_months = st.selectbox("冬タイヤ装着期間 (ヶ月)", options=[1, 2, 3, 4, 5, 6], index=2) if is_winter else 0

# --- 2. 計算ロジック（マスター下落曲線） ---

def get_master_value(age, is_kei):
    # 新車時を100%(1.0)とした絶対価値の推移
    if is_kei:
        curve = [1.0, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.05, 0.0]
        idx = min(age, 10)
    else:
        curve = [1.0, 0.75, 0.65, 0.55, 0.46, 0.38, 0.30, 0.24, 0.18, 0.14, 0.10, 0.08, 0.06, 0.05]
        idx = min(age, 13)
    return curve[idx]

def get_resale_rate(start_age, keep_years, is_kei):
    end_age = start_age + keep_years
    start_val = get_master_value(start_age, is_kei)
    end_val = get_master_value(end_age, is_kei)
    
    if start_val <= 0:
        return 0.0
    return end_val / start_val

def parse_age_label(age_label):
    if "新車" in age_label:
        return 0
    elif "10年落ち〜" in age_label:
        return 10
    else:
        match = re.search(r'\d+', age_label)
        return int(match.group()) if match else 5

def calc_all(price, mpg, is_kei, age_label, is_resale_included, t_unit, w_price, change_fee, d_grade, i_plan):
    start_age = parse_age_label(age_label)
    resale_rate = get_resale_rate(start_age, years, is_kei)
    resale_val = int(price * resale_rate)
    actual_dep = (price - resale_val) if is_resale_included else price
    
    fuel = (dist * years / mpg) * gas
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
    if "新規" in d_grade: grade_factor = 1.8
    elif "優良" in d_grade: grade_factor = 0.5
    else: grade_factor = 1.0
    
    adjusted_base_ins = base_ins * grade_factor
    
    if "万全" in i_plan: ins_rate = 0.025
    elif "安心" in i_plan: ins_rate = 0.015
    else: ins_rate = 0.0
    
    ins_total = int((adjusted_base_ins + (price * ins_rate)) * years)
    
    highway_factor = 1.0
    if is_kei:
        if highway_freq == "週1回以上（頻繁）": highway_factor = 1.4
        elif highway_freq == "月1〜2回程度": highway_factor = 1.2
    
    basic_maint = (15000 * years) * highway_factor
    total_mileage = (start_age * 10000) + (dist * years)
    extra_maint = 100000 if (is_kei and total_mileage >= 100000) else (120000 if total_mileage >= 100000 else 0)
    
    summer_ratio = (12 - w_months) / 12.0 if is_winter else 1.0
    tire_usage = (int(dist * years * summer_ratio / 30000) * t_unit) 
    winter_cost = ((t_unit + w_price + (change_fee * years)) if is_winter else 0)
    
    maint_total = tire_usage + winter_cost + basic_maint + extra_maint
    total = int(actual_dep + fuel + total_tax + shaken_total + ins_total + maint_total)
    
    return total, resale_val, int(actual_dep), int(fuel), int(total_tax), int(shaken_total), ins_total, int(maint_total)

# --- 3. 車両比較入力 ---
st.markdown("<h3 style='font-size: 1.1rem; margin-bottom: 0.5rem;'>🚘 比較する車両の入力</h3>", unsafe_allow_html=True)

resale_help = "【出典：中古車市場相場データ】車両の年式と保有期間から、シビアな値落ち推移を設定。"
is_resale_included = st.toggle("保有期間後の予想売却価格を計算に含める", value=True, help=resale_help)

col_v1, col_v2 = st.columns(2)
age_options = ["新車（最新モデル）"] + [f"中古（{i}年落ち）" for i in range(1, 10)] + ["中古（10年落ち〜）"]
ins_plan_options = ["基本（車両なし）", "安心（＋車両エコノミー）", "万全（＋車両一般）"]

with col_v1:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 1.1rem;'>【A】軽自動車</h4>", unsafe_allow_html=True)
        k_age = st.selectbox("車両の状態", age_options, key="k_age")
        k_p = st.number_input("購入価格 (円)", value=2000000 if "新車" in k_age else 1000000, step=100000, key="k_p")
        k_m = st.number_input("実用燃費 (km/L)", value=22.0 if "新車" in k_age else 18.0, step=1.0, key="k_m")
        k_ins = st.selectbox("車両保険プラン", ins_plan_options, index=2 if "新車" in k_age else 0, key="k_ins_plan")
        
        k_total, k_resale, k_dep, k_fuel, k_tax, k_shaken, k_ins_cost, k_tire = calc_all(k_p, k_m, True, k_age, is_resale_included, 35000, 20000, 6000, driver_grade, k_ins)
        if is_resale_included: st.info(f"💡 予想売却価格: **{k_resale:,}円**")

with col_v2:
    with st.container(border=True):
        st.markdown("<h4 style='font-size: 1.1rem;'>【B】普通車</h4>", unsafe_allow_html=True)
        s_age = st.selectbox("車両の状態", age_options, index=5, key="s_age")
        s_p = st.number_input("購入価格 (円)", value=3500000 if "新車" in s_age else 1800000, step=100000, key="s_p")
        s_m = st.number_input("実用燃費 (km/L)", value=20.0 if "新車" in s_age else 15.0, step=1.0, key="s_m")
        s_tire_size = st.selectbox("タイヤサイズ", ["15インチ以下", "16〜17インチ", "18インチ以上"], index=1)
        s_ins = st.selectbox("車両保険プラン", ins_plan_options, index=2 if "新車" in s_age else 0, key="s_ins_plan")
        
        if "15" in s_tire_size: s_t_unit, s_w_price, s_c_fee = 40000, 40000, 8000
        elif "16" in s_tire_size: s_t_unit, s_w_price, s_c_fee = 80000, 60000, 10000
        else: s_t_unit, s_w_price, s_c_fee = 120000, 80000, 12000
        
        s_total, s_resale, s_dep, s_fuel, s_tax, s_shaken, s_ins_cost, s_tire = calc_all(s_p, s_m, False, s_age, is_resale_included, s_t_unit, s_w_price, s_c_fee, driver_grade, s_ins)
        if is_resale_included: st.info(f"💡 予想売却価格: **{s_resale:,}円**")

# --- 4. 結果表示 ---
st.divider()
st.markdown("<h3 style='font-size: 1.1rem; margin-bottom: 0.5rem;'>📊 算出結果<br>（トータルコスト）</h3>", unsafe_allow_html=True)
res_c1, res_c2 = st.columns(2)
with res_c1:
    st.metric("軽自動車 合計", f"{k_total:,}円")
    with st.expander("🔍 内訳", expanded=False):
        st.write(f"- 車両実質負担: {k_dep:,}円\n- ガソリン代: {k_fuel:,}円\n- 自動車税等: {k_tax:,}円\n- 車検代: {k_shaken:,}円\n- 任意保険: {k_ins_cost:,}円\n- メンテ・タイヤ: {k_tire:,}円")
with res_c2:
    st.metric("普通車 合計", f"{s_total:,}円")
    with st.expander("🔍 内訳", expanded=False):
        st.write(f"- 車両実質負担: {s_dep:,}円\n- ガソリン代: {s_fuel:,}円\n- 自動車税等: {s_tax:,}円\n- 車検代: {s_shaken:,}円\n- 任意保険: {s_ins_cost:,}円\n- メンテ・タイヤ: {s_tire:,}円")

diff = s_total - k_total
if diff > 0: st.warning(f"普通車の方が **{diff:,}円** 高くなります。")
elif diff < 0: st.success(f"軽自動車の方が **{abs(diff):,}円** 高くなります。")

# --- 5. 賢者の計算根拠 ---
with st.expander("🧮 賢者の計算根拠・物理法則と市場ファクト", expanded=False):
    st.markdown("<h3 style='font-size: 1.1rem; margin-top: 0px;'>1. 忖度なしの「マスター下落曲線」による残価率算出</h3>", unsafe_allow_html=True)
    st.markdown("""
    当シミュレーターでは、大雑把な値引き計算ではなく、新車時を100%とした「年式ごとの絶対的な価値（マスター曲線）」を裏側に持たせ、**【売却時の価値 ÷ 購入時の価値】**というプロの査定士と同じ数学的ロジックでリセールを算出しています。
    * **軽自動車の残酷な現実**: 新車〜5年落ちまでは需要が高く価値が落ちにくいですが、耐久性の懸念から**10年・10万km目前で市場価値が「0%」**になるよう設定。5年落ちを買って5年乗ればリセールは0円です。
    * **普通車の底値の強さ**: 新車時の値落ちは激しいですが、海外輸出需要などがあるため、10年落ちでも「10%」、それ以降も「5%」の底値がしぶとく残るリアルな市場ファクトを反映しています。
    """)
    
    st.markdown("<h3 style='font-size: 1.1rem;'>2. 基本維持費の計算式と単価設定</h3>", unsafe_allow_html=True)
    resale_text = "（購入価格 － 保有期間後の予想売却価格）" if is_resale_included else "（購入価格のみ ※売却なし）"
    st.markdown(f"""
    * **車両実質負担額**: {resale_text} をベースに計算。新車・中古の選択や年式により残価率が異なります。
    * **燃料代**: 走行距離 ÷ 実用燃費 × ガソリン単価（{gas}円）で算出。
    * **自動車税**: 軽自動車 10,800円/年、普通車 30,500円/年（1.5L以下を想定）。
    * **車検代**: 2年に1回（軽: 6万、普通: 10万）と仮定。
    * **基本メンテナンス代**: エンジンオイルや消耗品代として「年間15,000円」をベースに設定しています。
    * **夏タイヤの消耗・買い替え**: 走行距離「累計30,000kmごと」に新品への交換費用（タイヤ4本分）が発生するよう計算。冬タイヤの装着期間に応じて、夏タイヤの摩耗割合も自動で減算調整されます。
    * **冬タイヤ関連費（スタッドレス導入＋毎年の履き替え工賃）**:
      * **軽自動車**: タイヤ約3.5万 / ホイール約2万 / 工賃年0.6万
      * **普通 15インチ以下**: タイヤ約4万 / ホイール約4万 / 工賃年0.8万
      * **普通 16〜17インチ**: タイヤ約8万 / ホイール約6万 / 工賃年1.0万
      * **普通 18インチ以上**: タイヤ約12万 / ホイール約8万 / 工賃年1.2万
    """)

    st.markdown("<h3 style='font-size: 1.1rem;'>3. 機械的負荷・物理法則による補正</h3>", unsafe_allow_html=True)
    st.markdown("""
    * **高回転による金属疲労**: 660ccの軽自動車は巡航時のエンジン回転数が普通車の1.5〜2倍になります。摩擦回数が多いことによるオイル劣化や駆動系の摩耗を考慮し、整備費（基本メンテナンス代）を補正しています。
    * **高速道路利用の影響**: 軽自動車は高速走行時の負荷が顕著なため、利用頻度に応じてメンテナンス係数を動的に加算（最大1.4倍）しています。
    """)
    
    st.markdown("<h3 style='font-size: 1.1rem;'>4. 13年超え重課税と10万kmメンテナンスの壁</h3>", unsafe_allow_html=True)
    st.markdown("""
    * **13年超えの重課税**: 新車登録から13年を経過すると、自動車税が約15%、重量税が約40%増税されます。高年式車におけるこの増税分を自動算出しています。
    * **10万km目前の大物パーツ整備**: 累計10万km到達時に発生する「タイミングベルト、ウォーターポンプ、足回り」等の交換費用（軽:10万、普通:12万）を特別整備費として算入しています。
    """)

    st.markdown("<h3 style='font-size: 1.1rem;'>5. 任意保険のリアルな算出ロジック</h3>", unsafe_allow_html=True)
    st.markdown("""
    大手ネット型自動車保険の相場を基準に、個人の状況と購入プランに合わせた実戦的な金額を算出します。
    * **運転者の等級レベル**: 事故歴や年齢によるベース保険料の差を、3段階の係数（新規・若年 約1.8倍 / 平均 1.0倍 / 優良・20等級 約0.5倍）で反映しています。
    * **車両保険（車両ごとの個別設定）**: 購入する車の価格に対して、プランごとの料率（なし 0% / エコノミー 約1.5% / 一般 約2.5%）を上乗せ。「新車は手厚く、乗り潰す中古車は車両保険なし」といった、実際の購入心理に沿った比較が可能です。
    """)
