import streamlit as st

# ページ設定：中央寄せにするため layout="wide" は使いません
st.set_page_config(page_title="賢者の車選びシミュレーター", page_icon="🚗")

# カスタムCSS：画面中央に寄せて、見た目を整える
st.markdown("""
    <style>
    .block-container { max-width: 800px; padding-top: 2rem; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #e9ecef; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 賢者の車選びシミュレーター")
st.write("「軽自動車」と「普通車」の維持費をリアルに比較。")

# --- 1. 基本条件 ---
with st.container(border=True):
    st.subheader("🗓️ シミュレーションの基本条件")
    years = st.slider("保有予定期間 (年)", 3, 10, 5)
    dist = st.number_input("年間走行距離 (km)", value=10000, step=1000)
    is_winter = st.toggle("スタッドレスタイヤを使用", value=True)
    w_months = st.slider("冬タイヤ装着期間 (ヶ月)", 1, 6, 3) if is_winter else 0

# サイドバー
gas = st.sidebar.slider("ガソリン単価 (円/L)", 150, 200, 175)
ins_type = st.sidebar.radio("保険プラン", ["基本", "安心", "万全"], index=1)

# --- 計算ロジック ---
def get_resale(p, y, is_new):
    r = {3:0.6, 5:0.4, 7:0.2, 10:0.05} if is_new else {3:0.45, 5:0.25, 7:0.15, 10:0.03}
    return p * r.get(y, 0.1)

def calc_all(price, mpg, is_kei, is_new):
    dep = price - get_resale(price, years, is_new)
    fuel = (dist * years / mpg) * gas
    tax = (10800 if is_kei else 30500) * years
    shaken = (years // 2) * (60000 if is_kei else 100000)
    ins = (35000 if is_kei else 45000) * years + (price * 0.02 * years if ins_type != "基本" else 0)
    # タイヤ代
    t_unit = 35000 if is_kei else 80000
    tire = (int(dist*years*0.7/30000)*t_unit) + ((t_unit+40000+8000*years) if is_winter else 0)
    return dep + fuel + tax + shaken + ins + tire

# --- 2. 車両入力 ---
st.header("🚘 比較する車両の入力")
with st.container(border=True):
    st.subheader("【A】軽自動車")
    k_p = st.number_input("購入価格 (円)", value=2000000, step=100000, key="k_p")
    k_m = st.number_input("実用燃費 (km/L)", value=20.0, step=1.0, key="k_m")
    k_total = calc_all(k_p, k_m, True, True)

with st.container(border=True):
    st.subheader("【B】普通車（中古）")
    s_p = st.number_input("購入価格 (円)", value=3000000, step=100000, key="s_p")
    s_m = st.number_input("実用燃費 (km/L)", value=15.0, step=1.0, key="s_m")
    s_total = calc_all(s_p, s_m, False, False)

# --- 3. 結果発表 ---
st.divider()
st.header("📊 算出結果")
c1, c2 = st.columns(2)
c1.metric("軽自動車 合計", f"{int(k_total/10000):,}万円")
c2.metric("普通車 合計", f"{int(s_total/10000):,}万円")

diff = s_total - k_total
if diff > 0:
    st.error(f"普通車の方が **{int(diff/10000):,}万円** 高くなります。")
else:
    st.success(f"普通車の方が **{int(abs(diff)/10000):,}万円** お得です！")
