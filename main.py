
import streamlit as st
import json
from datetime import date, datetime, timedelta
from openai import OpenAI, OpenAIError
from supabase import create_client
from streamlit_cookies_controller import CookieController

# =========================================================
# 1. 기본 설정
# =========================================================

st.set_page_config(
    page_title="FRIDGE MATE",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. 디자인
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(113,75,255,.18), transparent 30%),
        radial-gradient(circle at 90% 85%, rgba(0,220,255,.10), transparent 30%),
        #090b16;
    color: #f5f5ff;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: white !important;
    font-weight: 800 !important;
}

[data-testid="stSidebar"] {
    background: #101323;
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] * {
    color: #f5f5ff !important;
}

.hero {
    padding: 34px;
    border-radius: 25px;
    background: linear-gradient(135deg,
        rgba(118,83,255,.25),
        rgba(24,205,255,.12));
    border: 1px solid rgba(255,255,255,.12);
    margin-bottom: 25px;
}

.hero-small {
    color: #b9b6ff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero-title {
    font-size: 39px;
    font-weight: 900;
    margin-top: 9px;
    color: white;
}

.hero-desc {
    color: #c7c9df;
    font-size: 15px;
    margin-top: 10px;
}

.glass-card {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 19px;
    padding: 20px;
    margin-bottom: 14px;
}

.stat-card {
    background: linear-gradient(145deg,
        rgba(128,101,255,.20),
        rgba(255,255,255,.04));
    border: 1px solid rgba(255,255,255,.12);
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

.food-card {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 16px;
    padding: 17px;
    margin-bottom: 10px;
}

.food-name {
    font-size: 17px;
    font-weight: 800;
    color: white;
}

.food-detail {
    color: #b8bad0;
    font-size: 12px;
    margin-top: 7px;
}

.urgent {
    color: #ff8796;
    background: rgba(255,90,110,.15);
    border: 1px solid rgba(255,90,110,.3);
    border-radius: 20px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 800;
}

.normal {
    color: #76e6bd;
    background: rgba(90,220,170,.12);
    border: 1px solid rgba(90,220,170,.25);
    border-radius: 20px;
    padding: 4px 9px;
    font-size: 11px;
}

.section-label {
    color: #a99aff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

div.stButton > button {
    background: linear-gradient(135deg,#8065ff,#5c9dff);
    color: white !important;
    border: none;
    border-radius: 11px;
    font-weight: 700;
    transition: .2s;
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
.stNumberInput input,
.stDateInput input {
    background: #171b2d !important;
    color: white !important;
    border: 1px solid #414765 !important;
    border-radius: 10px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #171b2d !important;
    color: white !important;
    border-color: #414765 !important;
}

.stRadio label, .stCheckbox label {
    color: #eeeeff !important;
}

hr {
    border-color: rgba(255,255,255,.10);
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. 기본 데이터
# =========================================================

DEFAULT_DATA = {
    "fridge_items": [],
    "grocery_items": [],
    "saved_recipes": [],
    "recipe_results": None,
    "recipe_ingredients": "",
    "recipe_category": "전체",
    "recipe_max_time": 30,
    "recipe_difficulty": "전체",
    "recipe_extra_request": ""
}

for key, value in DEFAULT_DATA.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, list) else value

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

if "cloud_ready" not in st.session_state:
    st.session_state.cloud_ready = False

if "cloud_message" not in st.session_state:
    st.session_state.cloud_message = ""


# =========================================================
# 4. Supabase 연결 및 익명 세션
# =========================================================

def get_cookie_controller():
    return CookieController()


def session_to_cookie(session):
    return json.dumps({
        "access_token": session.access_token,
        "refresh_token": session.refresh_token
    })


def connect_supabase():
    """
    브라우저 쿠키의 세션을 복구하고,
    세션이 없으면 익명 사용자를 생성한다.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

        client = create_client(url, key)
        controller = get_cookie_controller()

        cookie_value = controller.get("fridge_mate_session")
        session = None

        if cookie_value:
            try:
                saved = (
                    json.loads(cookie_value)
                    if isinstance(cookie_value, str)
                    else cookie_value
                )

                access_token = saved.get("access_token")
                refresh_token = saved.get("refresh_token")

                if access_token and refresh_token:
                    response = client.auth.set_session(
                        access_token,
                        refresh_token
                    )
                    session = response.session

            except Exception:
                session = None

        if session is None:
            response = client.auth.sign_in_anonymously()
            session = response.session

        if session is None:
            raise RuntimeError("인증 세션을 만들지 못했어.")

        # 갱신된 토큰도 쿠키에 다시 기록
        controller.set(
            "fridge_mate_session",
            session_to_cookie(session)
        )

        return client, session.user.id

    except Exception as e:
        st.session_state.cloud_message = str(e)
        return None, None


def serialize_data():
    """Supabase JSONB에 저장할 데이터로 변환"""

    items = []

    for item in st.session_state.fridge_items:
        copied = item.copy()

        if isinstance(copied.get("expiry"), date):
            copied["expiry"] = copied["expiry"].isoformat()

        if isinstance(copied.get("purchase_date"), date):
            copied["purchase_date"] = copied["purchase_date"].isoformat()

        items.append(copied)

    return {
        "fridge_items": items,
        "grocery_items": st.session_state.grocery_items,
        "saved_recipes": st.session_state.saved_recipes,
        "recipe_results": st.session_state.recipe_results,
        "recipe_ingredients": st.session_state.recipe_ingredients,
        "recipe_category": st.session_state.recipe_category,
        "recipe_max_time": st.session_state.recipe_max_time,
        "recipe_difficulty": st.session_state.recipe_difficulty,
        "recipe_extra_request": st.session_state.recipe_extra_request
    }


def load_data(client, user_id):
    """로그인한 익명 사용자의 저장 데이터를 불러온다."""

    result = (
        client.table("vibe_check_data")
        .select("data")
        .eq("user_id", user_id)
        .execute()
    )

    if result.data:
        saved = result.data[0].get("data") or {}

        for key in DEFAULT_DATA:
            if key in saved:
                st.session_state[key] = saved[key]

        # 날짜 문자열을 date 객체로 복원
        for item in st.session_state.fridge_items:
            for date_key in ["expiry", "purchase_date"]:
                value = item.get(date_key)

                if isinstance(value, str):
                    try:
                        item[date_key] = date.fromisoformat(value)
                    except ValueError:
                        item[date_key] = date.today()

    st.session_state.data_loaded = True


def save_data():
    """현재 데이터를 Supabase에 저장한다."""

    client = st.session_state.get("supabase_client")
    user_id = st.session_state.get("supabase_user_id")

    if not client or not user_id:
        return False

    try:
        client.table("vibe_check_data").upsert({
            "user_id": user_id,
            "data": serialize_data(),
            "updated_at": datetime.now().isoformat()
        }).execute()

        return True

    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했어: {e}")
        return False


if "supabase_client" not in st.session_state:
    client, user_id = connect_supabase()

    st.session_state.supabase_client = client
    st.session_state.supabase_user_id = user_id

    if client and user_id:
        try:
            load_data(client, user_id)
            st.session_state.cloud_ready = True
        except Exception as e:
            st.session_state.cloud_message = str(e)
            st.session_state.data_loaded = True
    else:
        st.session_state.data_loaded = True


# =========================================================
# 5. 공통 함수
# =========================================================

def go_to_page(page):
    st.session_state.selected_menu = page


def save_and_refresh():
    save_data()
    st.rerun()


def expiry_status(expiry):
    if isinstance(expiry, str):
        expiry = date.fromisoformat(expiry)

    remaining = (expiry - date.today()).days

    if remaining < 0:
        return "날짜 지남", "urgent"
    if remaining == 0:
        return "오늘까지", "urgent"
    if remaining <= 3:
        return f"D-{remaining}", "urgent"

    return f"D-{remaining}", "normal"


def days_until(expiry):
    if isinstance(expiry, str):
        expiry = date.fromisoformat(expiry)

    return (expiry - date.today()).days


def get_recipe_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")

    if not api_key:
        raise ValueError("OPENAI_API_KEY 설정을 확인해 줘.")

    return OpenAI(api_key=api_key)


# =========================================================
# 6. AI 레시피 생성
# =========================================================

def generate_ai_recipes(
    ingredients,
    category,
    max_time,
    difficulty,
    extra_request
):
    client = get_recipe_client()

    instructions = """
너는 냉장고 재료를 활용하는 전문 한국어 요리 도우미야.

다음 규칙을 지켜.

1. 사용자가 가진 재료를 최대한 활용한다.
2. 없는 재료는 추가 재료로 명확하게 구분한다.
3. 조리 시간과 난이도 조건을 지킨다.
4. 1인분 기준으로 재료의 양을 알려준다.
5. 조리 순서를 초보자도 따라 할 수 있게 자세히 설명한다.
6. 대체 가능한 재료가 있으면 알려준다.
7. 알레르기나 특별 요청을 고려한다.
8. 식품 안전을 해치는 방법은 안내하지 않는다.
9. 최소 2개, 최대 3개의 레시피를 추천한다.
10. 한국어로 작성한다.

각 레시피 형식:

## 🍳 요리 이름

한 줄 소개

- 예상 시간:
- 난이도:
- 음식 종류:

### 필요한 재료
- 재료와 분량

### 추가로 필요한 재료
- 재료 또는 없음

### 조리 순서
1.
2.
3.

### 요리 팁
- 팁

마지막에는 가장 추천하는 레시피와 그 이유를 설명한다.
"""

    user_input = f"""
보유 재료: {ingredients}
음식 종류: {category}
최대 조리 시간: {max_time}분
난이도: {difficulty}
추가 요청: {extra_request or "없음"}
"""

    response = client.responses.create(
        model="gpt-5.5",
        instructions=instructions,
        input=user_input
    )

    return response.output_text


# =========================================================
# 7. 사이드바
# =========================================================

pages = [
    "대시보드",
    "내 냉장고",
    "소비기한 관리",
    "AI 레시피",
    "장보기 목록",
    "나의 요리책"
]

emojis = {
    "대시보드": "🏠",
    "내 냉장고": "🥬",
    "소비기한 관리": "⏰",
    "AI 레시피": "🍳",
    "장보기 목록": "🛒",
    "나의 요리책": "📖"
}

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "대시보드"

with st.sidebar:
    st.markdown("""
    <div style="padding:15px 5px 25px 5px;">
        <div style="font-size:12px;color:#a99aff;font-weight:800;letter-spacing:3px;">
            SMART KITCHEN
        </div>
        <div style="font-size:29px;font-weight:900;color:white;">
            FRIDGE MATE 🧊
        </div>
        <div style="font-size:12px;color:#aeb2ca;">
            냉장고를 더 똑똑하게
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    for page in pages:
        if st.button(
            f"{emojis[page]}  {page}",
            key=f"nav_{page}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.selected_menu == page
                else "secondary"
            )
        ):
            go_to_page(page)
            st.rerun()

    st.markdown("---")

    if st.session_state.cloud_ready:
        st.success("☁️ 데이터 저장 연결됨")
    else:
        st.warning("☁️ 클라우드 연결 확인 필요")

    st.caption("FRIDGE MATE")
    st.caption("Your smart kitchen companion.")


# =========================================================
# 8. 대시보드
# =========================================================

if st.session_state.selected_menu == "대시보드":

    items = st.session_state.fridge_items
    groceries = st.session_state.grocery_items

    urgent_items = [
        item for item in items
        if days_until(item["expiry"]) <= 3
    ]

    st.markdown("""
    <div class="hero">
        <div class="hero-small">SMART KITCHEN DASHBOARD</div>
        <div class="hero-title">나의 냉장고 🧊</div>
        <div class="hero-desc">
            오늘은 어떤 재료가 기다리고 있을까?
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<p style='color:#aaaec8;'>📅 {date.today().strftime('%Y년 %m월 %d일')}</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">🥬 {len(items)}</div>
            <div class="stat-label">전체 재료</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">⏰ {len(urgent_items)}</div>
            <div class="stat-label">날짜 확인 필요</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">🛒 {len(groceries)}</div>
            <div class="stat-label">장보기 항목</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">📖 {len(st.session_state.saved_recipes)}</div>
            <div class="stat-label">저장한 레시피</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚨 먼저 확인할 재료")

    if urgent_items:
        for item in sorted(urgent_items, key=lambda x: days_until(x["expiry"])):
            status, _ = expiry_status(item["expiry"])
            st.warning(
                f"**{item['name']}** · {status} · {item['storage']} 보관"
            )
    else:
        st.success("날짜 확인이 필요한 재료가 없어!")

    st.markdown("---")
    st.markdown("### ✨ 빠른 메뉴")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🥬 재료 등록", use_container_width=True):
            go_to_page("내 냉장고")
            st.rerun()

    with col2:
        if st.button("🍳 레시피 추천", use_container_width=True):
            go_to_page("AI 레시피")
            st.rerun()

    with col3:
        if st.button("🛒 장보기 목록", use_container_width=True):
            go_to_page("장보기 목록")
            st.rerun()


# =========================================================
# 9. 내 냉장고
# =========================================================

elif st.session_state.selected_menu == "내 냉장고":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">MY FOOD INVENTORY</div>
        <div class="hero-title">내 냉장고 🥬</div>
        <div class="hero-desc">
            보유한 식재료를 하나씩 기록하고 관리해 보자.
        </div>
    </div>
    """, unsafe_allow_html=True)

    items = st.session_state.fridge_items

    fridge_count = sum(1 for x in items if x["storage"] == "냉장")
    freezer_count = sum(1 for x in items if x["storage"] == "냉동")
    room_count = sum(1 for x in items if x["storage"] == "실온")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">🥗 {fridge_count}</div>
            <div class="stat-label">냉장 보관</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">🧊 {freezer_count}</div>
            <div class="stat-label">냉동 보관</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">🥔 {room_count}</div>
            <div class="stat-label">실온 보관</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ➕ 새로운 재료 등록")

    with st.form("add_food_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "재료 이름 *",
                placeholder="예: 계란"
            )

            category = st.selectbox(
                "카테고리",
                [
                    "채소", "과일", "육류", "해산물",
                    "유제품", "곡류·면류", "소스·양념",
                    "가공식품", "기타"
                ]
            )

            quantity = st.text_input(
                "수량",
                placeholder="예: 3개, 500g, 반 봉지"
            )

        with col2:
            storage = st.selectbox(
                "보관 장소",
                ["냉장", "냉동", "실온"]
            )

            purchase_date = st.date_input(
                "구매 날짜",
                value=date.today()
            )

            expiry = st.date_input(
                "소비기한 또는 확인 날짜",
                value=date.today() + timedelta(days=7)
            )

        note = st.text_input(
            "메모",
            placeholder="예: 개봉함, 요리하고 남은 재료"
        )

        submitted = st.form_submit_button(
            "➕ 냉장고에 추가하기",
            use_container_width=True
        )

        if submitted:
            if not name.strip():
                st.warning("재료 이름을 입력해 줘.")
            else:
                st.session_state.fridge_items.append({
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "name": name.strip(),
                    "category": category,
                    "quantity": quantity.strip() or "미입력",
                    "storage": storage,
                    "purchase_date": purchase_date,
                    "expiry": expiry,
                    "note": note.strip()
                })

                save_and_refresh()

    st.markdown("---")
    st.markdown("### 🥗 보관 중인 재료")

    filter_storage = st.selectbox(
        "보관 장소 필터",
        ["전체", "냉장", "냉동", "실온"]
    )

    filtered_items = [
        (i, item)
        for i, item in enumerate(st.session_state.fridge_items)
        if filter_storage == "전체" or item["storage"] == filter_storage
    ]

    if not filtered_items:
        st.info("아직 등록된 재료가 없어. 위에서 재료를 추가해 봐!")
    else:
        for i, item in filtered_items:
            status, status_type = expiry_status(item["expiry"])

            st.markdown(f"""
            <div class="food-card">
                <div class="food-name">
                    {item['name']}
                    <span class="{status_type}">{status}</span>
                </div>
                <div class="food-detail">
                    {item['category']} · {item['storage']} 보관
                    · 수량: {item['quantity']}
                </div>
                <div class="food-detail">
                    구매: {item['purchase_date']} · 날짜: {item['expiry']}
                </div>
                <div class="food-detail">{item.get('note', '')}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"✏️ {item['name']} 수정 / 삭제"):

                with st.form(f"edit_food_{item['id']}"):

                    new_name = st.text_input(
                        "재료 이름",
                        value=item["name"]
                    )

                    new_category = st.selectbox(
                        "카테고리",
                        [
                            "채소", "과일", "육류", "해산물",
                            "유제품", "곡류·면류", "소스·양념",
                            "가공식품", "기타"
                        ],
                        index=[
                            "채소", "과일", "육류", "해산물",
                            "유제품", "곡류·면류", "소스·양념",
                            "가공식품", "기타"
                        ].index(item.get("category", "기타"))
                    )

                    new_quantity = st.text_input(
                        "수량",
                        value=item["quantity"]
                    )

                    new_storage = st.selectbox(
                        "보관 장소",
                        ["냉장", "냉동", "실온"],
                        index=["냉장", "냉동", "실온"].index(item["storage"])
                    )

                    new_purchase = st.date_input(
                        "구매 날짜",
                        value=item["purchase_date"],
                        key=f"purchase_{item['id']}"
                    )

                    new_expiry = st.date_input(
                        "소비기한 또는 확인 날짜",
                        value=item["expiry"],
                        key=f"expiry_{item['id']}"
                    )

                    new_note = st.text_input(
                        "메모",
                        value=item.get("note", "")
                    )

                    update = st.form_submit_button("변경사항 저장")

                    if update:
                        if not new_name.strip():
                            st.warning("이름을 입력해 줘.")
                        else:
                            item.update({
                                "name": new_name.strip(),
                                "category": new_category,
                                "quantity": new_quantity,
                                "storage": new_storage,
                                "purchase_date": new_purchase,
                                "expiry": new_expiry,
                                "note": new_note
                            })
                            save_and_refresh()

                if st.button(
                    "🗑️ 이 재료 삭제",
                    key=f"remove_{item['id']}"
                ):
                    st.session_state.fridge_items.pop(i)
                    save_and_refresh()


# =========================================================
# 10. 소비기한 관리
# =========================================================

elif st.session_state.selected_menu == "소비기한 관리":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">EXPIRATION TRACKER</div>
        <div class="hero-title">소비기한 관리 ⏰</div>
        <div class="hero-desc">
            날짜를 확인하고 식재료를 계획적으로 관리해 보자.
        </div>
    </div>
    """, unsafe_allow_html=True)

    items = st.session_state.fridge_items

    expired = [x for x in items if days_until(x["expiry"]) < 0]
    today_items = [x for x in items if days_until(x["expiry"]) == 0]
    soon = [x for x in items if 1 <= days_until(x["expiry"]) <= 3]
    later = [x for x in items if days_until(x["expiry"]) > 3]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("날짜 지남", len(expired))
    col2.metric("오늘 확인", len(today_items))
    col3.metric("3일 이내", len(soon))
    col4.metric("여유 있음", len(later))

    st.markdown("---")

    groups = [
        ("🔴 날짜가 지난 재료", expired),
        ("🟠 오늘 확인할 재료", today_items),
        ("🟡 3일 이내 확인할 재료", soon),
        ("🟢 여유 있는 재료", later)
    ]

    if not items:
        st.info("등록된 재료가 없어. 먼저 냉장고에 재료를 추가해 줘.")
    else:
        for title, group in groups:
            st.markdown(f"### {title}")

            if not group:
                st.caption("해당하는 재료가 없어.")
                continue

            for item in sorted(group, key=lambda x: days_until(x["expiry"])):
                status, status_type = expiry_status(item["expiry"])

                st.markdown(f"""
                <div class="food-card">
                    <div class="food-name">
                        {item['name']}
                        <span class="{status_type}">{status}</span>
                    </div>
                    <div class="food-detail">
                        {item['storage']} · {item['quantity']}
                        · 날짜: {item['expiry']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.caption(
        "날짜 표시는 사용자가 입력한 날짜를 기준으로 한 참고 정보야. "
        "실제 섭취 가능 여부는 보관 상태와 식품 상태도 함께 확인해 줘."
    )


# =========================================================
# 11. AI 레시피
# =========================================================

elif st.session_state.selected_menu == "AI 레시피":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">AI RECIPE STUDIO</div>
        <div class="hero-title">오늘은 뭘 먹을까? 🍳</div>
        <div class="hero-desc">
            냉장고 속 재료로 새로운 요리를 발견해 보자.
        </div>
    </div>
    """, unsafe_allow_html=True)

    saved_ingredients = ", ".join(
        item["name"]
        for item in st.session_state.fridge_items
    )

    st.markdown("### 🥬 어떤 재료를 사용할까?")

    with st.form("recipe_form"):

        ingredients = st.text_area(
            "사용할 재료",
            value=saved_ingredients,
            placeholder="예: 계란, 양파, 밥, 김치, 참치",
            height=120
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "음식 종류",
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
                placeholder="예: 매콤하게, 설거지 적게"
            )

        generate = st.form_submit_button(
            "✨ AI 레시피 생성하기",
            use_container_width=True
        )

    if generate:
        if not ingredients.strip():
            st.warning("재료를 먼저 입력해 줘.")
        else:
            with st.spinner("AI 요리사가 레시피를 만드는 중이야..."):
                try:
                    result = generate_ai_recipes(
                        ingredients,
                        category,
                        max_time,
                        difficulty,
                        extra_request
                    )

                    st.session_state.recipe_results = result
                    st.session_state.recipe_ingredients = ingredients
                    st.session_state.recipe_category = category
                    st.session_state.recipe_max_time = max_time
                    st.session_state.recipe_difficulty = difficulty
                    st.session_state.recipe_extra_request = extra_request

                    save_data()

                except ValueError as e:
                    st.error(str(e))
                except OpenAIError:
                    st.error(
                        "AI 요청에 실패했어. API 키와 OpenAI 사용 설정을 확인해 줘."
                    )
                except Exception as e:
                    st.error(f"예상하지 못한 오류가 발생했어: {e}")

    if st.session_state.recipe_results:

        st.markdown("---")
        st.markdown("### 🍽️ 추천 레시피")

        st.markdown(st.session_state.recipe_results)

        st.markdown("---")

        if st.button("💜 이 레시피 모음 저장하기"):
            if st.session_state.recipe_results not in [
                x["content"] for x in st.session_state.saved_recipes
            ]:
                st.session_state.saved_recipes.append({
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "title": f"{st.session_state.recipe_category} 레시피",
                    "content": st.session_state.recipe_results,
                    "created_at": date.today().isoformat()
                })

                save_and_refresh()
            else:
                st.info("이미 저장한 레시피야!")


# =========================================================
# 12. 장보기 목록
# =========================================================

elif st.session_state.selected_menu == "장보기 목록":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">GROCERY CHECKLIST</div>
        <div class="hero-title">장보기 목록 🛒</div>
        <div class="hero-desc">
            필요한 재료를 기록하고 장보기를 간편하게 관리해 보자.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("grocery_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            grocery_name = st.text_input(
                "구매할 재료",
                placeholder="예: 우유"
            )

        with col2:
            grocery_quantity = st.text_input(
                "필요한 수량",
                placeholder="예: 1개, 2팩"
            )

        add_grocery = st.form_submit_button(
            "장보기 목록에 추가",
            use_container_width=True
        )

        if add_grocery:
            if grocery_name.strip():
                st.session_state.grocery_items.append({
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "name": grocery_name.strip(),
                    "quantity": grocery_quantity.strip() or "미입력",
                    "done": False
                })
                save_and_refresh()
            else:
                st.warning("재료 이름을 입력해 줘.")

    st.markdown("---")
    st.markdown("### 🧺 구매할 재료")

    groceries = st.session_state.grocery_items

    if not groceries:
        st.info("장보기 목록이 비어 있어!")
    else:
        for i, item in enumerate(groceries):

            col1, col2, col3 = st.columns([1, 5, 1])

            with col1:
                checked = st.checkbox(
                    "구매 완료",
                    value=item["done"],
                    key=f"grocery_done_{item['id']}"
                )

            with col2:
                if checked:
                    st.markdown(
                        f"~~**{item['name']}**~~ · {item['quantity']}"
                    )
                else:
                    st.markdown(
                        f"**{item['name']}** · {item['quantity']}"
                    )

            with col3:
                if st.button("삭제", key=f"delete_grocery_{item['id']}"):
                    st.session_state.grocery_items.pop(i)
                    save_and_refresh()

            if checked != item["done"]:
                item["done"] = checked
                save_data()

        st.markdown("---")

        done_count = sum(1 for x in groceries if x["done"])
        st.progress(done_count / len(groceries))
        st.caption(f"{done_count} / {len(groceries)}개 구매 완료")

        if st.button("구매 완료 항목 모두 삭제"):
            st.session_state.grocery_items = [
                x for x in groceries if not x["done"]
            ]
            save_and_refresh()


# =========================================================
# 13. 나의 요리책
# =========================================================

elif st.session_state.selected_menu == "나의 요리책":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">MY PERSONAL COOKBOOK</div>
        <div class="hero-title">나의 요리책 📖</div>
        <div class="hero-desc">
            마음에 드는 레시피를 모아 나만의 요리책을 만들어 보자.
        </div>
    </div>
    """, unsafe_allow_html=True)

    recipes = st.session_state.saved_recipes

    if not recipes:
        st.info("아직 저장한 레시피가 없어. AI 레시피에서 마음에 드는 요리를 저장해 봐!")
    else:
        st.markdown(f"### 💜 저장한 레시피 {len(recipes)}개")

        for i, recipe in enumerate(recipes):

            with st.expander(
                f"🍳 {recipe['title']} · {recipe['created_at']}"
            ):
                st.markdown(recipe["content"])

                if st.button(
                    "🗑️ 이 레시피 삭제",
                    key=f"delete_recipe_{recipe['id']}"
                ):
                    st.session_state.saved_recipes.pop(i)
                    save_and_refresh()


# =========================================================
# 14. 공통 하단
# =========================================================

st.markdown("---")

st.markdown("""
<div style="
    text-align:center;
    padding:20px;
    color:#777c9e;
    font-size:12px;
">
    🧊 FRIDGE MATE · Your smart kitchen companion.
</div>
""", unsafe_allow_html=True)
