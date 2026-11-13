
import streamlit as st
import time
import random
import re
from datetime import datetime

# ==================================================
# 1. 기본 설정
# ==================================================

st.set_page_config(
    page_title="VIBE CHECK | 취향 치트키",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. 디자인 CSS
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

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1250px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

h1, h2, h3, p, label {
    color: #f7f7ff;
}

h1 {
    font-weight: 900 !important;
    letter-spacing: -1.5px;
}

h2, h3 {
    font-weight: 800 !important;
}

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

.eyebrow {
    color: #00f5d4;
    font-size: .75rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-align: center;
    margin-bottom: 12px;
}

.section-label {
    color: #00f5d4;
    font-size: .76rem;
    font-weight: 900;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.glass-card {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 10px 35px rgba(0,0,0,.18);
}

.hero-card {
    background: linear-gradient(120deg, rgba(0,245,212,.13), rgba(155,93,229,.15));
    border: 1px solid rgba(0,245,212,.28);
    border-radius: 26px;
    padding: 28px;
    margin: 12px 0 25px 0;
}

.hero-card h2 {
    margin: 0;
    font-size: 1.65rem;
}

.hero-card p {
    color: #c5cbe7;
    margin-bottom: 0;
}

.mini-label {
    color: #aab2d5;
    font-size: .8rem;
    font-weight: 700;
}

.big-number {
    font-size: 2.1rem;
    font-weight: 900;
    color: #00f5d4;
}

.food-card-title {
    font-size: 1.05rem;
    font-weight: 900;
    margin-top: 8px;
}

.food-card-info {
    color: #b7bfdc;
    font-size: .82rem;
}

.status-urgent {
    color: #ff8da1;
    background: rgba(255,77,109,.13);
    border: 1px solid rgba(255,77,109,.4);
    padding: 4px 9px;
    border-radius: 20px;
    font-size: .72rem;
    font-weight: 800;
}

.status-safe {
    color: #00f5d4;
    background: rgba(0,245,212,.10);
    border: 1px solid rgba(0,245,212,.3);
    padding: 4px 9px;
    border-radius: 20px;
    font-size: .72rem;
    font-weight: 800;
}

div.stButton > button {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(255,255,255,.08);
    color: white;
    font-weight: 800;
    min-height: 46px;
    transition: .2s;
}

div.stButton > button:hover {
    border-color: #00f5d4;
    color: #00f5d4;
    background: rgba(0,245,212,.10);
    transform: translateY(-2px);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #00c9b7, #00a8e8);
    border: none;
    color: #071321;
}

div.stButton > button[kind="primary"]:hover {
    color: #071321;
    box-shadow: 0 0 22px rgba(0,245,212,.28);
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.07) !important;
    color: white !important;
    border-color: rgba(255,255,255,.17) !important;
    border-radius: 12px !important;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.12);
    padding: 18px;
    border-radius: 18px;
}

[data-testid="stMetricValue"] {
    color: #00f5d4;
}

[data-testid="stSidebar"] {
    background: #0d1024;
    border-right: 1px solid rgba(255,255,255,.10);
}

[data-testid="stSidebar"] * {
    color: #f7f7ff;
}

hr {
    border-color: rgba(255,255,255,.12);
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 20px;
    padding: 20px;
}

div[data-testid="stAlert"] {
    border-radius: 14px;
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
# 3. 음식 이미지 및 분류
# ==================================================

FOOD_IMAGES = {
    "채소": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=700",
    "과일": "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=700",
    "고기": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=700",
    "해산물": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=700",
    "유제품": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=700",
    "빵": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=700",
    "밥": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=700",
    "기타": "https://images.unsplash.com/photo-1547592180-85f173990554?w=700"
}

FOOD_KEYWORDS = {
    "채소": [
        "양파", "대파", "파", "마늘", "감자", "고구마",
        "당근", "토마토", "오이", "배추", "김치", "상추",
        "양배추", "브로콜리", "버섯", "애호박", "호박"
    ],
    "과일": [
        "사과", "바나나", "딸기", "포도", "수박",
        "오렌지", "귤", "복숭아", "키위", "블루베리"
    ],
    "고기": [
        "고기", "소고기", "돼지고기", "삼겹살",
        "베이컨", "닭고기", "닭가슴살", "치킨",
        "햄", "소시지", "스팸"
    ],
    "해산물": [
        "생선", "연어", "새우", "오징어", "참치",
        "고등어", "갈치", "조개"
    ],
    "유제품": [
        "우유", "치즈", "버터", "계란", "달걀",
        "요거트", "요플레", "두유"
    ],
    "빵": ["빵", "식빵", "베이글", "크루아상"],
    "밥": ["밥", "쌀", "볶음밥"]
}

FOOD_EMOJI = {
    "계란": "🥚", "달걀": "🥚", "우유": "🥛",
    "치즈": "🧀", "버터": "🧈", "양파": "🧅",
    "대파": "🌱", "파": "🌱", "마늘": "🧄",
    "감자": "🥔", "고구마": "🍠", "당근": "🥕",
    "토마토": "🍅", "오이": "🥒", "배추": "🥬",
    "김치": "🥬", "상추": "🥬", "브로콜리": "🥦",
    "버섯": "🍄", "사과": "🍎", "바나나": "🍌",
    "딸기": "🍓", "포도": "🍇", "수박": "🍉",
    "소고기": "🥩", "돼지고기": "🥓", "삼겹살": "🥓",
    "닭고기": "🍗", "치킨": "🍗", "햄": "🍖",
    "소시지": "🌭", "스팸": "🥫", "참치": "🐟",
    "생선": "🐟", "연어": "🍣", "새우": "🦐",
    "오징어": "🦑", "밥": "🍚", "빵": "🍞",
    "라면": "🍜", "만두": "🥟"
}


def get_food_category(name):
    for category, keywords in FOOD_KEYWORDS.items():
        if any(keyword in name for keyword in keywords):
            return category
    return "기타"


def get_food_emoji(name):
    for keyword, emoji in FOOD_EMOJI.items():
        if keyword in name:
            return emoji
    return "🍱"


def get_food_image(name):
    category = get_food_category(name)
    return FOOD_IMAGES.get(category, FOOD_IMAGES["기타"])


# ==================================================
# 4. 레시피 데이터
# ==================================================

RECIPES = [
    {
        "name": "계란 볶음밥",
        "emoji": "🍳",
        "ingredients": ["계란", "밥", "대파"],
        "extra": ["간장", "식용유"],
        "time": "10분",
        "difficulty": "쉬움",
        "description": "간단하지만 든든한 한 끼!"
    },
    {
        "name": "김치볶음밥",
        "emoji": "🍚",
        "ingredients": ["김치", "밥", "계란"],
        "extra": ["참기름", "간장"],
        "time": "15분",
        "difficulty": "쉬움",
        "description": "냉장고 속 김치를 활용해 보자."
    },
    {
        "name": "토마토 계란볶음",
        "emoji": "🍅",
        "ingredients": ["토마토", "계란"],
        "extra": ["소금", "식용유"],
        "time": "10분",
        "difficulty": "쉬움",
        "description": "부드럽고 산뜻한 조합."
    },
    {
        "name": "감자전",
        "emoji": "🥔",
        "ingredients": ["감자"],
        "extra": ["소금", "식용유"],
        "time": "20분",
        "difficulty": "보통",
        "description": "감자 하나로 만드는 바삭한 요리."
    },
    {
        "name": "참치마요 덮밥",
        "emoji": "🍱",
        "ingredients": ["참치", "밥", "계란"],
        "extra": ["마요네즈", "간장"],
        "time": "10분",
        "difficulty": "쉬움",
        "description": "빠르고 든든한 덮밥."
    },
    {
        "name": "베이컨 크림 파스타",
        "emoji": "🍝",
        "ingredients": ["베이컨", "우유", "치즈"],
        "extra": ["파스타면", "마늘"],
        "time": "20분",
        "difficulty": "보통",
        "description": "고소한 크림소스가 매력적인 요리."
    },
    {
        "name": "닭가슴살 샐러드",
        "emoji": "🥗",
        "ingredients": ["닭가슴살", "상추", "토마토"],
        "extra": ["드레싱"],
        "time": "10분",
        "difficulty": "쉬움",
        "description": "가볍고 산뜻하게 즐기는 샐러드."
    },
    {
        "name": "햄 계란말이",
        "emoji": "🍳",
        "ingredients": ["햄", "계란"],
        "extra": ["소금", "식용유"],
        "time": "10분",
        "difficulty": "쉬움",
        "description": "반찬으로 활용하기 좋은 메뉴."
    },
    {
        "name": "감자 치즈구이",
        "emoji": "🧀",
        "ingredients": ["감자", "치즈"],
        "extra": ["소금", "후추"],
        "time": "20분",
        "difficulty": "보통",
        "description": "고소하고 포근한 감자 요리."
    },
    {
        "name": "바나나 토스트",
        "emoji": "🍞",
        "ingredients": ["바나나", "빵"],
        "extra": ["꿀", "버터"],
        "time": "5분",
        "difficulty": "쉬움",
        "description": "간단하게 만드는 달콤한 간식."
    }
]


def match_recipe(recipe, available_names):
    matched = []
    missing = []

    for ingredient in recipe["ingredients"]:
        if any(ingredient in item or item in ingredient for item in available_names):
            matched.append(ingredient)
        else:
            missing.append(ingredient)

    return matched, missing


# ==================================================
# 5. 세션 상태
# ==================================================

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "홈"

if "fridge_items" not in st.session_state:
    st.session_state.fridge_items = []

if "recipe_results" not in st.session_state:
    st.session_state.recipe_results = False

if "study_seconds" not in st.session_state:
    st.session_state.study_seconds = 25 * 60

if "study_running" not in st.session_state:
    st.session_state.study_running = False

if "study_started_at" not in st.session_state:
    st.session_state.study_started_at = None

if "study_subject" not in st.session_state:
    st.session_state.study_subject = "수학"

if "study_sessions" not in st.session_state:
    st.session_state.study_sessions = 0

if "worry_answer" not in st.session_state:
    st.session_state.worry_answer = False

if "fact_result" not in st.session_state:
    st.session_state.fact_result = False


def navigate_to(menu):
    st.session_state.selected_menu = menu
    st.rerun()


# ==================================================
# 6. 공통 사이드바
# ==================================================

with st.sidebar:
    st.markdown(
        '<div class="vibe-title" style="font-size:2rem;">VIBE CHECK</div>',
        unsafe_allow_html=True
    )
    st.caption("YOUR PERSONAL LIFE HACK")

    st.divider()

    menu_options = [
        "홈",
        "냉장고 파먹기",
        "스터디 타이머",
        "고민 상담소",
        "팩트체크"
    ]

    for menu in menu_options:
        icon = {
            "홈": "🏠",
            "냉장고 파먹기": "🥑",
            "스터디 타이머": "⏱️",
            "고민 상담소": "💜",
            "팩트체크": "🔎"
        }[menu]

        if st.button(
            f"{icon}  {menu}",
            key=f"side_{menu}",
            use_container_width=True,
            type="primary" if st.session_state.selected_menu == menu else "secondary"
        ):
            navigate_to(menu)

    st.divider()
    st.caption("⚡ MAKE YOUR OWN VIBE")
    st.caption("작은 습관부터 나만의 리듬으로.")


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

    total_items = len(st.session_state.fridge_items)
    urgent_items = [
        item for item in st.session_state.fridge_items
        if item["days"] <= 3
    ]

    st.markdown("""
    <div class="hero-card">
        <div class="section-label">TODAY'S VIBE</div>
        <h2>오늘 하루도 나답게, 가볍게 시작하기.</h2>
        <p>먹고, 공부하고, 생각을 정리하는 나만의 작은 공간.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ✨ 나의 오늘")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("냉장고 재료", f"{total_items}개")

    with m2:
        st.metric("소비 임박 재료", f"{len(urgent_items)}개")

    with m3:
        st.metric("완료한 집중 세션", f"{st.session_state.study_sessions}회")

    st.markdown("---")
    st.markdown("### 🚀 QUICK START")
    st.caption("원하는 기능을 선택해 바로 시작해 봐.")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("## 🥑 냉장고 파먹기")
            st.write("냉장고 속 재료를 정리하고 오늘의 메뉴를 찾아봐.")
            if st.button("냉장고 열기 →", key="home_fridge", use_container_width=True):
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

    if urgent_items:
        st.markdown("---")
        st.markdown("### 🚨 냉장고에서 먼저 확인할 재료")

        for item in urgent_items[:3]:
            st.warning(
                f"{get_food_emoji(item['name'])} {item['name']} · "
                f"등록한 유통기한까지 {item['days']}일"
            )


# ==================================================
# 8. 냉장고 파먹기
# ==================================================

elif st.session_state.selected_menu == "냉장고 파먹기":

    st.markdown('<div class="section-label">SMART FRIDGE SYSTEM</div>', unsafe_allow_html=True)
    st.title("🥑 냉장고 파먹기")
    st.caption("냉장고 속 재료를 한눈에 확인하고, 있는 재료로 만들 수 있는 요리를 찾아보자.")

    items = st.session_state.fridge_items

    total = len(items)
    fridge_count = sum(1 for i in items if i["type"] == "냉장실")
    freezer_count = sum(1 for i in items if i["type"] == "냉동실")
    urgent_count = sum(1 for i in items if i["days"] <= 3)

    a, b, c, d = st.columns(4)

    a.metric("전체 재료", f"{total}개")
    b.metric("냉장실", f"{fridge_count}개")
    c.metric("냉동실", f"{freezer_count}개")
    d.metric("소비 임박", f"{urgent_count}개")

    st.markdown("---")

    # 재료 등록
    st.markdown("### ➕ 새로운 재료 등록")
    st.caption("재료를 등록하면 아래 인벤토리에 사진 카드로 추가돼.")

    with st.form("add_food_form", clear_on_submit=True):

        c1, c2 = st.columns([2, 1])

        with c1:
            new_name = st.text_input(
                "음식 이름",
                placeholder="예: 계란, 삼겹살, 바나나"
            )

        with c2:
            new_type = st.selectbox(
                "보관 위치",
                ["냉장실", "냉동실"]
            )

        c3, c4 = st.columns(2)

        with c3:
            new_qty = st.number_input(
                "수량",
                min_value=1,
                max_value=99,
                value=1
            )

        with c4:
            new_days = st.number_input(
                "소비까지 남은 기간 (일)",
                min_value=1,
                max_value=365,
                value=5
            )

        submitted = st.form_submit_button(
            "＋ 재료 등록하기",
            type="primary",
            use_container_width=True
        )

        if submitted:

            clean_name = re.sub(
                r"[<>]",
                "",
                new_name.strip()
            )

            if clean_name:
                st.session_state.fridge_items.append({
                    "name": clean_name,
                    "type": new_type,
                    "qty": int(new_qty),
                    "days": int(new_days)
                })

                st.success(f"{clean_name} 등록 완료!")
                st.rerun()

            else:
                st.warning("음식 이름을 입력해 줘!")

    st.markdown("---")

    # 재료 검색 및 필터
    st.markdown("### 🧊 MY FRIDGE")

    f1, f2 = st.columns([2, 1])

    with f1:
        search_text = st.text_input(
            "🔎 재료 검색",
            placeholder="찾고 싶은 재료를 입력해 봐."
        )

    with f2:
        location_filter = st.selectbox(
            "보관 위치",
            ["전체", "냉장실", "냉동실"]
        )

    filtered_items = []

    for idx, item in enumerate(st.session_state.fridge_items):

        if search_text and search_text.lower() not in item["name"].lower():
            continue

        if location_filter != "전체" and item["type"] != location_filter:
            continue

        filtered_items.append((idx, item))

    if not filtered_items:

        if not st.session_state.fridge_items:
            st.info("아직 등록된 재료가 없어. 위에서 첫 번째 재료를 추가해 봐!")
        else:
            st.info("검색 조건에 맞는 재료가 없어.")

    else:

        fridge_items = [
            pair for pair in filtered_items
            if pair[1]["type"] == "냉장실"
        ]

        freezer_items = [
            pair for pair in filtered_items
            if pair[1]["type"] == "냉동실"
        ]

        def render_food_cards(section_title, section_items):

            st.markdown(f"#### {section_title}")

            if not section_items:
                st.caption("등록된 재료가 없습니다.")
                return

            card_columns = st.columns(3)

            for position, (original_idx, item) in enumerate(section_items):

                with card_columns[position % 3]:

                    with st.container(border=True):

                        # 음식 사진
                        st.image(
                            get_food_image(item["name"]),
                            use_container_width=True
                        )

                        st.markdown(
                            f"### {get_food_emoji(item['name'])} {item['name']}"
                        )

                        st.caption(
                            f"{get_food_category(item['name'])} · "
                            f"{item['qty']}개 · {item['type']}"
                        )

                        if item["days"] <= 3:
                            st.markdown(
                                f'<span class="status-urgent">D-{item["days"]} 소비 확인!</span>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f'<span class="status-safe">D-{item["days"]} 보관 중</span>',
                                unsafe_allow_html=True
                            )

                        st.write("")

                        if st.button(
                            "이 재료 삭제",
                            key=f"delete_food_{original_idx}",
                            use_container_width=True
                        ):
                            st.session_state.fridge_items.pop(original_idx)
                            st.rerun()

        if location_filter in ["전체", "냉장실"]:
            render_food_cards("❄️ 냉장실", fridge_items)

        if location_filter in ["전체", "냉동실"]:
            render_food_cards("🧊 냉동실", freezer_items)

    # 레시피 추천
    st.markdown("---")
    st.markdown("### 🍽️ WHAT CAN I COOK?")
    st.write("지금 가지고 있는 재료로 만들 수 있는 요리를 추천해 줄게.")

    if st.button(
        "✨ 내 재료로 레시피 찾기",
        type="primary",
        use_container_width=True
    ):
        st.session_state.recipe_results = True

    if st.session_state.recipe_results:

        available_names = [
            item["name"] for item in st.session_state.fridge_items
        ]

        if not available_names:
            st.warning("먼저 냉장고에 재료를 등록해 줘!")

        else:

            scored_recipes = []

            for recipe in RECIPES:

                matched, missing = match_recipe(
                    recipe,
                    available_names
                )

                score = len(matched) / len(recipe["ingredients"])

                if matched:
                    scored_recipes.append(
                        (score, recipe, matched, missing)
                    )

            scored_recipes.sort(
                key=lambda x: (x[0], len(x[2])),
                reverse=True
            )

            if not scored_recipes:
                st.info("현재 재료로 추천할 수 있는 메뉴가 아직 없어.")
            else:

                st.success(
                    f"등록한 재료를 바탕으로 {len(scored_recipes)}개의 메뉴를 찾았어!"
                )

                for score, recipe, matched, missing in scored_recipes[:5]:

                    with st.container(border=True):

                        r1, r2 = st.columns([1, 3])

                        with r1:
                            st.markdown(
                                f"<div style='font-size:3.5rem;text-align:center;padding-top:15px;'>{recipe['emoji']}</div>",
                                unsafe_allow_html=True
                            )

                        with r2:
                            st.markdown(f"### {recipe['name']}")
                            st.caption(
                                f"⏱️ {recipe['time']}  ·  "
                                f"난이도 {recipe['difficulty']}"
                            )
                            st.write(recipe["description"])

                            st.progress(score)

                            st.caption(
                                f"사용 가능: {', '.join(matched)}"
                            )

                            if missing:
                                st.caption(
                                    f"추가로 필요한 재료: {', '.join(missing)}"
                                )
                            else:
                                st.success("필수 재료가 모두 있어!")

                            if recipe["extra"]:
                                st.caption(
                                    f"선택 재료: {', '.join(recipe['extra'])}"
                                )

    st.markdown("---")

    if st.button("🗑️ 냉장고 전체 비우기", use_container_width=True):
        st.session_state.fridge_items = []
        st.session_state.recipe_results = False
        st.rerun()


# ==================================================
# 9. 스터디 타이머
# ==================================================

elif st.session_state.selected_menu == "스터디 타이머":

    st.markdown('<div class="section-label">FOCUS MODE</div>', unsafe_allow_html=True)
    st.title("⏱️ 스터디 타이머")
    st.caption("완벽한 계획보다 지금 시작하는 25분이 더 중요해.")

    st.markdown("---")

    st.markdown("### 🎯 오늘의 집중 목표")

    subject = st.text_input(
        "공부할 과목",
        value=st.session_state.study_subject
    )

    if subject != st.session_state.study_subject:
        st.session_state.study_subject = subject

    timer_mode = st.selectbox(
        "집중 시간 선택",
        ["25분 집중", "50분 집중", "15분 집중"]
    )

    duration_map = {
        "25분 집중": 25 * 60,
        "50분 집중": 50 * 60,
        "15분 집중": 15 * 60
    }

    if not st.session_state.study_running:
        st.session_state.study_seconds = duration_map[timer_mode]

    remaining = st.session_state.study_seconds

    if st.session_state.study_running:

        elapsed = int(time.time() - st.session_state.study_started_at)
        remaining = max(0, st.session_state.study_seconds - elapsed)

        if remaining == 0:
            st.session_state.study_running = False
            st.session_state.study_sessions += 1
            st.session_state.study_seconds = duration_map[timer_mode]
            st.session_state.study_started_at = None
            st.success("🎉 집중 세션 완료! 잠깐 쉬어 가자.")
            remaining = 0

    minutes = remaining // 60
    seconds = remaining % 60

    st.markdown(
        f'<div class="timer-display">{minutes:02d}:{seconds:02d}</div>',
        unsafe_allow_html=True
    )

    st.progress(
        max(0.0, min(1.0, 1 - remaining / duration_map[timer_mode]))
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
            if st.button("⏸ 일시 정지", use_container_width=True):
                elapsed = int(time.time() - st.session_state.study_started_at)
                st.session_state.study_seconds = max(
                    0,
                    st.session_state.study_seconds - elapsed
                )
                st.session_state.study_running = False
                st.session_state.study_started_at = None
                st.rerun()

    with b2:
        if st.button("↻ 타이머 초기화", use_container_width=True):
            st.session_state.study_running = False
            st.session_state.study_started_at = None
            st.session_state.study_seconds = duration_map[timer_mode]
            st.rerun()

    st.markdown("---")
    st.metric("완료한 집중 세션", f"{st.session_state.study_sessions}회")

    if st.session_state.study_running:
        st.info("타이머는 화면을 다시 실행할 때 남은 시간이 갱신돼. 잠시 후 화면을 새로고침해 확인해 줘.")


# ==================================================
# 10. 고민 상담소
# ==================================================

elif st.session_state.selected_menu == "고민 상담소":

    st.markdown('<div class="section-label">MIND CARE SPACE</div>', unsafe_allow_html=True)
    st.title("💜 익명 고민 상담소")
    st.caption("정답을 찾지 않아도 괜찮아. 먼저 마음속 이야기를 정리해 보자.")

    st.markdown("""
    <div class="hero-card">
        <h2>오늘 마음은 어떤 날씨야?</h2>
        <p>여기서는 완벽하게 말하지 않아도 괜찮아.</p>
    </div>
    """, unsafe_allow_html=True)

    mood = st.select_slider(
        "지금 기분을 골라 봐.",
        options=["많이 지침", "조금 우울함", "그냥 그래", "괜찮음", "기분 좋음"]
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
            st.markdown("---")
            st.markdown("### 🌷 오늘의 작은 응원")

            messages = [
                "지금 느끼는 감정은 틀린 게 아니야. 스스로를 너무 몰아붙이지 않았으면 좋겠어.",
                "모든 일을 오늘 다 해결하지 않아도 괜찮아. 하나씩 정리해도 충분해.",
                "다른 사람의 속도와 비교하지 말고, 지금 네가 할 수 있는 만큼만 해도 괜찮아.",
                "힘든 마음을 말로 꺼내는 것도 용기가 필요한 일이야. 이야기해 줘서 고마워."
            ]

            st.success(random.choice(messages))

            st.caption(
                f"선택한 오늘의 기분: {mood}"
            )

            st.info(
                "이 공간은 생각을 정리하는 데 도움을 주기 위한 곳이야. "
                "마음이 오래 힘들거나 혼자 감당하기 어렵다면 믿을 수 있는 어른에게도 이야기해 줘."
            )


# ==================================================
# 11. 팩트체크
# ==================================================

elif st.session_state.selected_menu == "팩트체크":

    st.markdown('<div class="section-label">TRUTH CHECK LAB</div>', unsafe_allow_html=True)
    st.title("🔎 팩트체크")
    st.caption("자극적인 문장일수록 한 번 더 확인하는 습관!")

    st.markdown("""
    <div class="hero-card">
        <h2>잠깐, 이 정보 정말 사실일까?</h2>
        <p>문장을 입력하고 확인해야 할 부분을 정리해 보자.</p>
    </div>
    """, unsafe_allow_html=True)

    claim = st.text_area(
        "확인하고 싶은 문장",
        placeholder="예: 인터넷에서 본 정보나 기사 제목을 입력해 봐.",
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

            st.markdown("---")
            st.markdown("### 🧪 점검 결과")

            warning_words = [
                "무조건", "100%", "절대", "충격",
                "비밀", "전부", "완벽하게", "확실히"
            ]

            found_words = [
                word for word in warning_words
                if word in claim
            ]

            st.info(
                "이 기능은 문장의 표현을 점검하는 간단한 보조 도구야. "
                "실제 사실 여부를 판정하거나 인터넷 자료를 확인한 결과는 아니야."
            )

            if found_words:
                st.warning(
                    "확인해 볼 표현: " + ", ".join(found_words)
                )
            else:
                st.success("특별히 등록된 과장 표현은 발견되지 않았어.")

            st.markdown("#### 직접 확인해 볼 체크리스트")

            st.write("- 작성자와 출처가 명확한가?")
            st.write("- 작성 날짜가 최근인가?")
            st.write("- 다른 신뢰할 만한 자료에서도 같은 내용을 확인할 수 있는가?")
            st.write("- 사실과 개인의 의견이 구분되어 있는가?")

            st.markdown("#### 입력한 문장")
            st.write(claim)


# ==================================================
# 12. 하단 공통 푸터
# ==================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:15px 0; color:#858eaf;">
        <div style="font-weight:900; letter-spacing:2px; color:#00f5d4;">
            VIBE CHECK ⚡
        </div>
        <div style="font-size:.78rem; margin-top:7px;">
            YOUR SPACE. YOUR PACE. YOUR VIBE.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
