import streamlit as st

st.set_page_config(page_title="多要素認証体験ゲーム", page_icon="🔐", layout="wide")

# ---------------------------------------------------------
# データ定義
# ---------------------------------------------------------
METHODS = {
    "パスワード": {"factor": "知識要素", "security": 20, "convenience": 90, "icon": "🔑"},
    "PINコード": {"factor": "知識要素", "security": 15, "convenience": 95, "icon": "🔢"},
    "秘密の質問": {"factor": "知識要素", "security": 10, "convenience": 85, "icon": "❓"},
    "ICカード": {"factor": "所持要素", "security": 30, "convenience": 70, "icon": "💳"},
    "スマートフォン（SMS認証）": {"factor": "所持要素", "security": 25, "convenience": 75, "icon": "📱"},
    "セキュリティキー": {"factor": "所持要素", "security": 35, "convenience": 60, "icon": "🔐"},
    "指紋認証": {"factor": "生体要素", "security": 35, "convenience": 80, "icon": "👆"},
    "顔認証": {"factor": "生体要素", "security": 30, "convenience": 85, "icon": "🙂"},
}

ATTACKS = {
    "パスワード漏洩（フィッシング）": {"target": "知識要素", "desc": "フィッシングサイトなどによってパスワードや秘密の質問の答えが盗まれた。"},
    "スマホ・IC カード盗難": {"target": "所持要素", "desc": "認証に使うスマートフォンやICカード、セキュリティキーが盗まれた。"},
    "偽造指紋・顔認証突破": {"target": "生体要素", "desc": "型取りや高精細写真などにより指紋・顔情報が偽造された。"},
}

DIVERSITY_BONUS = {1: 0, 2: 25, 3: 45}

FACTOR_DESC = {
    "知識要素": "本人だけが知っている情報（例：パスワード、PIN）",
    "所持要素": "本人だけが持っている物（例：スマホ、ICカード）",
    "生体要素": "本人の身体的特徴（例：指紋、顔）",
}

# ---------------------------------------------------------
# セッション状態初期化
# ---------------------------------------------------------
if "selected_methods" not in st.session_state:
    st.session_state.selected_methods = []
if "security_score" not in st.session_state:
    st.session_state.security_score = 0
if "convenience_score" not in st.session_state:
    st.session_state.convenience_score = 0
if "attack_log" not in st.session_state:
    st.session_state.attack_log = []


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
st.title("🔐 多要素認証体験ゲーム")
st.caption("高校「情報Ⅰ」向け ― 多要素認証（知識・所持・生体）を体験的に学ぼう")

tab1, tab2, tab3, tab4 = st.tabs(
    ["① 認証構成セットアップ", "② なりすまし攻撃シミュレーション", "③ 評価", "④ まとめ"]
)

# ---------------------------------------------------------
# ① 認証構成セットアップ画面
# ---------------------------------------------------------
with tab1:
    st.header("① 認証構成セットアップ")
    st.write(
        "以下の認証方法から、実際に使いたいものを選んでください（複数選択可）。"
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
# ② なりすまし攻撃シミュレーション画面
# ---------------------------------------------------------
with tab2:
    st.header("② なりすまし攻撃シミュレーション")

    if not st.session_state.selected_methods:
        st.warning("先に「① 認証構成セットアップ」で認証方法を選択してください。")
    else:
        used_factors = set(METHODS[m]["factor"] for m in st.session_state.selected_methods)
        st.write("あなたの認証構成：", "、".join(st.session_state.selected_methods))
        st.write(f"使用している要素：{'・'.join(used_factors)}")

        attack = st.radio(
            "攻撃者が試みる、なりすまし手段を選んでください",
            options=list(ATTACKS.keys()),
        )
        st.caption(ATTACKS[attack]["desc"])

        if st.button("攻撃を実行する", type="primary"):
            target = ATTACKS[attack]["target"]
            if target not in used_factors:
                st.info(f"🛡️ あなたは「{target}」を利用していないため、この攻撃はそもそも成立しません。")
                result = "対象外（無効）"
            elif len(used_factors) == 1:
                st.error(
                    f"💥 突破されました！「{target}」だけに頼っていたため、"
                    "攻撃者になりすまされてしまいました…"
                )
                result = "なりすまし成功（防御失敗）"
            else:
                remaining = used_factors - {target}
                st.success(
                    f"🛡️ 防御成功！「{target}」は突破されましたが、"
                    f"残りの要素（{'・'.join(remaining)}）が本人確認をブロックしました！"
                )
                result = "防御成功"
            st.session_state.attack_log.append((attack, result))

        if st.session_state.attack_log:
            st.subheader("これまでの攻撃結果ログ")
            for a, r in st.session_state.attack_log:
                st.write(f"- {a} → **{r}**")

# ---------------------------------------------------------
# ③ 評価画面
# ---------------------------------------------------------
with tab3:
    st.header("③ 評価")

    if not st.session_state.selected_methods:
        st.warning("先に「① 認証構成セットアップ」で認証方法を選択してください。")
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

# ---------------------------------------------------------
# ④ まとめ
# ---------------------------------------------------------
with tab4:
    st.header("④ まとめ")

    if not st.session_state.selected_methods:
        st.warning("先に①〜③のフェーズを完了させてください。")
    else:
        st.subheader("学習のポイント")
        st.markdown(
            """
- 多要素認証は **知識要素・所持要素・生体要素** の3種類に分類できる
- 異なる種類の要素を組み合わせるほど、1つが突破されても他の要素が防御できるため、なりすましされにくくなる
- 一方で、要素を増やすほど入力や準備の手間が増え、**利便性は下がる**傾向がある
- セキュリティと利便性は多くの場合トレードオフの関係にあり、用途に応じたバランスが重要
            """
        )

        st.write(
            f"あなたの最終スコア → セキュリティ：**{st.session_state.security_score}点** ／ "
            f"利便性：**{st.session_state.convenience_score}点**"
        )

        if st.button("学習完了！", type="primary"):
            st.success("お疲れさまでした！多要素認証の仕組みとバランス感覚を体験できましたね🎉")
            st.balloons()
