
import streamlit as st
import json
import html
import uuid
from datetime import date, datetime, timedelta
from openai import OpenAI, OpenAIError
from supabase import create_client
from streamlit_cookies_controller import CookieController


# =====================================================
# 1. 기본 설정
# =====================================================

st.set_page_config(
    page_title="FRIDGE MATE",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. 디자인
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background: #F7F8F6;
    color: #303A32;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    color: #29352D !important;
    font-weight: 800 !important;
}

p {
    color: #68736A;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E8ECE7;
}

[data-testid="stSidebar"] * {
    font-family: 'Pretendard', sans-serif;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #778278;
}

/* 사이드바 버튼 기본 스타일 */
[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    min-height: 43px;
    border-radius: 11px;
    font-size: 14px;
    font-weight: 700;
    transition: all .2s ease;
}

/* 선택되지 않은 버튼 */
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E7ECE5 !important;
    color: #536653 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] p {
    color: #536653 !important;
}

/* 선택된 버튼 */
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: #71896B !important;
    border: 1px solid #71896B !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] p {
    color: #FFFFFF !important;
}

/* 사이드바 버튼 내부 모든 텍스트 */
[data-testid="stSidebar"] div.stButton > button[kind="primary"] *,
[data-testid="stSidebar"] div.stButton > button[kind="primary"] p {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] *,
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] p {
    color: #536653 !important;
}

/* 메인 버튼 */
div.stButton > button {
    background: #71896B;
    color: #FFFFFF !important;
    border: 1px solid #71896B;
    border-radius: 11px;
    font-weight: 700;
}

div.stButton > button p {
    color: #FFFFFF !important;
}

div.stButton > button:hover {
    background: #5E7758;
    border-color: #5E7758;
}

/* 메인 영역 */
.hero {
    background: linear-gradient(120deg, #FFFFFF, #EEF3EA);
    border: 1px solid #E7ECE3;
    border-radius: 24px;
    padding: 34px;
    margin-bottom: 26px;
}

.hero-small {
    color: #80957B;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero-title {
    color: #354A38;
    font-size: 38px;
    font-weight: 900;
    margin-top: 10px;
    line-height: 1.3;
}

.hero-desc {
    color: #788579;
    font-size: 15px;
    margin-top: 10px;
}

.stat-card {
    background: #FFFFFF;
    border: 1px solid #E9EDE7;
    border-radius: 18px;
    padding: 21px;
    min-height: 115px;
    box-shadow: 0 3px 12px rgba(40,60,40,.025);
}

.stat-number {
    color: #617B5B;
    font-size: 30px;
    font-weight: 900;
}

.stat-label {
    color: #879187;
    font-size: 13px;
    margin-top: 5px;
}

.content-card, .food-card, .quick-card {
    background: #FFFFFF;
    border: 1px solid #E9EDE7;
    border-radius: 18px;
    padding: 19px;
    margin-bottom: 13px;
    box-shadow: 0 3px 12px rgba(40,60,40,.025);
}

.food-name {
    color: #39483A;
    font-size: 17px;
    font-weight: 800;
}

.food-detail {
    color: #849087;
    font-size: 12px;
    margin-top: 7px;
}

.badge-urgent {
    display: inline-block;
    background: #FFF0EC;
    color: #C76B55;
    border-radius: 20px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 800;
}

.badge-normal {
    display: inline-block;
    background: #EDF4E9;
    color: #64805D;
    border-radius: 20px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: 800;
}

.quick-icon {
    font-size: 27px;
}

.quick-title {
    font-size: 16px;
    font-weight: 800;
    color: #435644;
    margin-top: 9px;
}

.quick-desc {
    font-size: 12px;
    color: #849087;
    margin-top: 5px;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input {
    background: #FFFFFF !important;
    color: #344237 !important;
    border: 1px solid #DDE5D9 !important;
    border-radius: 10px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #344237 !important;
    border-color: #DDE5D9 !important;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E9EDE7;
    border-radius: 15px;
    padding: 14px;
}

[data-testid="stMetricValue"] {
    color: #607B59;
}

[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid #E8EDE5;
    border-radius: 13px;
}

.stProgress > div > div {
    background: #829A7B;
}

hr {
    border-color: #E8ECE6;
}

footer {
    visibility: hidden;
}

@media (max-width: 768px) {
    .hero {
        padding: 23px;
    }
    .hero-title {
        font-size: 29px;
    }
    .block-container {
        padding-top: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. 세션 상태
# =====================================================

DEFAULT_DATA = {
    "fridge_items": [],
    "grocery_items": [],
    "saved_recipes": [],
    "recipe_results": None
}

for key, value in DEFAULT_DATA.items():
    if key not in st.session_state:
        st.session_state[key] = (
            value.copy() if isinstance(value, list) else value
        )

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "대시보드"

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

if "cloud_ready" not in st.session_state:
    st.session_state.cloud_ready = False

if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = None

if "supabase_user_id" not in st.session_state:
    st.session_state.supabase_user_id = None


# =====================================================
# 4. Supabase 연결 및 데이터 저장
# =====================================================

def get_cookie_controller():
    try:
        return CookieController()
    except Exception:
        return None


def connect_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

        client = create_client(url, key)
        controller = get_cookie_controller()

        if controller is None:
            raise RuntimeError("쿠키 컨트롤러 연결 실패")

        cookie_value = controller.get("fridge_mate_session")
        session = None

        if cookie_value:
            try:
                saved = (
                    json.loads(cookie_value)
                    if isinstance(cookie_value, str)
                    else cookie_value
                )

                response = client.auth.set_session(
                    saved["access_token"],
                    saved["refresh_token"]
                )

                session = response.session

            except Exception:
                session = None

        if session is None:
            response = client.auth.sign_in_anonymously()
            session = response.session

        if session is None:
            raise RuntimeError("익명 로그인에 실패했어.")

        controller.set(
            "fridge_mate_session",
            json.dumps({
                "access_token": session.access_token,
                "refresh_token": session.refresh_token
            })
        )

        return client, session.user.id

    except Exception as e:
        st.session_state.cloud_error = str(e)
        return None, None


def serialize_data():
    items = []

    for item in st.session_state.fridge_items:
        copied = item.copy()

        for key in ["expiry", "purchase_date"]:
            if isinstance(copied.get(key), date):
                copied[key] = copied[key].isoformat()

        items.append(copied)

    return {
        "fridge_items": items,
        "grocery_items": st.session_state.grocery_items,
        "saved_recipes": st.session_state.saved_recipes,
        "recipe_results": st.session_state.recipe_results
    }


def load_data(client, user_id):
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

        for item in st.session_state.fridge_items:
            for key in ["expiry", "purchase_date"]:
                value = item.get(key)

                if isinstance(value, str):
                    try:
                        item[key] = date.fromisoformat(value)
                    except ValueError:
                        item[key] = date.today()

    st.session_state.data_loaded = True


def save_cookie_session():
    try:
        client = st.session_state.supabase_client
        if not client:
            return

        session = client.auth.get_session()

        if session:
            controller = get_cookie_controller()

            if controller:
                controller.set(
                    "fridge_mate_session",
                    json.dumps({
                        "access_token": session.access_token,
                        "refresh_token": session.refresh_token
                    })
                )
    except Exception:
        pass


def save_data():
    client = st.session_state.supabase_client
    user_id = st.session_state.supabase_user_id

    if not client or not user_id:
        return False

    try:
        client.table("vibe_check_data").upsert({
            "user_id": user_id,
            "data": serialize_data(),
            "updated_at": datetime.now().isoformat()
        }).execute()

        save_cookie_session()
        return True

    except Exception as e:
        st.error(f"저장 오류: {e}")
        return False


def save_and_refresh():
    save_data()
    st.rerun()


if not st.session_state.data_loaded:
    client, user_id = connect_supabase()

    st.session_state.supabase_client = client
    st.session_state.supabase_user_id = user_id

    if client and user_id:
        try:
            load_data(client, user_id)
            st.session_state.cloud_ready = True
        except Exception as e:
            st.session_state.cloud_error = str(e)
            st.session_state.data_loaded = True
    else:
        st.session_state.data_loaded = True


# =====================================================
# 5. 공통 함수
# =====================================================

def expiry_days(expiry):
    if isinstance(expiry, str):
        expiry = date.fromisoformat(expiry)

    return (expiry - date.today()).days


def expiry_status(expiry):
    remaining = expiry_days(expiry)

    if remaining < 0:
        return "날짜 지남", "badge-urgent"
    elif remaining == 0:
        return "오늘 확인", "badge-urgent"
    elif remaining <= 3:
        return f"D-{remaining}", "badge-urgent"

    return f"D-{remaining}", "badge-normal"


def safe_text(value):
    return html.escape(str(value))


def open_page(page):
    st.session_state.selected_menu = page
    st.rerun()


# =====================================================
# 6. AI 레시피 생성
# =====================================================

def generate_ai_recipes(
    ingredients,
    category,
    max_time,
    difficulty,
    extra_request
):
    api_key = st.secrets.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY를 확인해 줘.")

    client = OpenAI(api_key=api_key)

    instructions = """
너는 친절하고 꼼꼼한 한국어 요리 도우미야.

사용자의 냉장고 재료를 최대한 활용해서 현실적인 요리를 추천해.

반드시 지켜야 할 규칙:
1. 가진 재료를 최대한 활용한다.
2. 없는 재료는 추가 재료로 구분한다.
3. 조리 시간과 난이도를 지킨다.
4. 재료 양은 1인분 기준으로 알려준다.
5. 초보자도 이해할 수 있게 조리 과정을 설명한다.
6. 대체 재료가 있으면 알려준다.
7. 알레르기와 특별 요청을 고려한다.
8. 식품 안전을 함부로 단정하지 않는다.
9. 2~3개의 레시피를 추천한다.
10. 모든 답변은 한국어로 작성한다.

각 요리 형식:

## 🍳 요리 이름

한 줄 소개

- 예상 조리 시간:
- 난이도:
- 음식 종류:

### 필요한 재료
재료와 분량

### 추가로 필요한 재료
부족한 재료 또는 없음

### 조리 순서
1.
2.
3.

### 요리 팁
맛있게 만드는 팁

마지막에는 가장 추천하는 요리와 이유를 알려줘.
"""

    user_input = f"""
사용 가능한 재료: {ingredients}
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


# =====================================================
# 7. 사이드바
# =====================================================

pages = [
    ("대시보드", "🏠"),
    ("내 냉장고", "🥬"),
    ("소비기한 관리", "📅"),
    ("AI 레시피", "🍳"),
    ("장보기 목록", "🛒"),
    ("나의 요리책", "📖")
]

with st.sidebar:

    # HTML 대신 Streamlit 기본 텍스트 사용
    st.caption("S M A R T   K I T C H E N")
    st.title("FRIDGE MATE 🥬")
    st.caption("나만의 작은 키친 매니저")

    st.divider()

    for page, emoji in pages:
        selected = st.session_state.selected_menu == page

        if st.button(
            f"{emoji}  {page}",
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if selected else "secondary"
        ):
            open_page(page)

    st.divider()

    if st.session_state.cloud_ready:
        st.success("☁️ 클라우드 연결됨")
    else:
        st.warning("☁️ 저장 연결 확인 필요")

    st.caption("Fresh food, better days.")


# =====================================================
# 8. 대시보드
# =====================================================

if st.session_state.selected_menu == "대시보드":

    items = st.session_state.fridge_items
    groceries = st.session_state.grocery_items
    recipes = st.session_state.saved_recipes

    urgent_items = [
        item for item in items
        if expiry_days(item["expiry"]) <= 3
    ]

    st.markdown("""
    <div class="hero">
        <div class="hero-small">WELCOME TO YOUR KITCHEN</div>
        <div class="hero-title">오늘의 냉장고는<br>어떤 모습인가요? 🥬</div>
        <div class="hero-desc">
            재료를 확인하고, 맛있는 한 끼를 계획해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"📅 {date.today().strftime('%Y년 %m월 %d일')}")

    st.markdown("### Kitchen Overview")

    cols = st.columns(4)

    stats = [
        ("🥬", len(items), "보관 중인 재료"),
        ("⏰", len(urgent_items), "날짜 확인 필요"),
        ("🛒", len(groceries), "장보기 항목"),
        ("📖", len(recipes), "저장한 레시피")
    ]

    for col, (emoji, number, label) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:22px;">{emoji}</div>
                <div class="stat-number">{number}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### ⏰ 먼저 확인할 재료")

    if urgent_items:
        for item in sorted(
            urgent_items,
            key=lambda x: expiry_days(x["expiry"])
        ):
            status, badge = expiry_status(item["expiry"])

            st.markdown(f"""
            <div class="food-card">
                <div class="food-name">
                    {safe_text(item['name'])}
                    <span class="{badge}">{status}</span>
                </div>
                <div class="food-detail">
                    {safe_text(item['storage'])} 보관 ·
                    {safe_text(item['quantity'])} ·
                    확인 날짜 {safe_text(item['expiry'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("날짜 확인이 필요한 재료가 없어요!")

    st.markdown("### ✨ Quick Access")

    cols = st.columns(3)

    quick_items = [
        ("🥬", "냉장고 관리", "새로운 재료를 등록해 보세요.", "내 냉장고"),
        ("🍳", "AI 레시피", "오늘의 요리를 추천받아 보세요.", "AI 레시피"),
        ("🛒", "장보기 목록", "필요한 재료를 정리해 보세요.", "장보기 목록")
    ]

    for col, (icon, title, desc, page) in zip(cols, quick_items):
        with col:
            st.markdown(f"""
            <div class="quick-card">
                <div class="quick-icon">{icon}</div>
                <div class="quick-title">{title}</div>
                <div class="quick-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"{title} 열기 →",
                key=f"quick_{page}",
                use_container_width=True
            ):
                open_page(page)

    st.markdown("### 🥗 냉장고 미리보기")

    if items:
        cols = st.columns(4)

        for col, item in zip(cols, items[:4]):
            with col:
                st.markdown(f"""
                <div class="content-card">
                    <div style="font-size:24px;">🥬</div>
                    <div style="font-weight:800;color:#435644;">
                        {safe_text(item['name'])}
                    </div>
                    <div style="font-size:12px;color:#8A9689;">
                        {safe_text(item['storage'])} ·
                        {safe_text(item['quantity'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("아직 냉장고가 비어 있어요. 첫 번째 재료를 등록해 보세요!")


# =====================================================
# 9. 내 냉장고
# =====================================================

elif st.session_state.selected_menu == "내 냉장고":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">MY FOOD INVENTORY</div>
        <div class="hero-title">내 냉장고 🥬</div>
        <div class="hero-desc">
            가지고 있는 식재료를 한눈에 관리해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    items = st.session_state.fridge_items

    cols = st.columns(3)

    for col, storage, emoji in zip(
        cols,
        ["냉장", "냉동", "실온"],
        ["🥗", "🧊", "🥔"]
    ):
        count = sum(1 for x in items if x["storage"] == storage)

        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:24px;">{emoji}</div>
                <div class="stat-number">{count}</div>
                <div class="stat-label">{storage} 보관</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### ➕ 새로운 재료 등록")

    with st.form("add_food_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("재료 이름 *", placeholder="예: 계란")

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
                placeholder="예: 3개, 500g"
            )

        with col2:
            storage = st.selectbox("보관 장소", ["냉장", "냉동", "실온"])

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
            "＋ 냉장고에 추가하기",
            use_container_width=True
        )

        if submitted:
            if not name.strip():
                st.warning("재료 이름을 입력해 주세요.")
            else:
                st.session_state.fridge_items.append({
                    "id": str(uuid.uuid4()),
                    "name": name.strip(),
                    "category": category,
                    "quantity": quantity.strip() or "미입력",
                    "storage": storage,
                    "purchase_date": purchase_date,
                    "expiry": expiry,
                    "note": note.strip()
                })

                save_and_refresh()

    st.divider()
    st.markdown("### 🧺 보관 중인 재료")

    filter_storage = st.selectbox(
        "보관 장소",
        ["전체", "냉장", "냉동", "실온"]
    )

    filtered = [
        (i, item)
        for i, item in enumerate(st.session_state.fridge_items)
        if filter_storage == "전체" or item["storage"] == filter_storage
    ]

    if not filtered:
        st.info("해당하는 재료가 없어요.")
    else:
        for i, item in filtered:

            status, badge = expiry_status(item["expiry"])

            st.markdown(f"""
            <div class="food-card">
                <div class="food-name">
                    {safe_text(item['name'])}
                    <span class="{badge}">{status}</span>
                </div>
                <div class="food-detail">
                    {safe_text(item['category'])} ·
                    {safe_text(item['storage'])} ·
                    {safe_text(item['quantity'])}
                </div>
                <div class="food-detail">
                    구매일 {safe_text(item['purchase_date'])} ·
                    확인 날짜 {safe_text(item['expiry'])}
                </div>
                <div class="food-detail">
                    {safe_text(item.get('note', ''))}
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"✏️ {item['name']} 수정 / 삭제"):

                with st.form(f"edit_{item['id']}"):

                    new_name = st.text_input(
                        "재료 이름",
                        value=item["name"]
                    )

                    categories = [
                        "채소", "과일", "육류", "해산물",
                        "유제품", "곡류·면류", "소스·양념",
                        "가공식품", "기타"
                    ]

                    new_category = st.selectbox(
                        "카테고리",
                        categories,
                        index=categories.index(item["category"])
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
                            st.warning("재료 이름을 입력해 주세요.")
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
                    "🗑️ 재료 삭제",
                    key=f"delete_food_{item['id']}"
                ):
                    st.session_state.fridge_items.pop(i)
                    save_and_refresh()


# =====================================================
# 10. 소비기한 관리
# =====================================================

elif st.session_state.selected_menu == "소비기한 관리":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">EXPIRATION TRACKER</div>
        <div class="hero-title">소비기한 관리 📅</div>
        <div class="hero-desc">
            날짜를 확인하고 식재료를 계획적으로 관리해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    items = st.session_state.fridge_items

    expired = [x for x in items if expiry_days(x["expiry"]) < 0]
    today_items = [x for x in items if expiry_days(x["expiry"]) == 0]
    soon = [x for x in items if 1 <= expiry_days(x["expiry"]) <= 3]
    later = [x for x in items if expiry_days(x["expiry"]) > 3]

    cols = st.columns(4)

    for col, title, count in zip(
        cols,
        ["날짜 지남", "오늘", "3일 이내", "여유 있음"],
        [len(expired), len(today_items), len(soon), len(later)]
    ):
        with col:
            st.metric(title, f"{count}개")

    groups = [
        ("🔴 날짜가 지난 재료", expired),
        ("🟠 오늘 확인할 재료", today_items),
        ("🟡 3일 이내 확인할 재료", soon),
        ("🟢 여유 있는 재료", later)
    ]

    for title, group in groups:
        st.markdown(f"### {title}")

        if not group:
            st.caption("해당하는 재료가 없어요.")
            continue

        for item in sorted(group, key=lambda x: expiry_days(x["expiry"])):
            status, badge = expiry_status(item["expiry"])

            st.markdown(f"""
            <div class="food-card">
                <div class="food-name">
                    {safe_text(item['name'])}
                    <span class="{badge}">{status}</span>
                </div>
                <div class="food-detail">
                    {safe_text(item['storage'])} ·
                    {safe_text(item['quantity'])} ·
                    {safe_text(item['expiry'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if not items:
        st.info("먼저 냉장고에 재료를 등록해 주세요.")

    st.caption(
        "날짜 표시는 입력한 날짜를 기준으로 한 참고 정보예요. "
        "실제 섭취 가능 여부는 보관 상태와 식품 상태도 함께 확인해 주세요."
    )


# =====================================================
# 11. AI 레시피
# =====================================================

elif st.session_state.selected_menu == "AI 레시피":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">AI RECIPE STUDIO</div>
        <div class="hero-title">오늘은 어떤 요리를 할까요? 🍳</div>
        <div class="hero-desc">
            냉장고 속 재료를 활용해 새로운 한 끼를 발견해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    saved_ingredients = ", ".join(
        item["name"] for item in st.session_state.fridge_items
    )

    st.markdown("### 🥬 요리 조건 설정")

    with st.form("recipe_form"):

        ingredients = st.text_area(
            "사용할 재료",
            value=saved_ingredients,
            placeholder="예: 계란, 양파, 밥, 김치",
            height=110
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "음식 종류",
                ["전체", "한식", "양식", "중식", "일식", "간식", "간단식"]
            )

            max_time = st.selectbox(
                "조리 시간",
                [10, 20, 30, 60],
                index=2,
                format_func=lambda x: f"{x}분 이내"
            )

        with col2:
            difficulty = st.selectbox(
                "난이도",
                ["전체", "쉬움", "보통"]
            )

            extra_request = st.text_input(
                "추가 요청",
                placeholder="예: 매콤하게, 설거지 적게"
            )

        generate = st.form_submit_button(
            "✨ 나만의 레시피 만들기",
            use_container_width=True
        )

    if generate:
        if not ingredients.strip():
            st.warning("사용할 재료를 입력해 주세요.")
        else:
            with st.spinner("AI 요리사가 레시피를 만드는 중이에요..."):
                try:
                    result = generate_ai_recipes(
                        ingredients,
                        category,
                        max_time,
                        difficulty,
                        extra_request
                    )

                    st.session_state.recipe_results = result
                    save_data()

                except ValueError as e:
                    st.error(str(e))

                except OpenAIError:
                    st.error(
                        "AI 요청에 실패했어요. OpenAI API 키와 사용 설정을 확인해 주세요."
                    )

                except Exception as e:
                    st.error(f"오류가 발생했어요: {e}")

    if st.session_state.recipe_results:

        st.divider()
        st.markdown("### 🍽️ 오늘의 추천 레시피")

        st.markdown(st.session_state.recipe_results)

        if st.button("💚 이 레시피 모음 저장하기"):

            already_saved = any(
                recipe["content"] == st.session_state.recipe_results
                for recipe in st.session_state.saved_recipes
            )

            if not already_saved:
                st.session_state.saved_recipes.append({
                    "id": str(uuid.uuid4()),
                    "title": "AI 추천 레시피",
                    "content": st.session_state.recipe_results,
                    "created_at": date.today().isoformat()
                })

                save_and_refresh()
            else:
                st.info("이미 저장한 레시피예요!")


# =====================================================
# 12. 장보기 목록
# =====================================================

elif st.session_state.selected_menu == "장보기 목록":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">GROCERY CHECKLIST</div>
        <div class="hero-title">장보기 목록 🛒</div>
        <div class="hero-desc">
            필요한 재료를 기록하고 장보기를 계획해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("grocery_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "구매할 재료",
                placeholder="예: 우유"
            )

        with col2:
            quantity = st.text_input(
                "수량",
                placeholder="예: 1개, 2팩"
            )

        add = st.form_submit_button(
            "＋ 장보기 목록에 추가",
            use_container_width=True
        )

        if add:
            if name.strip():
                st.session_state.grocery_items.append({
                    "id": str(uuid.uuid4()),
                    "name": name.strip(),
                    "quantity": quantity.strip() or "미입력",
                    "done": False
                })

                save_and_refresh()
            else:
                st.warning("재료 이름을 입력해 주세요.")

    st.divider()
    st.markdown("### 🧺 구매할 재료")

    groceries = st.session_state.grocery_items

    if not groceries:
        st.info("장보기 목록이 비어 있어요.")
    else:
        for i, item in enumerate(groceries):

            col1, col2, col3 = st.columns([1, 5, 1])

            with col1:
                checked = st.checkbox(
                    "완료",
                    value=item["done"],
                    key=f"grocery_{item['id']}"
                )

            with col2:
                if checked:
                    st.markdown(
                        f"~~**{safe_text(item['name'])}**~~ · {safe_text(item['quantity'])}"
                    )
                else:
                    st.markdown(
                        f"**{safe_text(item['name'])}** · {safe_text(item['quantity'])}"
                    )

            with col3:
                if st.button(
                    "삭제",
                    key=f"delete_grocery_{item['id']}"
                ):
                    st.session_state.grocery_items.pop(i)
                    save_and_refresh()

            if checked != item["done"]:
                item["done"] = checked
                save_data()

        done_count = sum(1 for x in groceries if x["done"])

        st.divider()
        st.progress(done_count / len(groceries))
        st.caption(f"{done_count} / {len(groceries)}개 구매 완료")

        if st.button("완료한 항목 모두 삭제"):
            st.session_state.grocery_items = [
                x for x in groceries if not x["done"]
            ]
            save_and_refresh()


# =====================================================
# 13. 나의 요리책
# =====================================================

elif st.session_state.selected_menu == "나의 요리책":

    st.markdown("""
    <div class="hero">
        <div class="hero-small">MY PERSONAL COOKBOOK</div>
        <div class="hero-title">나의 작은 요리책 📖</div>
        <div class="hero-desc">
            마음에 드는 레시피를 모아 나만의 요리책을 만들어 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    recipes = st.session_state.saved_recipes

    if not recipes:
        st.info(
            "아직 저장한 레시피가 없어요. "
            "AI 레시피에서 마음에 드는 요리를 저장해 보세요!"
        )
    else:
        st.markdown(f"### 💚 저장한 레시피 {len(recipes)}개")

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


# =====================================================
# 14. 하단
# =====================================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    padding:24px;
    color:#A0AAA0;
    font-size:12px;
">
    🥬 FRIDGE MATE<br>
    Fresh food, better days.
</div>
""", unsafe_allow_html=True)
