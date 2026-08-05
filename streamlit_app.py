import streamlit as st

st.set_page_config(page_title="突破を防げるか！多要素認証ゲーム", page_icon="🔐", layout="wide")

# ---------------------------------------------------------
# データ定義
# ---------------------------------------------------------
METHODS = {
    "パスワード": {"factor": "知識要素", "security": 20, "convenience": 90, "icon": "🔑"},
    "PIN": {"factor": "知識要素", "security": 15, "convenience": 95, "icon": "🔢"},
    "秘密の質問": {"factor": "知識要素", "security": 10, "convenience": 85, "icon": "❓"},
    "スマホSMS認証": {"factor": "所持要素", "security": 25, "convenience": 75, "icon": "📱"},
    "ICカード": {"factor": "所持要素", "security": 30, "convenience": 70, "icon": "💳"},
    "指紋認証": {"factor": "生体要素", "security": 35, "convenience": 80, "icon": "👆"},
    "顔認証": {"factor": "生体要素", "security": 30, "convenience": 85, "icon": "🙂"},
}

FACTOR_DESC = {
    "知識要素": "本人だけが知っている情報（例：パスワード、PIN、秘密の質問）",
    "所持要素": "本人だけが持っている物（例：スマホ、ICカード）",
    "生体要素": "本人の身体的特徴（例：指紋、顔）",
}

# 攻撃手段：どの認証方法を狙うかをひもづける（イラスト代わりの絵文字アイコン付き）
ATTACKS = {
    "フィッシング：パスワード漏洩": {"target": "パスワード", "category": "フィッシング攻撃", "icon": "🎣🔑"},
    "フィッシング：PIN漏洩": {"target": "PIN", "category": "フィッシング攻撃", "icon": "🎣🔢"},
    "フィッシング：秘密の質問の回答漏洩": {"target": "秘密の質問", "category": "フィッシング攻撃", "icon": "🎣❓"},
    "盗難：スマートフォン盗難": {"target": "スマホSMS認証", "category": "盗難攻撃", "icon": "🕵️📱"},
    "盗難：ICカード盗難": {"target": "ICカード", "category": "盗難攻撃", "icon": "🕵️💳"},
    "偽造：指紋偽造": {"target": "指紋認証", "category": "偽造攻撃", "icon": "🧪👆"},
    "偽造：顔認証偽造": {"target": "顔認証", "category": "偽造攻撃", "icon": "🧪🙂"},
}

DIVERSITY_BONUS = {1: 0, 2: 25, 3: 45}

# ---------------------------------------------------------
# セッション状態初期化
# ---------------------------------------------------------
if "selected_methods" not in st.session_state:
    st.session_state.selected_methods = []
if "security_score" not in st.session_state:
    st.session_state.security_score = 0
if "convenience_score" not in st.session_state:
    st.session_state.convenience_score = 0


# ---------------------------------------------------------
# スコア計算
# ---------------------------------------------------------
def calc_scores(selected):
    if not selected:
        return 0, 0
    sec_list = [METHODS[m]["security"] for m in selected]
    conv_list = [METHODS[m]["convenience"] for m in selected]
    factors = set(METHODS[m]["factor"] for m in selected)
    bonus = DIVERSITY_BONUS[len(factors)]
    security = min(round(sum(sec_list) / len(sec_list) + bonus), 100)
    convenience = max(round(sum(conv_list) / len(conv_list) - (len(selected) - 1) * 10), 0)
    return security, convenience


# ---------------------------------------------------------
# タイトル
# ---------------------------------------------------------
st.title("🔐 突破を防げるか！多要素認証ゲーム")
st.caption("高校「情報Ⅰ」向け ― 多要素認証（知識・所持・生体）を体験的に学び、攻撃をブロックしよう")

tab1, tab2, tab3 = st.tabs(
    ["① 認証要素の選択", "② 攻撃シミュレーション", "③ 結果・評価"]
)

# ---------------------------------------------------------
# ① 認証要素の選択フェーズ
# ---------------------------------------------------------
with tab1:
    st.header("① 認証要素の選択")
    st.write(
        "以下の認証方法から、実際に使いたい組み合わせを選んでください（複数選択可）。"
        "それぞれの方法は「知識要素」「所持要素」「生体要素」のいずれかに分類されます。"
    )

    cols = st.columns(3)
    for col, fname in zip(cols, FACTOR_DESC.keys()):
        with col:
            st.markdown(f"**{fname}**")
            st.caption(FACTOR_DESC[fname])

    selected = st.multiselect(
        "使用する認証方法を選択してください",
        options=list(METHODS.keys()),
        default=st.session_state.selected_methods,
        format_func=lambda m: f'{METHODS[m]["icon"]} {m}（{METHODS[m]["factor"]}）',
    )
    st.session_state.selected_methods = selected

    if selected:
        st.subheader("あなたの認証構成")
        used_factors = set()
        for m in selected:
            info = METHODS[m]
            used_factors.add(info["factor"])
            st.write(f'{info["icon"]} **{m}** → 分類：{info["factor"]}')

        security, convenience = calc_scores(selected)
        st.session_state.security_score = security
        st.session_state.convenience_score = convenience

        st.markdown(f"**使用している要素の種類：{len(used_factors)} 種類**（{'・'.join(used_factors)}）")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("セキュリティ強度", f"{security} 点")
            st.progress(security / 100)
        with c2:
            st.metric("利便性スコア", f"{convenience} 点")
            st.progress(convenience / 100)

        if len(used_factors) >= 2:
            st.success("✅ 複数の要素を組み合わせた「多要素認証」になっています！")
        else:
            st.warning("⚠️ 現在は1種類の要素のみです。単一要素認証は、その要素が突破されると即座になりすまされてしまいます。")
    else:
        st.info("認証方法を1つ以上選択してください。")

# ---------------------------------------------------------
# ② 攻撃シミュレーションフェーズ
# ---------------------------------------------------------
with tab2:
    st.header("② 攻撃シミュレーション")

    if not st.session_state.selected_methods:
        st.warning("先に「① 認証要素の選択」で認証方法を選択してください。")
    else:
        student_methods = st.session_state.selected_methods
        factors_used = set(METHODS[m]["factor"] for m in student_methods)

        st.write("あなたの認証構成：", "、".join(student_methods))
        st.write(f"使用している要素：{'・'.join(factors_used)}")

        st.write("攻撃者の手段を選んでください（**最大2つまで**）：")

        categories = ["フィッシング攻撃", "盗難攻撃", "偽造攻撃"]
        for cat in categories:
            st.markdown(f"**{cat}**")
            cat_attacks = [a for a in ATTACKS if ATTACKS[a]["category"] == cat]
            cols = st.columns(len(cat_attacks))
            for col, atk in zip(cols, cat_attacks):
                with col:
                    st.markdown(
                        f'<div style="text-align:center; font-size:42px; line-height:1.2;">{ATTACKS[atk]["icon"]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.checkbox(atk.split("：")[1], key=f"atk_{atk}")

        selected_attacks = [a for a in ATTACKS if st.session_state.get(f"atk_{a}")]

        if len(selected_attacks) > 2:
            st.error("攻撃手段は最大2つまでです。チェックを1つ以上外してください。")

        if st.button("攻撃を試す", type="primary", disabled=len(selected_attacks) > 2):
            if not selected_attacks:
                st.info("攻撃手段を1つ以上選択してください。")
            else:
                st.subheader("攻撃結果の内訳")
                compromised_factors = set()
                for atk in selected_attacks:
                    target = ATTACKS[atk]["target"]
                    label = atk.split("：")[1]
                    icon = ATTACKS[atk]["icon"]
                    if target in student_methods:
                        st.write(f"- {icon} {label} → **{target}を使用しているため突破されました**")
                        compromised_factors.add(METHODS[target]["factor"])
                    else:
                        st.write(f"- {icon} {label} → {target}は使用していないため影響なし")

                st.write("---")
                if not compromised_factors:
                    st.success("🛡️ 防御成功！ あなたが使っている要素はどれも突破されませんでした。")
                elif compromised_factors == factors_used:
                    st.error(
                        "💥 攻撃成功（なりすまし成功）！ あなたが使っている要素がすべて突破されたため、"
                        "攻撃者になりすまされてしまいました…"
                    )
                else:
                    remaining = factors_used - compromised_factors
                    st.success(
                        f"🛡️ 防御成功！ 一部の要素（{'・'.join(compromised_factors)}）は突破されましたが、"
                        f"残りの要素（{'・'.join(remaining)}）が本人確認をブロックしました！"
                    )

# ---------------------------------------------------------
# ③ 結果・評価フェーズ
# ---------------------------------------------------------
with tab3:
    st.header("③ 結果・評価")

    if not st.session_state.selected_methods:
        st.warning("先に「① 認証要素の選択」で認証方法を選択してください。")
    else:
        security = st.session_state.security_score
        convenience = st.session_state.convenience_score

        c1, c2 = st.columns(2)
        with c1:
            st.metric("セキュリティ強度", f"{security} 点")
        with c2:
            st.metric("利便性スコア", f"{convenience} 点")

        st.write("---")
        self_eval = st.radio(
            "あなたが選んだ認証構成は、次のどれに近いと思いますか？",
            options=["セキュリティ重視", "利便性重視", "バランス型"],
        )

        if st.button("評価を送信する", type="primary"):
            diff = security - convenience
            if diff > 20:
                actual = "セキュリティ重視"
            elif diff < -20:
                actual = "利便性重視"
            else:
                actual = "バランス型"

            if self_eval == actual:
                st.success(f"🎯 正解！あなたの構成はスコア上も「{actual}」タイプです。自己評価とスコアが一致しています。")
            else:
                st.error(f"🤔 スコアから見ると、あなたの構成は実際には「{actual}」タイプに近いです。")
                st.write(
                    "セキュリティと利便性はトレードオフの関係にあります。"
                    "どちらを優先すべきかは、守りたい情報の重要度（例：銀行口座かSNSか）によって変わります。"
                )

            st.write("---")
            st.subheader("学習のまとめ")
            st.markdown(
                """
- 多要素認証は **知識要素・所持要素・生体要素** の3種類に分類できる
- 異なる種類の要素を組み合わせるほど、1つが突破されても他の要素が防御できるため、なりすましされにくくなる
- 一方で、要素を増やすほど入力や準備の手間が増え、**利便性は下がる**傾向がある
- セキュリティと利便性は多くの場合トレードオフの関係にあり、用途に応じたバランスが重要
                """
            )
            st.success("お疲れさまでした！多要素認証の仕組みとバランス感覚を体験できましたね🎉")
            st.balloons()
