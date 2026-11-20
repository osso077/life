
import streamlit as st
import json
import uuid
from datetime import date, datetime, timedelta, timezone
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
# 2. 디자인 CSS
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
    color: #354A38 !important;
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

[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    min-height: 43px;
    border-radius: 11px;
    font-size: 14px;
    font-weight: 700;
}

/* 선택되지 않은 사이드바 버튼 */
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E7ECE5 !important;
    color: #536653 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] p {
    color: #536653 !important;
}

/* 선택된 사이드바 버튼 */
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: #71896B !important;
    border: 1px solid #71896B !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] p {
    color: #FFFFFF !important;
}

/* 메인 버튼 */
div.stButton > button,
div.stFormSubmitButton > button {
    background: #71896B;
    color: #FFFFFF !important;
    border: 1px solid #71896B;
    border-radius: 11px;
    font-weight: 700;
}

div.stButton > button p,
div.stFormSubmitButton > button p {
    color: #FFFFFF !important;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background: #5E7758;
    border-color: #5E7758;
}

/* 카드 */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border: 1px solid #E8EDE5;
    border-radius: 16px;
}

/* 입력창 */
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

/* 메트릭 */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E9EDE7;
    border-radius: 15px;
    padding: 14px;
}

[data-testid="stMetricValue"] {
    color: #607B59;
}

/* 확장 영역 */
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
</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. 세션 상태 초기화
# =====================================================

DEFAULT_DATA = {
    "fridge_items": [],
    "grocery_items": [],
    "saved_recipes": [],
    "recipe_results": None,
    "profile": {"nickname": "", "allergies": [], "other_allergies": "", "avoid_ingredients": ""}
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
if "supabase_session" not in st.session_state:
    st.session_state.supabase_session = None


# =====================================================
# 4. Supabase 인증 / 세션 복원
# =====================================================

COOKIE_NAME = "fridge_mate_session"
COOKIE_DAYS = 30


_controller = None

def cookie_controller():
    # 한 번의 Streamlit 스크립트 실행에서는 컨트롤러를 하나만 만든다.
    global _controller
    if _controller is None:
        _controller = CookieController(key="fridge_mate_cookies")
    return _controller


def set_cloud_error(step, message):
    st.session_state.cloud_ready = False
    st.session_state.cloud_error_step = step
    st.session_state.cloud_error = str(message)


def supabase_client():
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
    if not url or not key:
        raise RuntimeError("Streamlit Secrets의 SUPABASE_URL 또는 SUPABASE_KEY가 비어 있어.")
    if url.endswith("/rest/v1") or url.endswith("/auth/v1"):
        raise RuntimeError("SUPABASE_URL에는 /rest/v1 또는 /auth/v1을 넣으면 안 돼.")
    return create_client(url, key)


def read_stored_session():
    # st.context.cookies는 새 브라우저 연결 당시의 실제 HTTP 쿠키를 읽는다.
    # 브라우저 컴포넌트 값이 첫 렌더링에서 아직 비어 있을 수 있으므로
    # '쿠키 없음'을 '새 계정 생성 허용'으로 해석하지 않는다.
    value = None
    try:
        value = st.context.cookies.get(COOKIE_NAME)
    except Exception:
        pass
    if not value:
        try:
            value = cookie_controller().get(COOKIE_NAME)
        except Exception as exc:
            st.session_state.cookie_warning = "쿠키 읽기 실패: " + str(exc)
    if not value:
        return None
    try:
        obj = json.loads(value) if isinstance(value, str) else value
        if not isinstance(obj, dict):
            raise ValueError("세션 형식이 올바르지 않아.")
        access = obj.get("access_token")
        refresh = obj.get("refresh_token")
        if not access or not refresh:
            raise ValueError("저장된 토큰이 불완전해.")
        return {"access_token": access, "refresh_token": refresh}
    except Exception as exc:
        raise RuntimeError("저장된 로그인 쿠키를 읽었지만 해석할 수 없어: " + str(exc)) from exc


def persist_session(session):
    # 토큰을 화면에 출력하지 않는다. 저장 실패 시 로그인을 새로 생성하지 않는다.
    try:
        cookie_controller().set(
            COOKIE_NAME,
            json.dumps({
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
            }),
            max_age=60 * 60 * 24 * COOKIE_DAYS,
            secure=True,
            same_site="lax",
        )
        st.session_state.cookie_warning = ""
        st.session_state.cookie_write_requested = True
        return True
    except Exception as exc:
        st.session_state.cookie_warning = (
            "로그인은 됐지만 쿠키 저장 요청이 실패했어: " + str(exc)
        )
        return False


def serialize_data():
    items = []
    for item in st.session_state.fridge_items:
        copied = item.copy()
        for field in ("expiry", "purchase_date"):
            if isinstance(copied.get(field), date):
                copied[field] = copied[field].isoformat()
        items.append(copied)
    return {
        "fridge_items": items,
        "grocery_items": st.session_state.grocery_items,
        "saved_recipes": st.session_state.saved_recipes,
        "recipe_results": st.session_state.recipe_results,
        "profile": st.session_state.profile,
    }


def load_data(client, user_id):
    result = (client.table("vibe_check_data")
              .select("data").eq("user_id", user_id).execute())
    # 데이터가 없다는 것은 신규 계정이라는 의미이고, 조회 실패와 구분한다.
    if result.data:
        saved = result.data[0].get("data") or {}
        for key in DEFAULT_DATA:
            if key in saved:
                st.session_state[key] = saved[key]
        for item in st.session_state.fridge_items:
            for field in ("expiry", "purchase_date"):
                value = item.get(field)
                if isinstance(value, str):
                    try:
                        item[field] = date.fromisoformat(value)
                    except ValueError:
                        item[field] = date.today()
    st.session_state.data_loaded = True


def connect_cloud(create_new=False):
    """기본 동작은 복원만. 신규 계정은 버튼으로 명시적으로 요청할 때만 생성."""
    st.session_state.cloud_error = ""
    st.session_state.cloud_error_step = ""
    try:
        client = supabase_client()
    except Exception as exc:
        set_cloud_error("Secrets / URL / API 키", exc)
        return False

    existing_session = st.session_state.get("supabase_session")
    try:
        if existing_session is not None and st.session_state.get("supabase_user_id"):
            # 동일한 Streamlit 세션에서 버튼 재시도 시에는 새 계정을 만들지 않는다.
            response = client.auth.set_session(
                existing_session.access_token,
                existing_session.refresh_token,
            )
            session = response.session
        else:
            credentials = read_stored_session()
            if credentials:
                response = client.auth.set_session(
                    credentials["access_token"], credentials["refresh_token"]
                )
                session = response.session
            elif create_new:
                response = client.auth.sign_in_anonymously()
                session = response.session
            else:
                set_cloud_error(
                    "로그인 정보 확인",
                    "현재 브라우저에서 로그인 쿠키를 찾지 못했어. "
                    "'기존 로그인 다시 확인'을 먼저 눌러봐. "
                    "새 계정이 정말 필요한 경우에만 계정을 생성해 줘."
                )
                return False
        if session is None or session.user is None:
            raise RuntimeError("로그인 세션을 받지 못했어.")
    except Exception as exc:
        set_cloud_error("로그인 복원 / 생성", exc)
        return False

    # DB 조회가 실패해도 같은 세션을 유지하며, 새 계정을 만들지 않는다.
    st.session_state.supabase_client = client
    st.session_state.supabase_user_id = session.user.id
    st.session_state.supabase_session = session
    persist_session(session)
    try:
        load_data(client, session.user.id)
    except Exception as exc:
        set_cloud_error("테이블 조회 / RLS", exc)
        return False

    st.session_state.cloud_ready = True
    st.session_state.cloud_error = ""
    st.session_state.cloud_error_step = ""
    return True


def save_cookie_session():
    client = st.session_state.get("supabase_client")
    if client is None:
        return False
    try:
        session = client.auth.get_session()
        if session is None:
            return False
        st.session_state.supabase_session = session
        return persist_session(session)
    except Exception as exc:
        st.session_state.cookie_warning = str(exc)
        return False


def save_data():
    client = st.session_state.get("supabase_client")
    user_id = st.session_state.get("supabase_user_id")
    if not st.session_state.cloud_ready or client is None or not user_id:
        st.error("클라우드에 연결되지 않아 저장하지 못했어. 사이드바의 연결 진단을 확인해 줘.")
        return False
    try:
        payload = serialize_data()
        client.table("vibe_check_data").upsert({
            "user_id": user_id,
            "data": payload,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="user_id").execute()
        readback = (client.table("vibe_check_data")
                    .select("data").eq("user_id", user_id).execute())
        if len(readback.data or []) != 1 or readback.data[0].get("data") != payload:
            raise RuntimeError("저장 후 다시 읽은 데이터가 일치하지 않아.")
        save_cookie_session()
        st.session_state.last_save_ok = datetime.now().strftime("%H:%M:%S")
        return True
    except Exception as exc:
        set_cloud_error("저장 / 재조회", exc)
        st.error("저장 확인 실패: " + str(exc))
        return False


def save_and_refresh():
    if save_data():
        st.rerun()


# 최초 접속에서는 브라우저의 쿠키를 복원만 시도하고 새 계정은 생성하지 않는다.
# 새로고침으로 session_state가 초기화되더라도 새 익명 ID가 생기지 않는다.
if not st.session_state.get("auth_initial_attempted", False):
    st.session_state.auth_initial_attempted = True
    connect_cloud(create_new=False)


# =====================================================
# 6. 공통 함수
# =====================================================

def expiry_days(expiry):
    if isinstance(expiry, str):
        expiry = date.fromisoformat(expiry)

    return (expiry - date.today()).days


def expiry_status(expiry):
    remaining = expiry_days(expiry)

    if remaining < 0:
        return "날짜 지남"

    if remaining == 0:
        return "오늘 확인"

    if remaining <= 3:
        return f"D-{remaining}"

    return f"D-{remaining}"


def open_page(page):
    st.session_state.selected_menu = page
    st.rerun()


def show_food_card(item):
    """HTML을 사용하지 않는 재료 카드"""

    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(f"🥬 {item['name']}")
            st.caption(
                f"{item['category']} · {item['storage']} 보관"
            )

        with col2:
            st.metric(
                "날짜",
                expiry_status(item["expiry"])
            )

        st.write(f"**수량:** {item['quantity']}")
        st.write(f"**구매일:** {item['purchase_date']}")
        st.write(f"**확인 날짜:** {item['expiry']}")

        if item.get("note"):
            st.caption(f"메모: {item['note']}")


# =====================================================
# 7. AI 레시피
# =====================================================

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
            "OPENAI_API_KEY가 없어. Streamlit Secrets를 확인해 줘."
        )

    client = OpenAI(api_key=api_key)
    profile = st.session_state.get("profile") or {}

    instructions = """
너는 친절하고 꼼꼼한 한국어 요리 도우미야.

사용자의 냉장고 재료를 최대한 활용해서 현실적인 요리를 추천해.

규칙:
1. 가지고 있는 재료를 최대한 활용한다.
2. 없는 재료는 추가 재료로 구분한다.
3. 조리 시간과 난이도를 지킨다.
4. 재료 양은 1인분 기준으로 알려준다.
5. 초보자도 이해할 수 있게 조리 과정을 자세히 쓴다.
6. 대체 재료가 있으면 함께 알려준다.
7. 알레르기와 특별 요청을 고려한다.
8. 식품 안전을 함부로 단정하지 않는다.
9. 2~3개의 레시피를 추천한다.
10. 모든 답변은 한국어로 작성한다.
11. 아래 알레르기 항목과 관련 소스, 가공식품은 요리에 사용하지 않는다.
12. 피하고 싶은 재료는 알레르기와 별도로 반영하고 가능한 한 제외한다.
13. 각 레시피에 알레르기 주의사항, 실제 제품 라벨과 교차접촉 확인 안내를 넣는다.
14. 알레르기 안전을 보장한다고 단정하지 않는다.

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
알레르기 항목: {", ".join(profile.get("allergies", [])) or "없음"}
기타 알레르기: {profile.get("other_allergies") or "없음"}
피하고 싶은 재료: {profile.get("avoid_ingredients") or "없음"}
"""

    response = client.responses.create(
        model="gpt-5.5",
        instructions=instructions,
        input=user_input
    )

    return response.output_text


# =====================================================
# 8. 사이드바
# =====================================================

pages = [
    ("대시보드", "🏠"),
    ("내 냉장고", "🥬"),
    ("소비기한 관리", "📅"),
    ("AI 레시피", "🍳"),
    ("장보기 목록", "🛒"),
    ("나의 요리책", "📖"),
    ("내 정보", "👤")
]

with st.sidebar:

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

    if not st.session_state.cloud_ready:
        with st.expander("🔎 저장 연결 진단", expanded=True):
            st.write("실패 단계:", st.session_state.get("cloud_error_step", "확인 중"))
            st.write(st.session_state.get("cloud_error", "오류 정보 없음"))
            if st.session_state.get("supabase_user_id"):
                st.info("현재 세션의 사용자 ID는 유지 중이야. 새 계정을 만들지 말고 기존 연결을 다시 확인해 줘.")
                st.code(st.session_state.supabase_user_id)
            if st.button("🔄 기존 로그인 다시 확인", use_container_width=True, key="retry_cloud_diagnostic"):
                if connect_cloud(create_new=False):
                    st.rerun()
                else:
                    st.error("연결 확인 실패: " + str(st.session_state.get("cloud_error", "")))
            st.caption("아직 로그인 기록이 전혀 없는 브라우저에서만 사용해. 기존 쿠키가 있으면 기존 계정을 우선 복원해.")
            if st.button("새 익명 계정 시작하기", use_container_width=True,
                         key="new_anon_diagnostic", disabled=bool(st.session_state.get("supabase_user_id"))):
                if connect_cloud(create_new=True):
                    st.rerun()
                else:
                    st.error("연결 실패: " + str(st.session_state.get("cloud_error", "")))
    else:
        st.caption("클라우드 데이터 조회 완료")
        if st.session_state.get("last_save_ok"):
            st.caption("마지막 저장 확인: " + st.session_state.last_save_ok)
        if st.session_state.get("cookie_warning"):
            st.warning("브라우저 로그인 쿠키에 문제가 있어: " + st.session_state.cookie_warning)
        with st.expander("🔎 연결 검사 / 계정 정보"):
            st.caption("새로고침 전후에 아래 ID가 동일해야 해.")
            st.code(st.session_state.supabase_user_id)
            if st.button("서버 데이터 다시 조회", key="reload_server_test"):
                try:
                    check = (st.session_state.supabase_client.table("vibe_check_data")
                             .select("data").eq("user_id", st.session_state.supabase_user_id).execute())
                    st.success("서버 조회 성공 · 데이터 행: " + str(len(check.data or [])))
                except Exception as exc:
                    st.error("조회 실패: " + str(exc))
            if st.button("로그인 쿠키 다시 저장", key="resave_cookie"):
                if save_cookie_session():
                    st.success("쿠키 저장을 요청했어. Ctrl+F5 후 사용자 ID가 같은지 확인해 줘.")
                else:
                    st.error("쿠키 저장 실패: " + st.session_state.get("cookie_warning", ""))

    st.caption("Fresh food, better days.")


if not st.session_state.cloud_ready:
    st.warning("클라우드 연결이 확인되지 않았어. 지금 수정한 내용은 저장되지 않을 수 있어. 먼저 사이드바의 '저장 연결 진단'을 확인해 줘.")

# =====================================================
# 9. 대시보드
# =====================================================

if st.session_state.selected_menu == "대시보드":

    items = st.session_state.fridge_items
    groceries = st.session_state.grocery_items
    recipes = st.session_state.saved_recipes

    urgent_items = [
        item for item in items
        if expiry_days(item["expiry"]) <= 3
    ]

    st.title("오늘의 냉장고 🥬")
    st.caption("재료를 확인하고 맛있는 한 끼를 계획해 보세요.")

    st.divider()

    st.subheader("Kitchen Overview")

    cols = st.columns(4)

    stats = [
        ("🥬", len(items), "보관 중인 재료"),
        ("⏰", len(urgent_items), "날짜 확인 필요"),
        ("🛒", len(groceries), "장보기 항목"),
        ("📖", len(recipes), "저장한 레시피")
    ]

    for col, (emoji, number, label) in zip(cols, stats):
        with col:
            with st.container(border=True):
                st.subheader(emoji)
                st.metric(label, number)

    st.subheader("⏰ 먼저 확인할 재료")

    if urgent_items:

        for item in sorted(
            urgent_items,
            key=lambda x: expiry_days(x["expiry"])
        ):
            show_food_card(item)

    else:
        st.success("날짜 확인이 필요한 재료가 없어요!")

    st.subheader("✨ Quick Access")

    cols = st.columns(3)

    quick_items = [
        ("🥬", "냉장고 관리", "새로운 재료를 등록해 보세요.", "내 냉장고"),
        ("🍳", "AI 레시피", "오늘의 요리를 추천받아 보세요.", "AI 레시피"),
        ("🛒", "장보기 목록", "필요한 재료를 정리해 보세요.", "장보기 목록")
    ]

    for col, (emoji, title, desc, page) in zip(cols, quick_items):

        with col:
            with st.container(border=True):
                st.subheader(emoji)
                st.markdown(f"**{title}**")
                st.caption(desc)

                if st.button(
                    f"{title} 열기 →",
                    key=f"quick_{page}",
                    use_container_width=True
                ):
                    open_page(page)

    st.subheader("🥗 냉장고 미리보기")

    if items:

        cols = st.columns(4)

        for col, item in zip(cols, items[:4]):

            with col:
                with st.container(border=True):
                    st.subheader(f"🥬 {item['name']}")
                    st.caption(item["storage"])
                    st.write(item["quantity"])

    else:
        st.info("아직 냉장고가 비어 있어요. 첫 번째 재료를 등록해 보세요!")


# =====================================================
# 10. 내 냉장고
# =====================================================

elif st.session_state.selected_menu == "내 냉장고":

    st.title("내 냉장고 🥬")
    st.caption("가지고 있는 식재료를 한눈에 관리해 보세요.")

    items = st.session_state.fridge_items

    cols = st.columns(3)

    for col, storage, emoji in zip(
        cols,
        ["냉장", "냉동", "실온"],
        ["🥗", "🧊", "🥔"]
    ):

        count = sum(
            1 for x in items
            if x["storage"] == storage
        )

        with col:
            st.metric(f"{emoji} {storage} 보관", f"{count}개")

    st.divider()
    st.subheader("➕ 새로운 재료 등록")

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
                placeholder="예: 3개, 500g"
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
    st.subheader("🧺 보관 중인 재료")

    filter_storage = st.selectbox(
        "보관 장소 필터",
        ["전체", "냉장", "냉동", "실온"]
    )

    filtered = [
        (i, item)
        for i, item in enumerate(st.session_state.fridge_items)
        if filter_storage == "전체"
        or item["storage"] == filter_storage
    ]

    if not filtered:

        st.info("해당하는 재료가 없어요.")

    else:

        for i, item in filtered:

            with st.container(border=True):

                st.subheader(f"🥬 {item['name']}")

                st.caption(
                    f"{item['category']} · {item['storage']} 보관"
                )

                st.write(f"**수량:** {item['quantity']}")
                st.write(f"**구매일:** {item['purchase_date']}")
                st.write(f"**확인 날짜:** {item['expiry']}")

                if item.get("note"):
                    st.caption(f"메모: {item['note']}")

                st.caption(
                    f"상태: {expiry_status(item['expiry'])}"
                )

                with st.expander("✏️ 수정 / 삭제"):

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
                            index=["냉장", "냉동", "실온"].index(
                                item["storage"]
                            )
                        )

                        new_purchase = st.date_input(
                            "구매 날짜",
                            value=item["purchase_date"],
                            key=f"purchase_{item['id']}"
                        )

                        new_expiry = st.date_input(
                            "확인 날짜",
                            value=item["expiry"],
                            key=f"expiry_{item['id']}"
                        )

                        new_note = st.text_input(
                            "메모",
                            value=item.get("note", "")
                        )

                        update = st.form_submit_button(
                            "변경사항 저장"
                        )

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
# 11. 소비기한 관리
# =====================================================

elif st.session_state.selected_menu == "소비기한 관리":

    st.title("소비기한 관리 📅")
    st.caption("날짜를 확인하고 식재료를 계획적으로 관리해 보세요.")

    items = st.session_state.fridge_items

    expired = [
        x for x in items
        if expiry_days(x["expiry"]) < 0
    ]

    today_items = [
        x for x in items
        if expiry_days(x["expiry"]) == 0
    ]

    soon = [
        x for x in items
        if 1 <= expiry_days(x["expiry"]) <= 3
    ]

    later = [
        x for x in items
        if expiry_days(x["expiry"]) > 3
    ]

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

        st.subheader(title)

        if not group:
            st.caption("해당하는 재료가 없어요.")
            continue

        for item in sorted(
            group,
            key=lambda x: expiry_days(x["expiry"])
        ):
            show_food_card(item)

    if not items:
        st.info("먼저 냉장고에 재료를 등록해 주세요.")

    st.caption(
        "날짜 표시는 입력한 날짜를 기준으로 한 참고 정보예요. "
        "실제 섭취 가능 여부는 보관 상태와 식품 상태도 함께 확인해 주세요."
    )


# =====================================================
# 12. AI 레시피
# =====================================================

elif st.session_state.selected_menu == "AI 레시피":

    st.title("오늘은 어떤 요리를 할까요? 🍳")
    st.caption("냉장고 속 재료를 활용해 새로운 한 끼를 발견해 보세요.")

    saved_ingredients = ", ".join(
        item["name"]
        for item in st.session_state.fridge_items
    )

    st.divider()
    st.subheader("🥬 요리 조건 설정")

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
        st.subheader("🍽️ 오늘의 추천 레시피")

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
# 13. 장보기 목록
# =====================================================

elif st.session_state.selected_menu == "장보기 목록":

    st.title("장보기 목록 🛒")
    st.caption("필요한 재료를 기록하고 장보기를 계획해 보세요.")

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
    st.subheader("🧺 구매할 재료")

    groceries = st.session_state.grocery_items

    if not groceries:

        st.info("장보기 목록이 비어 있어요.")

    else:

        for i, item in enumerate(groceries):

            with st.container(border=True):

                col1, col2 = st.columns([5, 1])

                with col1:

                    checked = st.checkbox(
                        f"{item['name']} · {item['quantity']}",
                        value=item["done"],
                        key=f"grocery_{item['id']}"
                    )

                with col2:

                    delete = st.button(
                        "삭제",
                        key=f"delete_grocery_{item['id']}"
                    )

                if delete:
                    st.session_state.grocery_items.pop(i)
                    save_and_refresh()

                if checked != item["done"]:
                    item["done"] = checked
                    save_data()

        done_count = sum(
            1 for x in groceries if x["done"]
        )

        st.divider()
        st.progress(done_count / len(groceries))
        st.caption(f"{done_count} / {len(groceries)}개 구매 완료")

        if st.button("완료한 항목 모두 삭제"):

            st.session_state.grocery_items = [
                x for x in groceries if not x["done"]
            ]

            save_and_refresh()


# =====================================================
# 14. 나의 요리책
# =====================================================

elif st.session_state.selected_menu == "나의 요리책":

    st.title("나의 작은 요리책 📖")
    st.caption("마음에 드는 레시피를 모아 나만의 요리책을 만들어 보세요.")

    recipes = st.session_state.saved_recipes

    if not recipes:

        st.info(
            "아직 저장한 레시피가 없어요. "
            "AI 레시피에서 마음에 드는 요리를 저장해 보세요!"
        )

    else:

        st.subheader(f"💚 저장한 레시피 {len(recipes)}개")

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
# 15. 내 정보 (기존 데이터에 profile 필드만 추가)
# =====================================================

elif st.session_state.selected_menu == "내 정보":
    st.title("내 정보 👤")
    st.caption("닉네임과 식재료 선호 정보를 관리해 보세요.")
    profile = st.session_state.profile or {}
    allergy_choices = ["난류(계란)", "우유", "땅콩", "호두", "잣", "대두", "밀", "메밀", "새우", "게", "고등어", "오징어", "조개류", "복숭아", "토마토", "돼지고기", "쇠고기", "닭고기", "아황산류"]
    with st.form("profile_form"):
        nickname = st.text_input("닉네임", value=profile.get("nickname", ""))
        allergies = st.multiselect("알레르기 유발 식재료", allergy_choices,
                                   default=[x for x in profile.get("allergies", []) if x in allergy_choices])
        other_allergies = st.text_input("기타 알레르기", value=profile.get("other_allergies", ""))
        avoid_ingredients = st.text_area("피하고 싶은 재료 (알레르기와 별개)", value=profile.get("avoid_ingredients", ""))
        update_profile = st.form_submit_button("내 정보 저장", use_container_width=True)
    if update_profile:
        st.session_state.profile = {"nickname": nickname.strip(), "allergies": allergies,
                                    "other_allergies": other_allergies.strip(), "avoid_ingredients": avoid_ingredients.strip()}
        save_and_refresh()
    st.info("AI 레시피는 알레르기 안전을 보장할 수 없어. 실제 포장지의 알레르기 표기와 교차접촉 여부를 반드시 확인해 줘.")


# =====================================================
# 16. 하단
# =====================================================

st.divider()

st.caption("🥬 FRIDGE MATE · Fresh food, better days.")
