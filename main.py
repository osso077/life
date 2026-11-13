
import streamlit as st
import time
import random
import re

# ==================================================
# 1. 기본 설정
# ==================================================

st.set_page_config(
    page_title="VIBE CHECK | 취향 치트키",
    page_icon="⚡",
    layout="wide"
)

# ==================================================
# 2. 디자인
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800;900&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0,245,212,.10), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(155,93,229,.13), transparent 30%),
        linear-gradient(135deg, #090b1c, #11152d 55%, #17142d);
    color: #f7f7ff;
    font-family: 'Pretendard', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 1250px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

h1, h2, h3, p, label { color: #f7f7ff; }

h1, h2, h3 { font-weight: 900 !important; }

.vibe-title {
    font-size: 3.5rem;
    line-height: 1.1;
    font-weight: 900;
    text-align: center;
    letter-spacing: -2px;
    background: linear-gradient(90deg, #00f5d4, #00bbf9, #c77dff, #ff70a6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.vibe-subtitle {
    text-align: center;
    color: #b9c1e5;
    font-size: 1.05rem;
    margin-top: 12px;
    margin-bottom: 35px;
}

.eyebrow, .section-label {
    color: #00f5d4;
    font-size: .76rem;
    font-weight: 900;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

.eyebrow {
    text-align: center;
    letter-spacing: 3px;
}

.hero-card {
    background: linear-gradient(120deg, rgba(0,245,212,.13), rgba(155,93,229,.15));
    border: 1px solid rgba(0,245,212,.28);
    border-radius: 26px;
    padding: 28px;
    margin: 12px 0 25px 0;
}

.hero-card p { color: #c5cbe7; margin-bottom: 0; }

div.stButton > button {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(255,255,255,.08);
    color: white !important;
    font-weight: 800;
    min-height: 46px;
    transition: .2s;
}

div.stButton > button:hover {
    border-color: #00f5d4;
    color: #00f5d4 !important;
    background: rgba(0,245,212,.10);
    transform: translateY(-2px);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #00c9b7, #00a8e8);
    border: none;
    color: #071321 !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #202744 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #00f5d4 !important;
    border: 1px solid #596487 !important;
    border-radius: 12px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #aab4d0 !important;
    -webkit-text-fill-color: #aab4d0 !important;
    opacity: 1 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #202744 !important;
    color: #ffffff !important;
    border-color: #596487 !important;
}

.stSelectbox div[data-baseweb="select"] span {
    color: #ffffff !important;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.12);
    padding: 18px;
    border-radius: 18px;
}

[data-testid="stMetricValue"] { color: #00f5d4; }

[data-testid="stSidebar"] {
    background: #0d1024;
    border-right: 1px solid rgba(255,255,255,.10);
}

[data-testid="stSidebar"] * { color: #f7f7ff; }

div[data-testid="stForm"] {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 20px;
    padding: 20px;
}

[data-testid="stAlert"] { border-radius: 14px; }

.recipe-card {
    background: linear-gradient(135deg, rgba(255,255,255,.075), rgba(155,93,229,.08));
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 15px;
}

.status-safe {
    color: #00f5d4;
    background: rgba(0,245,212,.10);
    border: 1px solid rgba(0,245,212,.3);
    padding: 4px 9px;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 800;
}

.timer-display {
    font-size: 4rem;
    font-weight: 900;
    text-align: center;
    color: #00f5d4;
    letter-spacing: 4px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. 레시피 데이터베이스
# ==================================================

RECIPES = [
    {
        "name": "계란 볶음밥",
        "emoji": "🍳",
        "category": "한식",
        "time": 10,
        "difficulty": "쉬움",
        "ingredients": ["계란", "밥", "대파"],
        "extra": ["간장", "식용유"],
        "description": "간단하지만 든든하게 먹을 수 있는 기본 볶음밥!",
        "steps": [
            "대파를 잘게 썰어 준비해 줘.",
            "팬에 식용유를 두르고 대파를 볶아 향을 내 줘.",
            "밥을 넣고 잘 풀어가며 볶아 줘.",
            "계란을 넣고 밥과 골고루 섞어 줘.",
            "간장으로 간을 맞추면 완성!"
        ]
    },
    {
        "name": "김치볶음밥",
        "emoji": "🍚",
        "category": "한식",
        "time": 15,
        "difficulty": "쉬움",
        "ingredients": ["김치", "밥"],
        "extra": ["참기름", "계란", "식용유"],
        "description": "냉장고에 남은 김치를 활용하기 좋은 메뉴!",
        "steps": [
            "김치를 먹기 좋은 크기로 잘라 줘.",
            "팬에 기름을 두르고 김치를 볶아 줘.",
            "밥을 넣고 김치와 골고루 섞어 줘.",
            "기호에 따라 참기름을 넣어 줘.",
            "계란을 곁들이면 더욱 맛있어!"
        ]
    },
    {
        "name": "토마토 계란볶음",
        "emoji": "🍅",
        "category": "한식",
        "time": 10,
        "difficulty": "쉬움",
        "ingredients": ["토마토", "계란"],
        "extra": ["소금", "식용유"],
        "description": "부드러운 계란과 상큼한 토마토의 조합!",
        "steps": [
            "토마토를 먹기 좋은 크기로 잘라 줘.",
            "계란을 풀어 팬에서 부드럽게 익혀 줘.",
            "토마토를 넣고 함께 볶아 줘.",
            "소금으로 간을 맞추면 완성!"
        ]
    },
    {
        "name": "감자전",
        "emoji": "🥔",
        "category": "한식",
        "time": 20,
        "difficulty": "보통",
        "ingredients": ["감자"],
        "extra": ["소금", "식용유"],
        "description": "감자 하나로도 도전할 수 있는 바삭한 메뉴!",
        "steps": [
            "감자를 깨끗하게 씻어 준비해 줘.",
            "감자를 강판에 갈거나 잘게 갈아 줘.",
            "소금으로 간을 해 줘.",
            "팬에 기름을 두르고 앞뒤로 노릇하게 익혀 줘."
        ]
    },
    {
        "name": "참치마요 덮밥",
        "emoji": "🍱",
        "category": "한식",
        "time": 10,
        "difficulty": "쉬움",
        "ingredients": ["참치", "밥"],
        "extra": ["마요네즈", "간장", "김가루"],
        "description": "요리 초보도 간단하게 만들 수 있는 한 그릇 메뉴!",
        "steps": [
            "참치의 기름을 적당히 제거해 줘.",
            "밥을 그릇에 담아 줘.",
            "참치를 밥 위에 올려 줘.",
            "마요네즈와 간장을 기호에 맞게 곁들여 줘.",
            "김가루를 뿌리면 완성!"
        ]
    },
    {
        "name": "베이컨 크림 파스타",
        "emoji": "🍝",
        "category": "양식",
        "time": 20,
        "difficulty": "보통",
        "ingredients": ["베이컨", "우유", "치즈"],
        "extra": ["파스타면", "마늘", "소금"],
        "description": "우유와 치즈로 만드는 부드러운 크림 파스타!",
        "steps": [
            "파스타면을 포장지 안내에 따라 삶아 줘.",
            "베이컨과 마늘을 먹기 좋은 크기로 준비해 줘.",
            "팬에 베이컨과 마늘을 볶아 줘.",
            "우유와 치즈를 넣고 소스를 만들어 줘.",
            "삶은 면을 넣고 잘 섞어 주면 완성!"
        ]
    },
    {
        "name": "햄 계란말이",
        "emoji": "🍳",
        "category": "한식",
        "time": 10,
        "difficulty": "보통",
        "ingredients": ["햄", "계란"],
        "extra": ["소금", "식용유"],
        "description": "간단한 반찬으로 활용하기 좋은 메뉴!",
        "steps": [
            "햄을 잘게 썰어 줘.",
            "계란을 풀고 햄을 섞어 줘.",
            "팬에 기름을 얇게 둘러 줘.",
            "계란물을 조금씩 부어가며 말아 줘.",
            "속까지 충분히 익히면 완성!"
        ]
    },
    {
        "name": "바나나 팬케이크",
        "emoji": "🥞",
        "category": "간식",
        "time": 15,
        "difficulty": "쉬움",
        "ingredients": ["바나나", "계란"],
        "extra": ["밀가루", "우유"],
        "description": "달콤한 바나나를 활용한 간단한 간식!",
        "steps": [
            "바나나를 으깨 줘.",
            "계란을 넣고 잘 섞어 줘.",
            "기호에 따라 밀가루를 조금 넣어 줘.",
            "팬에 반죽을 올리고 약한 불에서 익혀 줘.",
            "앞뒤로 충분히 익히면 완성!"
        ]
    },
    {
        "name": "감자 치즈구이",
        "emoji": "🧀",
        "category": "간식",
        "time": 20,
        "difficulty": "쉬움",
        "ingredients": ["감자", "치즈"],
        "extra": ["소금", "버터"],
        "description": "포슬포슬한 감자와 고소한 치즈의 조합!",
        "steps": [
            "감자를 깨끗하게 씻어 충분히 익혀 줘.",
            "익은 감자를 먹기 좋은 크기로 나눠 줘.",
            "치즈를 위에 올려 줘.",
            "치즈가 녹을 때까지 익혀 줘."
        ]
    },
    {
        "name": "참치 김치찌개",
        "emoji": "🍲",
        "category": "한식",
        "time": 25,
        "difficulty": "보통",
        "ingredients": ["참치", "김치"],
        "extra": ["양파", "대파", "물"],
        "description": "남은 김치와 참치로 만드는 든든한 찌개!",
        "steps": [
            "김치와 채소를 먹기 좋은 크기로 썰어 줘.",
            "냄비에 김치를 넣고 가볍게 볶아 줘.",
            "물을 넣고 충분히 끓여 줘.",
            "참치와 채소를 넣어 더 끓여 줘.",
            "재료가 충분히 익으면 완성!"
        ]
    },
    {
        "name": "우유 계란죽",
        "emoji": "🥣",
        "category": "간단식",
        "time": 15,
        "difficulty": "쉬움",
        "ingredients": ["우유", "계란", "밥"],
        "extra": ["소금", "치즈"],
        "description": "부드럽고 따뜻하게 즐길 수 있는 한 그릇 메뉴!",
        "steps": [
            "냄비에 밥과 우유를 넣어 줘.",
            "약한 불에서 저어가며 끓여 줘.",
            "계란을 풀어 넣고 잘 섞어 줘.",
            "소금으로 간을 맞춰 줘.",
            "기호에 따라 치즈를 추가해 줘."
        ]
    },
    {
        "name": "햄 치즈 토스트",
        "emoji": "🥪",
        "category": "간식",
        "time": 10,
        "difficulty": "쉬움",
        "ingredients": ["햄", "치즈", "빵"],
        "extra": ["버터", "계란"],
        "description": "아침 식사나 간식으로 좋은 간단 토스트!",
        "steps": [
            "빵 사이에 햄과 치즈를 넣어 줘.",
            "팬에 버터를 녹여 줘.",
            "토스트를 앞뒤로 노릇하게 구워 줘.",
            "치즈가 녹으면 완성!"
        ]
    }
]


# ==================================================
# 4. 재료 이름 인식 및 매칭
# ==================================================

INGREDIENT_ALIASES = {
    "달걀": "계란",
    "대파": "대파",
    "파": "대파",
    "밥": "밥",
    "쌀밥": "밥",
    "식빵": "빵",
    "토스트": "빵",
    "스팸": "햄",
    "슬라이스햄": "햄",
    "베이컨": "베이컨",
    "모짜렐라치즈": "치즈",
    "체다치즈": "치즈"
}


def normalize_ingredient(name):
    name = name.strip().replace(" ", "")

    if name in INGREDIENT_ALIASES:
        return INGREDIENT_ALIASES[name]

    return name


def parse_ingredients(text):
    raw_items = re.split(r"[,，\n;]+", text)

    result = []

    for item in raw_items:
        clean = re.sub(r"[<>]", "", item.strip())

        if clean:
            normalized = normalize_ingredient(clean)

            if normalized not in result:
                result.append(normalized)

    return result


def ingredient_matches(required, available):
    required = normalize_ingredient(required)

    for item in available:
        item = normalize_ingredient(item)

        if required == item:
            return True

        if len(required) >= 2 and len(item) >= 2:
            if required in item or item in required:
                return True

    return False


def match_recipe(recipe, available):
    matched = []
    missing = []

    for ingredient in recipe["ingredients"]:
        if ingredient_matches(ingredient, available):
            matched.append(ingredient)
        else:
            missing.append(ingredient)

    score = len(matched) / len(recipe["ingredients"])

    return matched, missing, score


def recommend_recipes(available, category, max_time, difficulty):
    results = []

    for recipe in RECIPES:

        if category != "전체" and recipe["category"] != category:
            continue

        if recipe["time"] > max_time:
            continue

        if difficulty != "전체" and recipe["difficulty"] != difficulty:
            continue

        matched, missing, score = match_recipe(recipe, available)

        if matched:
            results.append({
                "recipe": recipe,
                "matched": matched,
                "missing": missing,
                "score": score
            })

    results.sort(
        key=lambda x: (
            x["score"],
            len(x["matched"]),
            -len(x["missing"]),
            -x["recipe"]["time"]
        ),
        reverse=True
    )

    return results


# ==================================================
# 5. 세션 상태
# ==================================================

defaults = {
    "selected_menu": "홈",
    "recipe_results": None,
    "recipe_ingredients": "",
    "recipe_category": "전체",
    "recipe_max_time": 30,
    "recipe_difficulty": "전체",
    "study_seconds": 25 * 60,
    "study_running": False,
    "study_started_at": None,
    "study_subject": "수학",
    "study_sessions": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def navigate_to(menu):
    st.session_state.selected_menu = menu
    st.rerun()


# ==================================================
# 6. 사이드바
# ==================================================

with st.sidebar:

    st.markdown(
        '<div class="vibe-title" style="font-size:2rem;">VIBE CHECK</div>',
        unsafe_allow_html=True
    )

    st.caption("YOUR PERSONAL LIFE HACK")
    st.divider()

    menus = [
        ("🏠", "홈"),
        ("🥑", "냉장고 파먹기"),
        ("⏱️", "스터디 타이머"),
        ("💜", "고민 상담소"),
        ("🔎", "팩트체크")
    ]

    for icon, menu in menus:

        if st.button(
            f"{icon}  {menu}",
            key=f"side_{menu}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.selected_menu == menu
                else "secondary"
            )
        ):
            navigate_to(menu)

    st.divider()
    st.caption("⚡ YOUR SPACE. YOUR PACE.")


# ==================================================
# 7. 홈 화면
# ==================================================

if st.session_state.selected_menu == "홈":

    st.markdown(
        '<div class="eyebrow">⚡ YOUR PERSONAL LIFE HACK</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="vibe-title">VIBE CHECK</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="vibe-subtitle">나만의 취향 치트키 ⚡</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="hero-card">
        <div class="section-label">TODAY'S VIBE</div>
        <h2>오늘 하루도 나답게, 가볍게 시작하기.</h2>
        <p>먹고, 공부하고, 생각을 정리하는 나만의 작은 공간.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ✨ QUICK START")
    st.caption("원하는 기능을 선택해 바로 시작해 봐.")

    c1, c2 = st.columns(2)

    with c1:

        with st.container(border=True):
            st.markdown("## 🥑 냉장고 파먹기")
            st.write("가지고 있는 재료로 만들 수 있는 요리를 찾아봐.")

            if st.button("레시피 찾기 →", key="home_fridge", use_container_width=True):
                navigate_to("냉장고 파먹기")

        with st.container(border=True):
            st.markdown("## 💜 고민 상담소")
            st.write("마음속 이야기를 정리하고 잠깐 쉬어 가기.")

            if st.button("마음 정리하기 →", key="home_worry", use_container_width=True):
                navigate_to("고민 상담소")

    with c2:

        with st.container(border=True):
            st.markdown("## ⏱️ 스터디 타이머")
            st.write("오늘의 목표를 정하고 집중하는 시간 만들기.")

            if st.button("집중 시작하기 →", key="home_study", use_container_width=True):
                navigate_to("스터디 타이머")

        with st.container(border=True):
            st.markdown("## 🔎 팩트체크")
            st.write("정보를 무작정 믿기 전에 한 번 더 확인하기.")

            if st.button("검토하러 가기 →", key="home_fact", use_container_width=True):
                navigate_to("팩트체크")


# ==================================================
# 8. 스마트 레시피 큐레이터
# ==================================================

elif st.session_state.selected_menu == "냉장고 파먹기":

    st.markdown(
        '<div class="section-label">SMART RECIPE CURATOR</div>',
        unsafe_allow_html=True
    )

    st.title("🥑 냉장고 파먹기")

    st.caption(
        "냉장고 속 재료를 입력하면 만들 수 있는 요리를 찾아줄게."
    )

    st.markdown("""
    <div class="hero-card">
        <h2>오늘은 뭐 먹지? 🤔</h2>
        <p>
            가지고 있는 재료를 알려 줘!
            재료에 맞는 레시피를 찾아볼게.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧺 STEP 01. 가지고 있는 재료")

    with st.form("recipe_search_form"):

        ingredients_text = st.text_area(
            "냉장고 속 재료를 입력해 줘.",
            value=st.session_state.recipe_ingredients,
            placeholder="예: 계란, 양파, 대파, 밥, 김치",
            height=110
        )

        st.caption("쉼표(,)로 구분해서 여러 재료를 입력할 수 있어.")

        st.markdown("### 🍽️ STEP 02. 원하는 요리 조건")

        c1, c2 = st.columns(2)

        with c1:
            category = st.selectbox(
                "음식 종류",
                ["전체", "한식", "양식", "간식", "간단식"],
                index=[
                    "전체", "한식", "양식", "간식", "간단식"
                ].index(st.session_state.recipe_category)
            )

        with c2:
            max_time = st.selectbox(
                "조리 시간",
                [10, 20, 30],
                index=[10, 20, 30].index(
                    st.session_state.recipe_max_time
                ),
                format_func=lambda x: f"{x}분 이내"
            )

        difficulty = st.selectbox(
            "요리 난이도",
            ["전체", "쉬움", "보통"]
        )

        search_submitted = st.form_submit_button(
            "✨ 내 재료로 레시피 찾기",
            type="primary",
            use_container_width=True
        )

        if search_submitted:

            available = parse_ingredients(ingredients_text)

            if not available:
                st.session_state.recipe_results = None
                st.warning("재료를 한 가지 이상 입력해 줘!")

            else:
                st.session_state.recipe_ingredients = ingredients_text
                st.session_state.recipe_category = category
                st.session_state.recipe_max_time = max_time
                st.session_state.recipe_difficulty = difficulty

                st.session_state.recipe_results = recommend_recipes(
                    available,
                    category,
                    max_time,
                    difficulty
                )

                st.rerun()

    # 추천 결과
    if st.session_state.recipe_results is not None:

        st.markdown("---")
        st.markdown("### 🍳 YOUR RECIPE RESULTS")

        available = parse_ingredients(
            st.session_state.recipe_ingredients
        )

        results = st.session_state.recipe_results

        if not results:

            st.warning(
                "조건에 맞는 레시피를 찾지 못했어."
            )

            st.info(
                "재료를 더 추가하거나 조리 시간, 음식 종류, 난이도를 바꿔 봐!"
            )

        else:

            st.success(
                f"총 {len(results)}개의 레시피를 찾았어!"
            )

            st.caption(
                "보유한 필수 재료가 많은 메뉴부터 보여주고 있어."
            )

            for index, result in enumerate(results[:8]):

                recipe = result["recipe"]
                matched = result["matched"]
                missing = result["missing"]
                score = result["score"]

                with st.container(border=True):

                    st.markdown(
                        f"## {recipe['emoji']} {recipe['name']}"
                    )

                    st.caption(
                        f"⏱️ {recipe['time']}분  ·  "
                        f"난이도 {recipe['difficulty']}  ·  "
                        f"{recipe['category']}"
                    )

                    st.write(recipe["description"])

                    st.progress(score)

                    st.caption(
                        f"필수 재료 일치율: {int(score * 100)}%"
                    )

                    st.markdown("**🟢 가지고 있는 재료**")

                    if matched:
                        st.success(" · ".join(matched))

                    st.markdown("**🛒 추가로 필요한 재료**")

                    if missing:
                        st.warning(" · ".join(missing))
                    else:
                        st.success("필수 재료가 모두 있어!")

                    st.markdown("**🧂 선택 재료**")
                    st.caption(" · ".join(recipe["extra"]))

                    with st.expander("👩‍🍳 조리 방법 보기"):

                        for step_num, step in enumerate(
                            recipe["steps"], 1
                        ):
                            st.write(f"**{step_num}.** {step}")

                        st.info(
                            "조리 전 재료의 상태를 확인하고, "
                            "고기와 계란 등은 충분히 익혀 먹어 줘!"
                        )

            st.caption(
                "※ 추천 결과는 등록된 레시피 데이터베이스를 기준으로 계산해. "
                "모든 재료가 일치하지 않아도 일부 재료가 일치하면 추천할 수 있어."
            )

    st.markdown("---")

    if st.button(
        "↻ 재료 입력 초기화",
        use_container_width=True
    ):
        st.session_state.recipe_ingredients = ""
        st.session_state.recipe_results = None
        st.rerun()


# ==================================================
# 9. 스터디 타이머
# ==================================================

elif st.session_state.selected_menu == "스터디 타이머":

    st.markdown(
        '<div class="section-label">FOCUS MODE</div>',
        unsafe_allow_html=True
    )

    st.title("⏱️ 스터디 타이머")
    st.caption("완벽한 계획보다 지금 시작하는 시간이 더 중요해.")

    subject = st.text_input(
        "공부할 과목",
        value=st.session_state.study_subject
    )

    st.session_state.study_subject = subject

    timer_mode = st.selectbox(
        "집중 시간",
        ["25분 집중", "50분 집중", "15분 집중"]
    )

    duration_map = {
        "25분 집중": 25 * 60,
        "50분 집중": 50 * 60,
        "15분 집중": 15 * 60
    }

    if not st.session_state.study_running:
        st.session_state.study_seconds = duration_map[timer_mode]

    if st.session_state.study_running:

        elapsed = int(
            time.time() - st.session_state.study_started_at
        )

        remaining = max(
            0,
            st.session_state.study_seconds - elapsed
        )

        if remaining == 0:

            st.session_state.study_running = False
            st.session_state.study_sessions += 1
            st.session_state.study_started_at = None
            st.session_state.study_seconds = duration_map[timer_mode]

            st.success("🎉 집중 세션 완료! 잠깐 쉬어 가자.")

    remaining = st.session_state.study_seconds

    if st.session_state.study_running:

        elapsed = int(
            time.time() - st.session_state.study_started_at
        )

        remaining = max(
            0,
            st.session_state.study_seconds - elapsed
        )

    minutes = remaining // 60
    seconds = remaining % 60

    st.markdown(
        f'<div class="timer-display">{minutes:02d}:{seconds:02d}</div>',
        unsafe_allow_html=True
    )

    st.progress(
        max(
            0.0,
            min(
                1.0,
                1 - remaining / duration_map[timer_mode]
            )
        )
    )

    st.caption(f"현재 목표: {st.session_state.study_subject}")

    b1, b2 = st.columns(2)

    with b1:

        if not st.session_state.study_running:

            if st.button(
                "▶ 집중 시작",
                type="primary",
                use_container_width=True
            ):
                st.session_state.study_seconds = duration_map[timer_mode]
                st.session_state.study_started_at = time.time()
                st.session_state.study_running = True
                st.rerun()

        else:

            if st.button(
                "⏸ 일시 정지",
                use_container_width=True
            ):

                elapsed = int(
                    time.time() - st.session_state.study_started_at
                )

                st.session_state.study_seconds = max(
                    0,
                    st.session_state.study_seconds - elapsed
                )

                st.session_state.study_running = False
                st.session_state.study_started_at = None
                st.rerun()

    with b2:

        if st.button(
            "↻ 타이머 초기화",
            use_container_width=True
        ):
            st.session_state.study_running = False
            st.session_state.study_started_at = None
            st.session_state.study_seconds = duration_map[timer_mode]
            st.rerun()

    st.markdown("---")

    st.metric(
        "완료한 집중 세션",
        f"{st.session_state.study_sessions}회"
    )


# ==================================================
# 10. 고민 상담소
# ==================================================

elif st.session_state.selected_menu == "고민 상담소":

    st.markdown(
        '<div class="section-label">MIND CARE SPACE</div>',
        unsafe_allow_html=True
    )

    st.title("💜 익명 고민 상담소")

    st.caption(
        "정답을 찾지 않아도 괜찮아. 먼저 마음속 이야기를 정리해 보자."
    )

    st.markdown("""
    <div class="hero-card">
        <h2>오늘 마음은 어떤 날씨야?</h2>
        <p>여기서는 완벽하게 말하지 않아도 괜찮아.</p>
    </div>
    """, unsafe_allow_html=True)

    mood = st.select_slider(
        "지금 기분을 골라 봐.",
        options=[
            "많이 지침",
            "조금 우울함",
            "그냥 그래",
            "괜찮음",
            "기분 좋음"
        ]
    )

    worry = st.text_area(
        "하고 싶은 이야기를 적어 줘.",
        placeholder="무슨 일이 있었는지 천천히 적어 봐.",
        height=180
    )

    if st.button(
        "내 마음 정리하기",
        type="primary",
        use_container_width=True
    ):

        if not worry.strip():

            st.warning("마음속 이야기를 한 줄이라도 적어 봐.")

        else:

            messages = [
                "지금 느끼는 감정은 틀린 게 아니야. 스스로를 너무 몰아붙이지 않았으면 좋겠어.",
                "모든 일을 오늘 다 해결하지 않아도 괜찮아. 하나씩 정리해도 충분해.",
                "다른 사람의 속도와 비교하지 말고, 지금 할 수 있는 만큼만 해도 괜찮아.",
                "힘든 마음을 말로 꺼내는 것도 용기가 필요한 일이야. 이야기해 줘서 고마워."
            ]

            st.markdown("---")
            st.markdown("### 🌷 오늘의 작은 응원")

            st.success(random.choice(messages))

            st.caption(f"선택한 오늘의 기분: {mood}")

            st.info(
                "이 공간은 생각을 정리하는 데 도움을 주기 위한 곳이야. "
                "마음이 오래 힘들거나 혼자 감당하기 어렵다면 믿을 수 있는 어른에게도 이야기해 줘."
            )


# ==================================================
# 11. 팩트체크
# ==================================================

elif st.session_state.selected_menu == "팩트체크":

    st.markdown(
        '<div class="section-label">TRUTH CHECK LAB</div>',
        unsafe_allow_html=True
    )

    st.title("🔎 팩트체크")

    st.caption(
        "자극적인 문장일수록 한 번 더 확인하는 습관!"
    )

    st.markdown("""
    <div class="hero-card">
        <h2>잠깐, 이 정보 정말 사실일까?</h2>
        <p>문장을 입력하고 확인해야 할 부분을 정리해 보자.</p>
    </div>
    """, unsafe_allow_html=True)

    claim = st.text_area(
        "확인하고 싶은 문장",
        placeholder="인터넷에서 본 정보나 기사 제목을 입력해 봐.",
        height=150
    )

    if st.button(
        "🔍 문장 점검하기",
        type="primary",
        use_container_width=True
    ):

        if not claim.strip():

            st.warning("먼저 확인하고 싶은 문장을 입력해 줘.")

        else:

            warning_words = [
                "무조건",
                "100%",
                "절대",
                "충격",
                "비밀",
                "전부",
                "완벽하게",
                "확실히"
            ]

            found_words = [
                word for word in warning_words
                if word in claim
            ]

            st.markdown("---")
            st.markdown("### 🧪 점검 결과")

            st.info(
                "이 기능은 문장의 표현을 점검하는 간단한 보조 도구야. "
                "실제 사실 여부를 판정하거나 인터넷 자료를 확인한 결과는 아니야."
            )

            if found_words:

                st.warning(
                    "확인해 볼 표현: " + ", ".join(found_words)
                )

            else:

                st.success(
                    "특별히 등록된 과장 표현은 발견되지 않았어."
                )

            st.markdown("#### 직접 확인해 볼 체크리스트")

            st.write("- 작성자와 출처가 명확한가?")
            st.write("- 작성 날짜가 최근인가?")
            st.write("- 다른 신뢰할 만한 자료에서도 같은 내용을 확인할 수 있는가?")
            st.write("- 사실과 개인의 의견이 구분되어 있는가?")

            st.markdown("#### 입력한 문장")
            st.write(claim)


# ==================================================
# 12. 공통 푸터
# ==================================================

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:15px 0; color:#858eaf;">
    <div style="font-weight:900; letter-spacing:2px; color:#00f5d4;">
        VIBE CHECK ⚡
    </div>
    <div style="font-size:.78rem; margin-top:7px;">
        YOUR SPACE. YOUR PACE. YOUR VIBE.
    </div>
</div>
""", unsafe_allow_html=True)
