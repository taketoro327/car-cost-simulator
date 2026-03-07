import streamlit as st

# ページ構成の設定
st.set_page_config(page_title="賢者の車選びシミュレーター", layout="wide")

st.title("🚗 賢者の車選びシミュレーター：徹底比較版")
st.write("検討中の「軽自動車」と「普通車」の情報を入力し、数年後の損得を可視化します。")

# --- 1. 基本条件の設定 ---
st.header("1. 基本条件の設定")
col_base1, col_base2, col_base3 = st.columns(3)
with col_base1:
    years = st.slider("保有予定期間 (年)", 3, 10, 5, help="3年〜10年で1年刻みのシミュレーションが可能です。")
with col_base2:
    dist_annual = st.number_input("年間走行距離 (km)", min_value=1000, value=10000, step=1000)
with col_base3:
    is_winter_tire = st.checkbox("降雪地域での利用（スタッドレスを利用する）", value=True)
    if is_winter_tire:
        winter_months = st.slider("1年のうち、冬タイヤを装着する期間", 1, 6, 3, format="%dヶ月")
    else:
        winter_months = 0

# サイドバー設定
st.sidebar.header("共通設定")
gas_price = st.sidebar.slider("ガソリン単価 (円/L)", 150, 200, 175)

st.sidebar.subheader("🛡️ 自動車保険の設定")
insurance_plan = st.sidebar.radio("保険プランの選択", 
                                ["基本（対人対物のみ）", "安心（車両保険エコノミー付）", "万全（車両保険一般付）"],
                                help="30歳以上・11等級程度の標準的な概算です。車両価格に応じて保険料が変動します。")

# --- 内部計算用ロジック ---
def get_resale_price(price, years, is_new):
    if is_new:
        rates = {3: 0.60, 4: 0.50, 5: 0.40, 6: 0.30, 7: 0.20, 8: 0.15, 9: 0.10, 10: 0.05}
    else:
        rates = {3: 0.45, 4: 0.35, 5: 0.25, 6: 0.20, 7: 0.15, 8: 0.10, 9: 0.05, 10: 0.03}
    return price * rates.get(years, 0.05)

def calculate_insurance(price, plan, is_kei):
    base = 35000 if is_kei else 45000
    if plan == "基本（対人対物のみ）":
        return base
    elif plan == "安心（車両保険エコノミー付）":
        return base + (price * 0.015)
    else:
        return base + (price * 0.025)

def calculate_tire_cost(years, dist_annual, is_winter_tire, winter_months, unit_price, wheel_price):
    winter_ratio = winter_months / 12.0
    summer_ratio = 1.0 - winter_ratio
    
    total_summer_dist = dist_annual * years * summer_ratio
    total_winter_dist = dist_annual * years * winter_ratio
    
    # 夏タイヤの買い替え回数（3万km寿命）
    summer_repurchase = int(max(0, total_summer_dist - 1) / 30000)
    summer_cost = summer_repurchase * unit_price
    
    if is_winter_tire:
        # 冬タイヤの買い替え回数（4年または3万km）
        time_repurchase = (years - 1) // 4
        dist_repurchase = int(max(0, total_winter_dist - 1) / 30000)
        winter_repurchase_count = max(time_repurchase, dist_repurchase)
        
        # 初回（ゴム＋ホイール）＋ 2回目以降（ゴムのみ）
        winter_cost = (unit_price + wheel_price) + (unit_price * winter_repurchase_count)
        # 年2回の履き替え（脱着）工賃（年間8,000円）
        swap_cost = 8000 * years
    else:
        winter_cost = 0
        swap_cost = 0
        
    return summer_cost + winter_cost + swap_cost

# --- 2. 車両情報の入力 ---
st.header("2. 車両情報の詳細入力")
col_kei, col_std = st.columns(2)

# 【A】軽自動車セクション
with col_kei:
    st.subheader("【A】軽自動車の設定")
    kei_model = st.selectbox("モデル世代（燃費目安）", 
                          ["現行モデル：走行少ない（約22km/L）", "先代モデル：走行3〜5万km（約20km/L）", 
                           "2世代前：走行7万km以上（約17km/L）", "それ以前：低価格重視（約14km/L）"])
    kei_mpg_map = {"現行モデル：走行少ない（約22km/L）": 22.0, "先代モデル：走行3〜5万km（約20km/L）": 20.0, 
                   "2世代前：走行7万km以上（約17km/L）": 17.0, "それ以前：低価格重視（約14km/L）": 14.0}
    kei_mpg = kei_mpg_map[kei_model]
    is_kei_new = True if "現行モデル" in kei_model else False
    kei_price = st.number_input("車両購入価格 (円) (A)", min_value=0, value=2000000 if is_kei_new else 1000000, step=50000)
    
    # 計算
    kei_resale = get_resale_price(kei_price, years, is_kei_new)
    kei_depreciation = kei_price - kei_resale
    kei_fuel = (dist_annual * years / kei_mpg) * gas_price
    kei_tax = 10800 * years
    shaken_count = sum(1 for y in [3, 5, 7, 9] if years >= y)
    kei_shaken = shaken_count * 60000
    kei_insurance = calculate_insurance(kei_price, insurance_plan, True) * years
    kei_tire = calculate_tire_cost(years, dist_annual, is_winter_tire, winter_months, 35000, 20000)
    
    total_kei = kei_depreciation + kei_fuel + kei_tax + kei_shaken + kei_insurance + kei_tire

# 【B】普通車セクション
with col_std:
    st.subheader("【B】普通車（中古）の設定")
    std_price = st.number_input("車両購入価格 (円) (B)", min_value=0, value=3000000, step=50000)
    std_mpg = st.slider("想定の実用燃費 (km/L) (B)", 5.0, 35.0, 22.0, step=0.5)
    std_tire_size = st.selectbox("タイヤサイズ (B)", ["15インチ（コンパクト等）", "17インチ（セダン・ミニバン等）", "19インチ（SUV・高級車等）"], index=2)
    
    if "15" in std_tire_size:
        std_tax_annual, std_tire_unit, std_wheel_unit = 25000, 50000, 30000
    elif "17" in std_tire_size:
        std_tax_annual, std_tire_unit, std_wheel_unit = 30500, 80000, 40000
    else:
        std_tax_annual, std_tire_unit, std_wheel_unit = 39500, 120000, 60000
        
    # 計算
    std_resale = get_resale_price(std_price, years, False)
    std_depreciation = std_price - std_resale
    std_fuel = (dist_annual * years / std_mpg) * gas_price
    std_tax = std_tax_annual * years
    std_shaken = shaken_count * 100000
    std_insurance = calculate_insurance(std_price, insurance_plan, False) * years
    std_tire = calculate_tire_cost(years, dist_annual, is_winter_tire, winter_months, std_tire_unit, std_wheel_unit)
    
    total_std = std_depreciation + std_fuel + std_tax + std_shaken + std_insurance + std_tire

# --- 3. 比較結果サマリー ---
st.markdown("---")
st.header(f"3. {years}年間のコスト比較結果")

diff = total_std - total_kei
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.metric("【A】軽自動車 総額", f"{int(total_kei/10000):,} 万円")
    with st.expander("🔍 維持費の内訳を確認"):
        st.write(f"📉 実質車両コスト: {int(kei_depreciation/10000):,} 万円")
        st.write(f"⛽ 燃料代（{years}年）: {int(kei_fuel/10000):,} 万円")
        st.write(f"📜 自動車税（計）: {int(kei_tax/10000):,} 万円")
        st.write(f"🛠️ 車検費用（{shaken_count}回）: {int(kei_shaken/10000):,} 万円")
        st.write(f"🛡️ 自動車保険（{years}年）: {int(kei_insurance/10000):,} 万円")
        st.write(f"🛞 タイヤ関連費（購入・脱着）: {int(kei_tire/10000):,} 万円")

with res_col2:
    st.metric("【B】普通車 総額", f"{int(total_std/10000):,} 万円")
    with st.expander("🔍 維持費の内訳を確認"):
        st.write(f"📉 実質車両コスト: {int(std_depreciation/10000):,} 万円")
        st.write(f"⛽ 燃料代（{years}年）: {int(std_fuel/10000):,} 万円")
        st.write(f"📜 自動車税（計）: {int(std_tax/10000):,} 万円")
        st.write(f"🛠️ 車検費用（{shaken_count}回）: {int(std_shaken/10000):,} 万円")
        st.write(f"🛡️ 自動車保険（{years}年）: {int(std_insurance/10000):,} 万円")
        st.write(f"🛞 タイヤ関連費（購入・脱着）: {int(std_tire/10000):,} 万円")

st.markdown("---")
if diff > 0:
    st.error(f"⚠️ 普通車の方が **{int(diff/10000):,} 万円** 高コストです。")
    st.write(f"💡 普通車が **あと {int(diff):,} 円 安ければ**、軽自動車とトータルコストが並びます。")
else:
    st.success(f"✅ 普通車の方が **{int(abs(diff)/10000):,} 万円** 低コストです！")

# --- 4. 判定アドバイス ---
st.subheader("💡 賢者の判定アドバイス")
advice = ""
if abs(diff) < 300000:
    advice = "**【性能とコストの好バランス】** 差額が僅かです。この程度の差であれば、普通車の安全性や静粛性を優先する選択は非常に投資対効果が高いと言えます。"
elif diff > 1000000:
    advice = "**【徹底した経済性重視】** 軽自動車のコストメリットが圧倒的です。固定費を最小化し、余剰資金を他の生活資本に充てるのが最も合理的な判断です。"
elif is_winter_tire and "19" in std_tire_size:
    advice = "**【足回りコストへの注意】** 大径タイヤの維持費（ホイール代・買い替え費用）が全体のコストを押し上げています。インチダウンを検討することで経済性を改善できます。"
elif years == 3:
    advice = "**【資産価値を維持する戦略】** 3年での乗り換えは、高値売却により実質負担を抑えつつ、常に最新の安全機能を享受できる効率の良いサイクルです。"
else:
    advice = "このシミュレーション結果を参考に、ご自身のライフスタイルに最適な一台を選択してください。"
st.info(advice)

# --- 5. 算出根拠・前提条件 ---
st.markdown("---")
with st.expander("📊 当シミュレーターの算出根拠・前提条件"):
    st.markdown("""
    本シミュレーターは、以下の一般的な基準および独自の計算式に基づいて各維持費を算出しています。実際の金額は、ご契約の店舗や個人の利用状況により変動するため、あくまで目安としてご活用ください。

    **1. タイヤの消耗と買い替え判定**
    * **夏タイヤの寿命：** 走行距離 **30,000km** ごとに買い替え。
    * **冬タイヤの寿命：** 走行距離 **30,000km**、またはゴムの経年劣化による **4年経過** のどちらか早いタイミングで買い替え。
    * **タイヤ購入費用（ゴムのみ1回分目安）：** 軽自動車 3.5万円、普通車15インチ 5万円、17インチ 8万円、19インチ 12万円。
    * **冬用ホイール代（初回のみ加算）：** 軽自動車 2万円、普通車15インチ 3万円、17インチ 4万円、19インチ 6万円。
    * **履き替え工賃：** 冬タイヤありの場合、年2回（春・冬）のホイール脱着費用として **年間8,000円** を加算。

    **2. 車両の残価（リセールバリュー）**
    * **新車：** 3年後60%〜10年後5%で下落と仮定。
    * **中古車：** 3年後45%〜10年後3%で下落と仮定。

    **3. 自動車税・車検費用**
    * **自動車税：** 軽自動車 10,800円/年。普通車はタイヤサイズを排気量の目安とし算出（15インチ=2.5万円、17インチ=3.0万円、19インチ=3.9万円）。
    * **車検費用：** 軽自動車 6万円/回、普通車 10万円/回として計上。

    **4. 自動車保険料**
    「30歳以上・11等級程度」を想定。プランに応じて基本料金に車両購入価格の 1.5%〜2.5% を車両保険料として加算。
    """)