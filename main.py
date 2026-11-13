import streamlit as st
import time
import random
from datetime import date, datetime, timedelta
from openai import OpenAI, OpenAIError

# =========================================================
# 1. 기본 설정
# =========================================================

st.set_page_config(
    page_title="VIBE CHECK",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. 디자인 CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(113, 75, 255, 0.18), transparent 30%),
        radial-gradient(circle at 85% 80%, rgba(0, 220, 255, 0.12), transparent 30%),
        #090b16;
    color: #f5f5ff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1, h2, h3 {
    color: #ffffff !important;
    font-weight: 800 !important;
}

p, label, span, div {
    color: inherit;
}

[data-testid="stSidebar"] {
    background: #101323;
    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] * {
    color: #f5f5ff !important;
}

.hero {
    padding: 35px;
    border-radius: 25px;
    background: linear-gradient(
        135deg,
        rgba(118, 83, 255, 0.25),
        rgba(24, 205, 255, 0.12)
    );
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 25px;
}

.hero-small {
    color: #b9b6ff;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero-title {
    font-size: 42px;
    font-weight: 900;
    margin-top: 8px;
    color: white;
}

.hero-desc {
    color: #c7c9df;
    font-size: 16px;
    margin-top: 10px;
}

.glass-card {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}

.stat-card {
    background: linear-gradient(
        145deg,
        rgba(128, 101, 255, 0.2),
        rgba(255,255,255,0.04)
    );
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 20px;
    text-align: center;
}

.stat-number {
    font-size: 30px;
    font-weight: 900;
    color: #a99aff;
}

.stat-label {
    color: #c6c7dd;
    font-size: 13px;
}

.section-label {
    color: #a99aff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

.fridge-door-box {
    background: linear-gradient(145deg, #dff7fa, #bde8ed);
    color: #17333b;
    border-radius: 18px;
    padding: 18px;
    min-height: 130px;
}

.freezer-door-box {
    background: linear-gradient(145deg, #f1f5f9, #dbeafe);
    color: #1e293b;
    border-radius: 18px;
    padding: 18px;
    min-height: 130px;
}

.fridge-door-box *,
.freezer-door-box * {
    color: #17333b !important;
}

.food-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 14px;
    margin-bottom: 10px;
}

.food-name {
    font-size: 16px;
    font-weight: 800;
}

.food-detail {
    color: #b8bad0;
    font-size: 12px;
    margin-top: 5px;
}

.urgent-badge {
    display: inline-block;
    background: rgba(255, 90, 110, 0.2);
    color: #ff8796;
    border: 1px solid rgba(255,90,110,0.35);
    padding: 4px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
}

.normal-badge {
    display: inline-block;
    background: rgba(90, 220, 170, 0.15);
    color: #76e6bd;
    border: 1px solid rgba(90,220,170,0.3);
    padding: 4px 9px;
    border-radius: 20px;
    font-size: 11px;
}

div.stButton > button {
    background: linear-gradient(135deg, #8065ff, #5c9dff);
    color: white !important;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.55rem 1rem;
    transition: 0.2s;
}

div.stButton > button:hover {
    filter: brightness(1.15);
    transform: translateY(-1px);
}

div.stButton > button p {
    color: white !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #171b2d !important;
    color: #ffffff !important;
    border: 1px solid #414765 !important;
    border-radius: 10px !important;
    caret-color: #a99aff !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #9298b2 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #171b2d !important;
    color: white !important;
    border-color: #414765 !important;
}

.stDateInput input {
    background-color: #171b2d !important;
    color: white !important;
    border-color: #414765 !important;
}

.stRadio label, .stCheckbox label {
    color: #eeeeff !important;
}

.timer-display {
    font-size: 76px;
    font-weight: 900;
    text-align: center;
    color: #a99aff;
    padding: 20px;
    letter-spacing: 3px;
}

.worry-card {
    background: linear-gradient(
        135deg,
        rgba(130, 100, 255, 0.18),
        rgba(40, 190, 255, 0.08)
    );
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 22px;
    padding: 28px;
    line-height: 1.8;
}

div[data-testid="stMarkdownContainer"] {
    color: #eeeeff;
}

hr {
    border-color: rgba(255,255,255,0.1);
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. 세션 데이터 초기화
# =========================================================

defaults = {
    "selected_menu": "홈",
    "fridge_items": [],
    "recipe_results": None,
    "recipe_ingredients": "",
    "recipe_category": "전체",
    "recipe_max_time": 30,
    "recipe_difficulty": "전체",
    "recipe_extra_request": "",
    "study_seconds": 25 * 60,
    "study_running": False,
    "study_end_time": None,
    "study_subject": "수학",
    "study_sessions": 0,
    "study_total_seconds": 0,
    "worry_text": "",
    "fact_text": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 4. 공통 함수
# =========================================================

def go_to_page(page):
    st.session_state.selected_menu = page


def get_expiry_status(expiry):
    today = date.today()
    remaining = (expiry - today).days

    if remaining < 0:
        return "기간 지남", "urgent"
    elif remaining <= 3:
        return f"D-{remaining}", "urgent"
    else:
        return f"D-{remaining}", "normal"


def format_time(seconds):
    seconds = max(0, int(seconds))
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"


# =========================================================
# 5. AI 레시피 생성 함수
# =========================================================

def generate_ai_recipes(
    ingredients,
    category,
    max_time,
    difficulty,
    extra_request
):
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        raise ValueError(
            "OPENAI_API_KEY를 찾지 못했어. "
            "Streamlit Secrets 설정을 확인해 줘."
        )

    if not api_key:
        raise ValueError("API 키가 비어 있어.")

    client = OpenAI(api_key=api_key)

    instructions = """
너는 사용자의 냉장고 재료를 활용해 현실적이고 맛있는 요리를 추천하는
친절한 한국어 요리 도우미야.

반드시 다음 조건을 지켜.

1. 사용자가 입력한 재료를 최대한 활용해.
2. 입력하지 않은 재료가 꼭 필요하다면 '추가로 필요한 재료'에 표시해.
3. 집에서 구하기 쉬운 재료를 우선 사용해.
4. 조리 시간과 난이도 조건을 지켜.
5. 실제로 따라 할 수 있도록 조리 순서를 구체적으로 작성해.
6. 재료의 양은 1인분 기준으로 안내해.
7. 알레르기나 특별 요청이 있으면 반드시 고려해.
8. 위험한 조리 방법이나 부정확한 식품 안전 정보를 안내하지 마.
9. 레시피는 최소 2개, 최대 3개 추천해.
10. 한국어로 친절하고 읽기 쉽게 작성해.

각 레시피는 다음 형식을 사용해.

## 🍳 요리 이름

**한 줄 소개**

- 예상 조리 시간:
- 난이도:
- 활용하는 재료:

**추가로 필요한 재료**
- 필요한 재료 또는 없음

**조리 순서**
1.
2.
3.

**요리 팁**
- 맛있게 만드는 팁

마지막에는 가장 추천하는 요리 하나를 골라 이유를 설명해.
"""

    user_input = f"""
사용 가능한 재료:
{ingredients}

원하는 음식 종류:
{category}

최대 조리 시간:
{max_time}분

난이도:
{difficulty}

추가 요청:
{extra_request if extra_request else "특별한 요청 없음"}

위 조건에 맞는 요리를 추천해 줘.
"""

    response = client.responses.create(
        model="gpt-5.5",
        instructions=instructions,
        input=user_input
    )

    return response.output_text


# =========================================================
# 6. 사이드바
# =========================================================

with st.sidebar:
    st.markdown("""
    <div style="padding: 15px 5px 25px 5px;">
        <div style="font-size:13px; color:#a99aff; font-weight:800; letter-spacing:3px;">
            YOUR DAILY SPACE
        </div>
        <div style="font-size:29px; font-weight:900; color:white;">
            VIBE CHECK ✨
        </div>
        <div style="font-size:12px; color:#aeb2ca;">
            오늘의 나를 체크하는 작은 공간
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    pages = [
        ("홈", "🏠"),
        ("냉장고 파먹기", "🧊"),
        ("스터디 타이머", "⏳"),
        ("고민 상담소", "💭"),
        ("팩트체크", "🔎")
    ]

    for page, emoji in pages:
        selected = st.session_state.selected_menu == page

        if st.button(
            f"{emoji}  {page}",
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if selected else "secondary"
        ):
            go_to_page(page)
            st.rerun()

    st.markdown("---")

    st.caption("VIBE CHECK")
    st.caption("Make today a little better.")


# =========================================================
# 7. 홈
# =========================================================

if st.session_state.selected_menu == "홈":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">WELCOME TO YOUR SPACE</div>
        <div class="hero-title">오늘의 VIBE CHECK ✨</div>
        <div class="hero-desc">
            오늘도 나만의 속도로, 조금씩 채워 나가면 돼.
        </div>
    </div>
    """, unsafe_allow_html=True)

    today = date.today()

    st.markdown(f"""
    <div style="color:#aaaec8; font-size:14px; margin-bottom:20px;">
        📅 {today.strftime("%Y년 %m월 %d일")}
    </div>
    """, unsafe_allow_html=True)

    fridge_count = len(st.session_state.fridge_items)
    study_count = st.session_state.study_sessions

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">🧊 {fridge_count}</div>
            <div class="stat-label">냉장고 재료</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">⏳ {study_count}</div>
            <div class="stat-label">완료한 공부 세션</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">✨</div>
            <div class="stat-label">오늘도 잘하고 있어</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 오늘의 공간")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:30px;">🧊</div>
            <h3>냉장고 파먹기</h3>
            <p style="color:#b8bad0;">
                냉장고 속 재료를 확인하고 AI에게 새로운 요리를 추천받아 봐.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("냉장고 열어보기 →", key="home_fridge"):
            go_to_page("냉장고 파먹기")
            st.rerun()

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:30px;">⏳</div>
            <h3>스터디 타이머</h3>
            <p style="color:#b8bad0;">
                잠깐의 집중이 쌓여 큰 성취가 되는 시간.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("공부 시작하기 →", key="home_timer"):
            go_to_page("스터디 타이머")
            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:30px;">💭</div>
            <h3>고민 상담소</h3>
            <p style="color:#b8bad0;">
                마음속에 담아둔 생각을 정리해 보는 공간.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("고민 이야기하기 →", key="home_worry"):
            go_to_page("고민 상담소")
            st.rerun()

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:30px;">🔎</div>
            <h3>팩트체크</h3>
            <p style="color:#b8bad0;">
                정보의 출처와 근거를 한 번 더 생각해 보기.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("팩트체크 하러 가기 →", key="home_fact"):
            go_to_page("팩트체크")
            st.rerun()


# =========================================================
# 8. 냉장고 파먹기
# =========================================================

elif st.session_state.selected_menu == "냉장고 파먹기":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">FRIDGE MANAGEMENT</div>
        <div class="hero-title">냉장고 파먹기 🧊</div>
        <div class="hero-desc">
            냉장고 속 재료를 관리하고, AI와 함께 새로운 요리를 만들어 봐.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 냉장고 현황은 이 페이지 안에서만 표시
    st.markdown("### 🧊 냉장고 현황")

    items = st.session_state.fridge_items

    fridge_count = sum(
        1 for item in items if item.get("storage", "냉장") == "냉장"
    )
    freezer_count = sum(
        1 for item in items if item.get("storage", "냉장") == "냉동"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="fridge-door-box">
            <div style="font-size:27px;">🥬 냉장실</div>
            <div style="font-size:34px; font-weight:900;">{fridge_count}개</div>
            <div style="font-size:12px;">신선한 재료를 보관하는 공간</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="freezer-door-box">
            <div style="font-size:27px;">🧊 냉동실</div>
            <div style="font-size:34px; font-weight:900;">{freezer_count}개</div>
            <div style="font-size:12px;">오래 보관할 재료를 모아두는 공간</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 재료 추가
    st.markdown("### ➕ 재료 추가하기")

    with st.form("add_food_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            food_name = st.text_input(
                "재료 이름",
                placeholder="예: 계란, 양파, 우유"
            )

            food_quantity = st.text_input(
                "수량 또는 메모",
                placeholder="예: 3개, 반 봉지"
            )

        with col2:
            food_storage = st.selectbox(
                "보관 위치",
                ["냉장", "냉동"]
            )

            food_expiry = st.date_input(
                "소비기한 또는 확인 날짜",
                value=date.today() + timedelta(days=7)
            )

        add_food = st.form_submit_button(
            "재료 추가하기",
            use_container_width=True
        )

        if add_food:
            if food_name.strip():
                st.session_state.fridge_items.append({
                    "name": food_name.strip(),
                    "quantity": food_quantity.strip() or "수량 미입력",
                    "storage": food_storage,
                    "expiry": food_expiry
                })
                st.success(f"{food_name} 재료를 추가했어!")
                st.rerun()
            else:
                st.warning("재료 이름을 입력해 줘.")

    # 재료 목록
    st.markdown("---")
    st.markdown("### 🥗 보관 중인 재료")

    if not st.session_state.fridge_items:
        st.info("아직 등록된 재료가 없어. 위에서 재료를 추가해 봐!")
    else:
        for i, item in enumerate(st.session_state.fridge_items):

            status_text, status_type = get_expiry_status(item["expiry"])

            badge_class = (
                "urgent-badge"
                if status_type == "urgent"
                else "normal-badge"
            )

            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"""
                <div class="food-card">
                    <div class="food-name">
                        {item["name"]}
                        <span class="{badge_class}">{status_text}</span>
                    </div>
                    <div class="food-detail">
                        {item["storage"]} 보관 · {item["quantity"]}
                        · 날짜: {item["expiry"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("삭제", key=f"delete_food_{i}"):
                    st.session_state.fridge_items.pop(i)
                    st.rerun()

    # AI 레시피
    st.markdown("---")

    st.markdown("""
    <div class="hero">
        <div class="hero-small">AI RECIPE STUDIO</div>
        <div style="font-size:28px; font-weight:900; color:white;">
            오늘은 뭘 먹을까? 🍳
        </div>
        <div class="hero-desc">
            가지고 있는 재료를 입력하면 AI가 그때그때 새로운 레시피를 만들어 줘.
        </div>
    </div>
    """, unsafe_allow_html=True)

    saved_ingredients = ", ".join(
        item["name"] for item in st.session_state.fridge_items
    )

    with st.form("ai_recipe_form"):

        ingredients = st.text_area(
            "사용할 재료",
            value=saved_ingredients,
            placeholder="예: 계란, 양파, 밥, 김치, 참치",
            height=110
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "원하는 음식 종류",
                ["전체", "한식", "양식", "중식", "일식", "간식", "간단식"]
            )

            max_time = st.selectbox(
                "최대 조리 시간",
                [10, 20, 30, 60],
                index=2,
                format_func=lambda x: f"{x}분 이내"
            )

        with col2:
            difficulty = st.selectbox(
                "요리 난이도",
                ["전체", "쉬움", "보통"]
            )

            extra_request = st.text_input(
                "추가 요청",
                placeholder="예: 매콤하게, 설거지 적게, 밥 종류"
            )

        generate_button = st.form_submit_button(
            "✨ AI 레시피 생성하기",
            use_container_width=True
        )

    if generate_button:

        if not ingredients.strip():
            st.warning("사용할 재료를 먼저 입력해 줘.")
        else:
            with st.spinner("AI가 재료를 살펴보고 레시피를 만드는 중이야..."):

                try:
                    result = generate_ai_recipes(
                        ingredients=ingredients,
                        category=category,
                        max_time=max_time,
                        difficulty=difficulty,
                        extra_request=extra_request
                    )

                    st.session_state.recipe_results = result

                except ValueError as e:
                    st.error(str(e))

                except OpenAIError as e:
                    st.error(
                        "AI 요청 중 오류가 발생했어. "
                        "API 사용 가능 여부나 계정 설정을 확인해 줩."
                    )

                except Exception as e:
                    st.error(
                        "예상하지 못한 오류가 발생했어. "
                        "Streamlit 로그를 확인해 줘."
                    )

    if st.session_state.recipe_results:
        st.markdown("---")
        st.markdown("### 🍽️ AI가 추천한 오늘의 레시피")

        st.markdown(
            st.session_state.recipe_results
        )


# =========================================================
# 9. 스터디 타이머
# =========================================================

elif st.session_state.selected_menu == "스터디 타이머":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">FOCUS TIME</div>
        <div class="hero-title">스터디 타이머 ⏳</div>
        <div class="hero-desc">
            지금 이 순간에 집중해 봐. 작은 집중이 모여 큰 성취가 돼.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📚 공부 설정")

    col1, col2 = st.columns(2)

    with col1:
        subject = st.selectbox(
            "공부 과목",
            ["수학", "국어", "영어", "과학", "사회", "기타"],
            index=["수학", "국어", "영어", "과학", "사회", "기타"].index(
                st.session_state.study_subject
            )
        )

    with col2:
        study_minutes = st.selectbox(
            "집중 시간",
            [15, 25, 30, 45, 50, 60],
            index=1
        )

    st.session_state.study_subject = subject

    if not st.session_state.study_running:
        if st.button("⏳ 타이머 시작하기", use_container_width=True):
            st.session_state.study_seconds = study_minutes * 60
            st.session_state.study_end_time = time.time() + (
                study_minutes * 60
            )
            st.session_state.study_running = True
            st.rerun()

    else:
        if st.button("⏸️ 일시정지하기", use_container_width=True):
            remaining = max(
                0,
                int(st.session_state.study_end_time - time.time())
            )
            st.session_state.study_seconds = remaining
            st.session_state.study_running = False
            st.session_state.study_end_time = None
            st.rerun()

    if st.session_state.study_running:

        remaining = max(
            0,
            int(st.session_state.study_end_time - time.time())
        )

        if remaining <= 0:
            st.session_state.study_running = False
            st.session_state.study_end_time = None
            st.session_state.study_sessions += 1
            st.session_state.study_total_seconds += study_minutes * 60
            st.session_state.study_seconds = 0
            st.success("🎉 집중 시간 완료! 정말 수고했어.")
            st.rerun()

        st.markdown(
            f'<div class="timer-display">{format_time(remaining)}</div>',
            unsafe_allow_html=True
        )

        time.sleep(1)
        st.rerun()

    else:
        st.markdown(
            f'<div class="timer-display">{format_time(st.session_state.study_seconds)}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 📊 나의 공부 기록")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "완료한 공부 세션",
            f'{st.session_state.study_sessions}회'
        )

    with col2:
        total_minutes = st.session_state.study_total_seconds // 60
        st.metric(
            "누적 공부 시간",
            f"{total_minutes}분"
        )

    if st.button("타이머 초기화"):
        st.session_state.study_running = False
        st.session_state.study_end_time = None
        st.session_state.study_seconds = 25 * 60
        st.rerun()


# =========================================================
# 10. 고민 상담소
# =========================================================

elif st.session_state.selected_menu == "고민 상담소":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">YOUR LITTLE SAFE SPACE</div>
        <div class="hero-title">고민 상담소 💭</div>
        <div class="hero-desc">
            어떤 생각이든 잠시 내려놓고 정리해 보는 공간이야.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="worry-card">
        <div style="font-size:26px;">☁️ 잠깐 쉬어가도 괜찮아.</div>
        <p style="color:#d4d3ee;">
            모든 일을 완벽하게 해낼 필요는 없어.
            오늘의 마음을 천천히 들여다보자.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 지금 어떤 생각이 들어?")

    worry_text = st.text_area(
        "고민을 자유롭게 적어 봐",
        value=st.session_state.worry_text,
        placeholder="정리되지 않은 생각이어도 괜찮아.",
        height=160
    )

    if st.button("마음 정리하기", use_container_width=True):
        st.session_state.worry_text = worry_text

        if worry_text.strip():
            messages = [
                "지금 느끼는 감정을 억지로 없애려고 하지 않아도 괜찮아. 우선 어떤 마음인지 알아차리는 것부터 시작해 보자.",
                "한 번에 모든 문제를 해결하지 않아도 돼. 지금 할 수 있는 가장 작은 일 하나만 생각해 보자.",
                "네가 느끼는 감정에는 나름의 이유가 있을 수 있어. 스스로를 너무 몰아붙이지 않았으면 좋겠어.",
                "오늘 하루를 버텨낸 것만으로도 의미가 있어. 잠깐 쉬어 가도 괜찮아.",
                "혼자 정리하기 어려운 고민이라면 믿을 수 있는 사람에게 이야기해 보는 것도 좋은 방법이야."
            ]

            st.markdown("---")
            st.markdown("### 💌 오늘의 작은 응원")

            st.markdown(
                f"""
                <div class="worry-card">
                    <div style="font-size:18px; line-height:1.8;">
                        {random.choice(messages)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.caption(
                "이 공간은 생각을 정리하는 데 도움을 주기 위한 곳이야. "
                "힘든 일이 계속된다면 믿을 수 있는 어른에게도 이야기해 줘."
            )

        else:
            st.warning("먼저 마음속 이야기를 적어 줘.")

    if st.button("작성한 고민 지우기"):
        st.session_state.worry_text = ""
        st.rerun()


# =========================================================
# 11. 팩트체크
# =========================================================

elif st.session_state.selected_menu == "팩트체크":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">THINK BEFORE YOU BELIEVE</div>
        <div class="hero-title">팩트체크 🔎</div>
        <div class="hero-desc">
            정보를 그대로 믿기 전에 한 번 더 확인해 보자.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h3>🧠 정보 확인하기</h3>
        <p style="color:#b8bad0;">
            확인하고 싶은 문장이나 정보를 입력하면
            기본적인 확인 포인트를 알려 줄게.
        </p>
    </div>
    """, unsafe_allow_html=True)

    fact_text = st.text_area(
        "확인하고 싶은 내용을 입력해 줘.",
        placeholder="예: 인터넷에서 본 정보나 뉴스의 주장 등을 입력해 봐.",
        height=150
    )

    if st.button("확인 포인트 보기", use_container_width=True):

        if not fact_text.strip():
            st.warning("확인할 내용을 입력해 줘.")

        else:
            st.markdown("---")
            st.markdown("### 🔍 확인할 때 살펴볼 점")

            st.markdown("""
            <div class="glass-card">
                <h4>1. 출처 확인</h4>
                <p style="color:#c5c7dc;">
                    누가 작성했는지, 믿을 만한 기관이나 전문가의 정보인지 확인해 봐.
                </p>
            </div>

            <div class="glass-card">
                <h4>2. 날짜 확인</h4>
                <p style="color:#c5c7dc;">
                    오래된 정보가 현재도 맞는 내용인지 살펴봐.
                </p>
            </div>

            <div class="glass-card">
                <h4>3. 다른 자료와 비교</h4>
                <p style="color:#c5c7dc;">
                    서로 독립적인 여러 출처에서도 같은 내용을 확인할 수 있는지 살펴봐.
                </p>
            </div>

            <div class="glass-card">
                <h4>4. 근거 확인</h4>
                <p style="color:#c5c7dc;">
                    단순한 의견인지, 실제 자료나 연구 결과를 근거로 한 주장인지 구분해 봐.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.info(
                "현재 팩트체크는 정보 확인 방법을 안내하는 보조 기능이야. "
                "입력한 문장의 사실 여부를 실시간으로 검증하는 기능은 아니야."
            )


# =========================================================
# 12. 공통 하단
# =========================================================

st.markdown("---")

st.markdown("""
<div style="
    text-align:center;
    padding:20px;
    color:#777c9e;
    font-size:12px;
">
    ✨ VIBE CHECK · Make today a little better.
</div>
""", unsafe_allow_html=True)
