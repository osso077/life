
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

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E7ECE5 !important;
    color: #536653 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] p {
    color: #536653 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: #71896B !important;
    border: 1px solid #71896B !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] p {
    color: #FFFFFF !important;
}

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

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border: 1px solid #E8EDE5;
    border-radius: 16px;
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
    "profile": {
        "nickname": "",
        "allergies": [],
        "other_allergies": "",
        "avoid_ingredients": ""
    }
}

for key, value in DEFAULT_DATA.items():
    if key not in st.session_state:
        if isinstance(value, (list, dict)):
            st.session_state[key] = value.copy()
        else:
            st.session_state[key] = value

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
PROBE_COOKIE = "fridge_mate_cookie_test"
COOKIE_DAYS = 30


def cookie_controller():
    return CookieController(key="fridge_mate_cookies")


def set_cloud_error(step, message):
    st.session_state.cloud_ready = False
    st.session_state.cloud_error_step = step
    st.session_state.cloud_error = str(message)


def supabase_client():
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    key = str(st.secrets.get("SUPABASE_KEY", "")).strip()

    if not url or not key:
        raise RuntimeError(
            "Secrets의 SUPABASE_URL 또는 SUPABASE_KEY가 비어 있어."
        )

    if url.endswith("/rest/v1") or url.endswith("/auth/v1"):
        raise RuntimeError(
            "SUPABASE_URL은 프로젝트 기본 주소여야 해."
        )

    return create_client(url, key)


def cookie_snapshot():
    result = {
        "component_ok": False,
        "component_cookie": None,
        "request_cookie": None,
        "component_error": ""
    }

    try:
        result["request_cookie"] = st.context.cookies.get(COOKIE_NAME)
    except Exception:
        pass

    try:
        ctrl = cookie_controller()
        result["component_cookie"] = ctrl.get(COOKIE_NAME)
        result["component_ok"] = True
    except Exception as exc:
        result["component_error"] = (
            type(exc).__name__ + ": " + str(exc)
        )

    return result


def read_stored_session():
    snap = cookie_snapshot()
    value = snap["component_cookie"] or snap["request_cookie"]

    if not value:
        return None

    try:
        obj = json.loads(value) if isinstance(value, str) else value

        if (
            not isinstance(obj, dict)
            or not obj.get("access_token")
            or not obj.get("refresh_token")
        ):
            raise ValueError("로그인 쿠키 구조가 올바르지 않아.")

        return {
            "access_token": obj["access_token"],
            "refresh_token": obj["refresh_token"]
        }

    except Exception as exc:
        raise RuntimeError(
            "쿠키에 로그인 정보가 있지만 읽을 수 없어: " + str(exc)
        ) from exc


def write_cookie(name, value):
    cookie_controller().set(
        name,
        value,
        path="/",
        expires=datetime.now() + timedelta(days=COOKIE_DAYS),
        max_age=60 * 60 * 24 * COOKIE_DAYS,
        secure=True,
        same_site="lax",
    )


def persist_session(session):
    try:
        write_cookie(
            COOKIE_NAME,
            json.dumps({
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
            })
        )

        st.session_state.cookie_write_requested = True
        st.session_state.cookie_warning = ""
        return True

    except Exception as exc:
        st.session_state.cookie_warning = (
            "쿠키 저장 요청 실패: " + str(exc)
        )
        return False


def test_cookie_write():
    try:
        token = str(uuid.uuid4())
        write_cookie(PROBE_COOKIE, token)

        st.session_state.probe_expected = token
        st.session_state.probe_result = (
            "테스트 쿠키 저장 요청 완료. 앱을 Ctrl+F5로 새로고침한 뒤 "
            "'테스트 쿠키 읽기'를 눌러줘."
        )

        return True

    except Exception as exc:
        st.session_state.probe_result = (
            "테스트 쿠키 쓰기 요청 실패: " + str(exc)
        )
        return False


def test_cookie_read():
    try:
        expected = st.session_state.get("probe_expected")
        ctrl_value = cookie_controller().get(PROBE_COOKIE)
        request_value = st.context.cookies.get(PROBE_COOKIE)

        if request_value:
            msg = (
                "새 연결 요청에서 테스트 쿠키가 확인됐어. "
                "브라우저 전달 확인 성공."
            )
        elif ctrl_value:
            msg = (
                "쿠키 컴포넌트에서 테스트 쿠키가 확인됐어. "
                "새 브라우저 연결에서도 유지되는지는 추가 확인이 필요해."
            )
        else:
            msg = (
                "테스트 쿠키를 읽지 못했어. "
                "브라우저 쿠키 차단 또는 컴포넌트 로딩 문제일 수 있어."
            )

        if expected and ctrl_value and ctrl_value != expected:
            msg += " (이전 실행의 테스트 쿠키일 수 있어.)"

        st.session_state.probe_result = msg

    except Exception as exc:
        st.session_state.probe_result = (
            "테스트 쿠키 읽기 실패: " + str(exc)
        )


def diagnostic_summary():
    out = {}

    try:
        snap = cookie_snapshot()

        out["쿠키 컴포넌트"] = (
            "호출 가능" if snap["component_ok"] else "호출 실패"
        )

        out["컴포넌트 로그인 쿠키"] = (
            "감지됨" if snap["component_cookie"] else "미감지"
        )

        out["새 연결 요청 쿠키"] = (
            "감지됨" if snap["request_cookie"] else "미감지"
        )

        if snap["component_error"]:
            out["컴포넌트 오류"] = snap["component_error"]

    except Exception as exc:
        out["쿠키 진단"] = type(exc).__name__ + ": " + str(exc)

    out["로그인 세션"] = (
        "서버 세션 있음"
        if st.session_state.get("supabase_session")
        else "없음"
    )

    out["사용자 ID"] = (
        str(st.session_state.get("supabase_user_id"))[:8] + "…"
        if st.session_state.get("supabase_user_id")
        else "없음"
    )

    out["데이터베이스"] = (
        "조회 성공" if st.session_state.cloud_ready else "미연결 / 미검증"
    )

    out["실패 단계"] = st.session_state.get(
        "cloud_error_step", "없음"
    )

    return out


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
            for field in ("expiry", "purchase_date"):
                value = item.get(field)

                if isinstance(value, str):
                    try:
                        item[field] = date.fromisoformat(value)
                    except ValueError:
                        item[field] = date.today()

    st.session_state.data_loaded = True


def connect_cloud(create_new=False):
    st.session_state.cloud_error = ""
    st.session_state.cloud_error_step = ""

    try:
        client = supabase_client()
    except Exception as exc:
        set_cloud_error("Secrets / URL / API 키", exc)
        return False

    existing_session = st.session_state.get("supabase_session")

    try:
        if (
            existing_session is not None
            and st.session_state.get("supabase_user_id")
        ):
            response = client.auth.set_session(
                existing_session.access_token,
                existing_session.refresh_token,
            )
            session = response.session

        else:
            credentials = read_stored_session()

            if credentials:
                response = client.auth.set_session(
                    credentials["access_token"],
                    credentials["refresh_token"]
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

    old_user = st.session_state.get("supabase_user_id")

    if old_user and old_user != session.user.id:
        for name, value in DEFAULT_DATA.items():
            st.session_state[name] = (
                value.copy()
                if isinstance(value, (list, dict))
                else value
            )

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
        st.error(
            "클라우드에 연결되지 않아 저장하지 못했어. "
            "사이드바의 연결 진단을 확인해 줘."
        )
        return False

    try:
        payload = serialize_data()

        client.table("vibe_check_data").upsert({
            "user_id": user_id,
            "data": payload,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="user_id").execute()

        readback = (
            client.table("vibe_check_data")
            .select("data")
            .eq("user_id", user_id)
            .execute()
        )

        if (
            len(readback.data or []) != 1
            or readback.data[0].get("data") != payload
        ):
            raise RuntimeError(
                "저장 후 다시 읽은 데이터가 일치하지 않아."
            )

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


if not st.session_state.get("auth_initial_attempted", False):
    st.session_state.auth_initial_attempted = True
    connect_cloud(create_new=False)


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
        return "날짜 지남"

    if remaining == 0:
        return "오늘 확인"

    return f"D-{remaining}"


def open_page(page):
    st.session_state.selected_menu = page
    st.rerun()


def safe_expiry_days(item):
    try:
        return expiry_days(item.get("expiry", date.today()))
    except Exception:
        return 9999


def usable_fridge_items():
    return [
        x for x in st.session_state.fridge_items
        if safe_expiry_days(x) >= 0
    ]


def urgent_fridge_items():
    return sorted(
        [
            x for x in usable_fridge_items()
            if safe_expiry_days(x) <= 3
        ],
        key=safe_expiry_days
    )


def ingredient_label(item):
    days = safe_expiry_days(item)

    if days < 0:
        status = "날짜 지남 · 확인 필요"
    elif days == 0:
        status = "오늘"
    elif days <= 3:
        status = f"D-{days} · 임박"
    else:
        status = f"D-{days}"

    return (
        f"{item.get('name', '이름 없음')} · "
        f"{item.get('quantity', '수량 미입력')} · {status}"
    )


def show_food_card(item):
    with st.container(border=True):
        left, right = st.columns([4, 1])

        with left:
            st.subheader(f"🥬 {item.get('name', '이름 없음')}")
            st.caption(
                f"{item.get('category', '기타')} · "
                f"{item.get('storage', '보관 정보 없음')} 보관"
            )

        with right:
            st.metric(
                "날짜",
                expiry_status(item.get("expiry", date.today()))
            )

        st.write(f"**수량:** {item.get('quantity', '미입력')}")
        st.write(f"**구매일:** {item.get('purchase_date', '미입력')}")
        st.write(f"**소비기한/확인 날짜:** {item.get('expiry', '미입력')}")

        if item.get("note"):
            st.caption(f"메모: {item['note']}")


# =====================================================
# 6. Groq AI 레시피 생성
# =====================================================

def generate_ai_recipes(
    ingredients,
    category,
    max_time,
    difficulty,
    extra_request,
    strict_selected=False,
    urgent_names=None,
    allow_substitutes=True
):
    # Groq API 키 확인
    api_key = str(
        st.secrets.get("GROQ_API_KEY", "")
    ).strip()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY가 없어. Streamlit Secrets에 "
            "Groq API 키를 등록해 줘."
        )

    profile = st.session_state.get("profile") or {}
    urgent_names = urgent_names or []

    if strict_selected:
        ingredient_rule = """
사용자가 직접 선택한 재료만 보유 재료로 취급한다.
선택하지 않은 냉장고 재료를 임의로 사용하지 않는다.
목록에 없는 식재료를 필수 재료로 추가하지 않는다.
기본 조미료도 보유했다고 가정하지 않는다.
선택 재료만으로 가능한 요리를 우선 창작한다.
"""

    elif allow_substitutes:
        ingredient_rule = """
보유 재료를 최대한 활용한다.
부족한 재료가 있다면 현실적인 대체 재료를 제안한다.
대체 재료는 냉장고에 이미 있는 재료를 우선 탐색한다.
냉장고에 없는 재료는 추가 구매 재료로 명확히 구분한다.
"""

    else:
        ingredient_rule = """
냉장고에 등록된 재료 안에서만 요리를 창작한다.
없는 재료를 필수 재료로 추가하지 않는다.
재료가 부족하면 억지로 요리를 만들지 말고 부족한 점을 설명한다.
"""

    system_prompt = f"""
너는 FRIDGE MATE의 창의적인 AI 셰프다.

너의 역할은 정해진 레시피 목록을 검색하는 것이 아니다.
사용자가 가진 식재료를 직접 분석하고, 재료의 특성과 조합을 바탕으로
새로운 요리를 설계하는 것이다.

[가장 중요한 창작 원칙]

1. 정해진 요리 목록에 재료를 끼워 맞추지 않는다.
2. 재료의 맛, 향, 식감, 수분, 지방, 전분, 단백질 특성을 분석한다.
3. 재료끼리 어떤 맛과 식감으로 어울리는지 스스로 판단한다.
4. 흔히 알려진 요리뿐 아니라 새로운 조합의 요리도 창작할 수 있다.
5. 단, 실제로 조리할 수 있고 맛의 조합이 납득되는 요리여야 한다.
6. 같은 재료로 이름만 바꾼 비슷한 요리를 여러 개 추천하지 않는다.
7. 조리법과 재료 조합이 서로 확실히 다른 요리를 추천한다.
8. 보유 재료를 중심으로 요리를 구성한다.
9. 사용자가 가진 재료의 수량을 고려해 현실적인 분량을 제안한다.
10. 재료가 적으면 가능한 범위 안에서 추천하고, 억지로 개수를 채우지 않는다.

[재료 사용 규칙]

{ingredient_rule}

[소비기한 규칙]

- 소비기한이 임박한 재료를 우선적으로 활용한다.
- 임박 재료: {", ".join(urgent_names) if urgent_names else "없음"}
- 날짜가 지난 재료는 추천에 사용하지 않는다.
- 날짜가 지난 식재료가 안전하다고 추정하지 않는다.
- 실제 식품 안전은 제품 표시와 보관 상태를 확인해야 한다.

[알레르기 및 기피 재료]

- 알레르기 정보와 기피 재료를 반드시 확인한다.
- 알레르기 관련 식재료는 레시피에 넣지 않는다.
- 교차접촉 가능성을 AI가 보장할 수 있다고 말하지 않는다.
- 실제 제품의 원재료와 알레르기 표시 확인을 안내한다.

[조리법 작성 규칙]

- 초보자도 따라 할 수 있도록 조리 순서를 구체적으로 쓴다.
- 재료를 손질하는 방법부터 설명한다.
- 불 세기, 조리 시간, 익힘 정도를 가능한 한 구체적으로 안내한다.
- 육류, 달걀, 해산물 등은 안전하게 충분히 익히도록 한다.
- 재료가 가진 수분과 조리 특성을 고려한다.
- 조리 시간과 난이도 조건을 지킨다.
- 맛을 보완하는 방법과 실패를 줄이는 팁을 알려준다.

[출력 규칙]

한국어로 답변한다.
Markdown 형식으로 보기 좋게 작성한다.
서로 다른 요리 최대 5개를 창작한다.
가능한 요리가 적으면 적은 개수만 추천한다.

각 요리는 다음 형식을 따른다.

## 🍳 요리 이름

요리를 한 문장으로 소개한다.

- 예상 조리 시간:
- 난이도:
- 요리 종류:
- 활용하는 보유 재료:
- 소비기한 임박 재료 활용 여부:

### 💡 이 요리를 생각한 이유
재료의 맛과 식감, 조리 특성을 분석하고 조합이 어울리는 이유를 설명한다.

### 🥬 필요한 재료와 분량
보유 재료와 추가 구매 재료를 구분한다.

### 🔄 대체할 수 있는 재료
가능한 대체 재료와 맛의 차이를 설명한다.

### 👩‍🍳 조리 순서
초보자가 따라 할 수 있도록 순서대로 설명한다.

### ✨ 요리 팁
맛과 식감을 살리는 방법을 설명한다.

### ⚠️ 주의사항
필요한 식품 안전 및 알레르기 확인 사항을 안내한다.

마지막에는 다음 내용을 추가한다.

## 🏆 오늘의 가장 추천하는 요리
가장 추천하는 요리 하나와 그 이유를 설명한다.

## 🧠 냉장고 재료 분석
이번 재료 조합에서 발견한 특징과 활용 아이디어를 정리한다.
"""

    user_prompt = f"""
[사용자가 보유한 식재료와 수량]
{ingredients}

[음식 종류]
{category}

[최대 조리 시간]
{max_time}분

[희망 난이도]
{difficulty}

[추가 요청]
{extra_request or "없음"}

[알레르기]
{", ".join(profile.get("allergies", [])) or "없음"}

[기타 알레르기]
{profile.get("other_allergies") or "없음"}

[피하고 싶은 재료]
{profile.get("avoid_ingredients") or "없음"}

위 정보를 바탕으로 식재료를 분석해 줘.

정해진 레시피를 단순히 나열하지 말고,
재료의 특성을 조합해 만들 수 있는 요리를 직접 창작해 줘.

가능하면 서로 다른 조리 방식과 맛의 방향을 가진 요리를 추천해 줘.
"""

    # Groq의 OpenAI 호환 API 사용
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        timeout=90.0,
        max_retries=1
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.8,
        max_tokens=5000
    )

    result = response.choices[0].message.content

    if not result or not result.strip():
        raise RuntimeError(
            "Groq에서 응답을 받았지만 레시피 내용이 비어 있어."
        )

    return result.strip()


# =====================================================
# 7. 알레르기 및 요리 선호 설정
# =====================================================

def save_profile_from_form():
    profile = st.session_state.get("profile") or {}

    allergy_choices = [
        "난류(계란)", "우유", "땅콩", "호두", "잣", "대두", "밀", "메밀",
        "새우", "게", "고등어", "오징어", "조개류", "복숭아", "토마토",
        "돼지고기", "쇠고기", "닭고기", "아황산류"
    ]

    with st.expander("⚠️ 알레르기·요리 선호 설정", expanded=False):
        with st.form("foraging_profile_form"):
            nickname = st.text_input(
                "닉네임",
                value=profile.get("nickname", "")
            )

            allergies = st.multiselect(
                "알레르기 유발 식재료",
                allergy_choices,
                default=[
                    x for x in profile.get("allergies", [])
                    if x in allergy_choices
                ]
            )

            other_allergies = st.text_input(
                "기타 알레르기",
                value=profile.get("other_allergies", "")
            )

            avoid_ingredients = st.text_area(
                "피하고 싶은 재료",
                value=profile.get("avoid_ingredients", "")
            )

            submitted = st.form_submit_button(
                "요리 안전·선호 설정 저장",
                use_container_width=True
            )

        if submitted:
            st.session_state.profile = {
                "nickname": nickname.strip(),
                "allergies": allergies,
                "other_allergies": other_allergies.strip(),
                "avoid_ingredients": avoid_ingredients.strip()
            }

            save_and_refresh()

        st.caption(
            "AI가 알레르기 안전을 보장할 수는 없어. "
            "실제 제품의 원재료·알레르기 표시와 교차접촉 가능성을 확인해 줘."
        )


# =====================================================
# 8. 메뉴명 이전 버전 호환
# =====================================================

if st.session_state.get("selected_menu") in (
    "대시보드", "AI 레시피", "나의 요리책", "내 정보"
):
    old_menu = st.session_state.get("selected_menu")

    if old_menu == "AI 레시피":
        st.session_state.selected_menu = "냉장고 파먹기"
    else:
        st.session_state.selected_menu = "냉장고 홈"


# =====================================================
# 9. 사이드바
# =====================================================

pages = [
    ("냉장고 홈", "🏠"),
    ("내 냉장고", "🥬"),
    ("냉장고 파먹기", "🍳"),
    ("소비기한 관리", "📅"),
    ("장보기 목록", "🛒")
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

    with st.expander(
        "🔎 저장·로그인 진단",
        expanded=not st.session_state.cloud_ready
    ):
        st.caption("민감한 API 키·로그인 토큰은 표시하지 않아.")

        for label, value in diagnostic_summary().items():
            st.write(f"**{label}:** {value}")

        if st.session_state.get("cloud_error"):
            st.error(
                "연결 오류: " + str(st.session_state.cloud_error)
            )

        if st.session_state.get("cookie_warning"):
            st.warning(st.session_state.cookie_warning)

        st.markdown("**① 브라우저 쿠키 동작 검사**")

        if st.button(
            "테스트 쿠키 저장",
            key="probe_write",
            use_container_width=True
        ):
            test_cookie_write()

        if st.button(
            "테스트 쿠키 읽기",
            key="probe_read",
            use_container_width=True
        ):
            test_cookie_read()

        if st.session_state.get("probe_result"):
            st.info(st.session_state.probe_result)

        st.markdown("**② 로그인 연결 검사**")

        if st.button(
            "기존 로그인 쿠키로 다시 연결",
            key="diag_reconnect",
            use_container_width=True
        ):
            ok = connect_cloud(create_new=False)

            st.session_state.diag_action = (
                "기존 로그인 연결 성공"
                if ok
                else (
                    "연결 실패: "
                    + str(st.session_state.get("cloud_error", "알 수 없음"))
                )
            )

            st.rerun()

        if st.session_state.get("diag_action"):
            st.info(st.session_state.diag_action)

        if st.session_state.get("supabase_user_id"):
            st.caption("현재 연결 사용자 ID (앞 8자리)")
            st.code(
                str(st.session_state.supabase_user_id)[:8] + "…"
            )

        else:
            st.caption(
                "기존 로그인 정보가 없을 때만 새 익명 계정을 시작해 줘."
            )

            if st.button(
                "새 익명 계정 시작",
                key="diag_new",
                use_container_width=True
            ):
                ok = connect_cloud(create_new=True)

                st.session_state.diag_action = (
                    "신규 계정 로그인 성공"
                    if ok
                    else (
                        "생성/연결 실패: "
                        + str(st.session_state.get("cloud_error", "알 수 없음"))
                    )
                )

                st.rerun()

        st.markdown("**③ 클라우드 저장·재조회 검사**")

        if st.button(
            "현재 데이터 저장 후 다시 읽기",
            key="diag_db",
            use_container_width=True,
            disabled=not st.session_state.cloud_ready
        ):
            if save_data():
                st.session_state.db_test_result = (
                    "Supabase 저장 및 재조회 일치 확인 성공"
                )
            else:
                st.session_state.db_test_result = (
                    "저장 검증 실패. 위 오류를 확인해 줘."
                )

        if st.session_state.get("db_test_result"):
            st.info(st.session_state.db_test_result)

    st.caption("Fresh food, better days.")


if not st.session_state.cloud_ready:
    st.warning(
        "클라우드 연결이 확인되지 않았어. 지금 수정한 내용은 저장되지 않을 수 있어. "
        "먼저 사이드바의 '저장·로그인 진단'을 확인해 줘."
    )


# =====================================================
# 10. 냉장고 홈
# =====================================================

if st.session_state.selected_menu == "냉장고 홈":
    items = st.session_state.fridge_items
    groceries = st.session_state.grocery_items
    urgent = urgent_fridge_items()

    expired = [
        x for x in items
        if safe_expiry_days(x) < 0
    ]

    st.title("오늘의 냉장고 🥬")
    st.caption(
        "내가 가진 재료부터 확인하고, 버리는 재료 없이 맛있는 한 끼를 만들어 봐요."
    )
    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🥬 보관 중인 재료", f"{len(items)}개")
    c2.metric("⏰ 3일 이내 확인", f"{len(urgent)}개")
    c3.metric("⚠️ 날짜 확인 필요", f"{len(expired)}개")
    c4.metric("🛒 장보기 항목", f"{len(groceries)}개")

    st.subheader("⏰ 먼저 사용하면 좋은 재료")

    if urgent:
        for item in urgent:
            show_food_card(item)
    else:
        st.success("3일 이내에 확인할 재료가 없어요!")

    if expired:
        st.warning(
            "날짜가 지난 것으로 등록된 재료가 있어. 자동 레시피 추천에서는 제외했어. "
            "날짜가 지났다고 무조건 섭취 가능하거나 불가능하다고 단정할 수 없으니 "
            "제품 표시와 보관 상태를 확인해 줘."
        )

        with st.expander("날짜 확인이 필요한 재료 보기"):
            for item in sorted(expired, key=safe_expiry_days):
                st.write(
                    f"• {item.get('name')} — {item.get('expiry')}"
                )

    st.divider()
    st.subheader("🍳 오늘의 냉장고 파먹기")
    st.write(
        "보유 재료를 바탕으로 만들 수 있는 요리를 AI에게 추천받아 보세요."
    )

    if items:
        if st.button(
            "내 재료로 요리 추천받기 →",
            use_container_width=True
        ):
            open_page("냉장고 파먹기")
    else:
        st.info("먼저 '내 냉장고'에서 재료를 등록해 줘.")

        if st.button(
            "재료 등록하러 가기 →",
            use_container_width=True
        ):
            open_page("내 냉장고")

    st.divider()
    st.subheader("🥗 냉장고 미리보기")

    if items:
        cols = st.columns(4)

        for col, item in zip(cols, items[:8]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"**🥬 {item.get('name', '이름 없음')}**"
                    )
                    st.caption(
                        f"{item.get('storage', '')} · "
                        f"{item.get('quantity', '')}"
                    )
                    st.caption(
                        f"날짜: {item.get('expiry', '미입력')}"
                    )
    else:
        st.info(
            "아직 냉장고가 비어 있어요. 첫 번째 재료를 등록해 보세요!"
        )

    st.subheader("✨ 빠른 이동")

    q1, q2, q3 = st.columns(3)

    with q1:
        if st.button("🥬 내 냉장고 관리", use_container_width=True):
            open_page("내 냉장고")

    with q2:
        if st.button("📅 소비기한 확인", use_container_width=True):
            open_page("소비기한 관리")

    with q3:
        if st.button("🛒 장보기 목록", use_container_width=True):
            open_page("장보기 목록")


# =====================================================
# 11. 내 냉장고
# =====================================================

elif st.session_state.selected_menu == "내 냉장고":
    st.title("내 냉장고 🥬")
    st.caption(
        "가지고 있는 식재료와 수량, 보관 장소, 날짜를 관리해 보세요."
    )

    items = st.session_state.fridge_items

    a, b, c = st.columns(3)

    for col, storage, emoji in zip(
        (a, b, c),
        ("냉장", "냉동", "실온"),
        ("🥗", "🧊", "🥔")
    ):
        col.metric(
            f"{emoji} {storage} 보관",
            f"{sum(1 for x in items if x.get('storage') == storage)}개"
        )

    st.divider()
    st.subheader("➕ 새로운 재료 등록")

    with st.form("add_food_form", clear_on_submit=True):
        left, right = st.columns(2)

        with left:
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

        with right:
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
        or item.get("storage") == filter_storage
    ]

    if not filtered:
        st.info("해당하는 재료가 없어요.")

    else:
        for index, item in filtered:
            with st.container(border=True):
                st.subheader(
                    f"🥬 {item.get('name', '이름 없음')}"
                )

                st.caption(
                    f"{item.get('category', '기타')} · "
                    f"{item.get('storage', '')} 보관"
                )

                st.write(
                    f"**수량:** {item.get('quantity', '미입력')}"
                )

                st.write(
                    f"**구매일:** {item.get('purchase_date', '미입력')}"
                )

                st.write(
                    f"**소비기한/확인 날짜:** {item.get('expiry', '미입력')}"
                )

                if item.get("note"):
                    st.caption(f"메모: {item['note']}")

                st.caption(
                    f"상태: {expiry_status(item.get('expiry', date.today()))}"
                )

                with st.expander("✏️ 수정 / 삭제"):
                    with st.form(f"edit_{item.get('id', index)}"):
                        new_name = st.text_input(
                            "재료 이름",
                            value=item.get("name", "")
                        )

                        categories = [
                            "채소", "과일", "육류", "해산물",
                            "유제품", "곡류·면류", "소스·양념",
                            "가공식품", "기타"
                        ]

                        old_category = item.get("category", "기타")

                        new_category = st.selectbox(
                            "카테고리",
                            categories,
                            index=(
                                categories.index(old_category)
                                if old_category in categories
                                else len(categories) - 1
                            )
                        )

                        new_quantity = st.text_input(
                            "수량",
                            value=item.get("quantity", "")
                        )

                        storages = ["냉장", "냉동", "실온"]
                        old_storage = item.get("storage", "냉장")

                        new_storage = st.selectbox(
                            "보관 장소",
                            storages,
                            index=(
                                storages.index(old_storage)
                                if old_storage in storages
                                else 0
                            )
                        )

                        new_purchase = st.date_input(
                            "구매 날짜",
                            value=(
                                item.get("purchase_date")
                                if isinstance(item.get("purchase_date"), date)
                                else date.today()
                            ),
                            key=f"purchase_{item.get('id', index)}"
                        )

                        new_expiry = st.date_input(
                            "소비기한 또는 확인 날짜",
                            value=(
                                item.get("expiry")
                                if isinstance(item.get("expiry"), date)
                                else date.today()
                            ),
                            key=f"expiry_{item.get('id', index)}"
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
                                "quantity": new_quantity.strip() or "미입력",
                                "storage": new_storage,
                                "purchase_date": new_purchase,
                                "expiry": new_expiry,
                                "note": new_note.strip()
                            })

                            save_and_refresh()

                    if st.button(
                        "🗑️ 재료 삭제",
                        key=f"delete_food_{item.get('id', index)}"
                    ):
                        st.session_state.fridge_items.pop(index)
                        save_and_refresh()


# =====================================================
# 12. 냉장고 파먹기
# =====================================================

elif st.session_state.selected_menu == "냉장고 파먹기":
    st.title("냉장고 파먹기 🍳")
    st.caption(
        "지금 가진 재료를 분석해 새로운 요리를 창작해 봐요."
    )

    all_items = st.session_state.fridge_items
    usable = usable_fridge_items()
    urgent = urgent_fridge_items()

    if not all_items:
        st.info(
            "아직 등록된 재료가 없어. 먼저 내 냉장고에 재료를 추가해 줘."
        )

        if st.button("내 냉장고로 이동 →"):
            open_page("내 냉장고")

    else:
        if urgent:
            st.subheader("⏰ 먼저 활용하면 좋은 재료")
            st.caption(
                "등록된 날짜를 기준으로 3일 이내에 확인할 재료를 우선 표시해."
            )

            cols = st.columns(min(3, len(urgent)))

            for i, item in enumerate(urgent):
                with cols[i % len(cols)]:
                    with st.container(border=True):
                        st.markdown(f"**⏰ {item.get('name')}**")

                        days = safe_expiry_days(item)

                        st.caption(
                            "오늘 확인" if days == 0 else f"D-{days}"
                        )

                        st.caption(
                            f"수량: {item.get('quantity', '미입력')}"
                        )
        else:
            st.success(
                "현재 3일 이내로 등록된 임박 재료는 없어."
            )

        expired = [
            x for x in all_items
            if safe_expiry_days(x) < 0
        ]

        if expired:
            st.warning(
                "날짜가 지난 재료는 자동 추천에서 제외했어. "
                "실제 섭취 여부는 날짜만으로 판단하지 말고 "
                "제품 표시와 보관 상태를 확인해 줘."
            )

        st.divider()
        st.subheader("🥬 어떤 방식으로 요리할까?")

        mode = st.radio(
            "추천 방식",
            [
                "보유 재료로 만들 수 있는 요리 자동 추천",
                "내가 선택한 재료만으로 레시피 만들기"
            ],
            horizontal=False
        )

        labels = {
            ingredient_label(x): x
            for x in usable
        }

        if mode.startswith("보유 재료"):
            selected_items = sorted(
                usable,
                key=lambda x: (
                    0 if safe_expiry_days(x) <= 3 else 1,
                    safe_expiry_days(x)
                )
            )

            st.write(
                "등록된 재료를 자동으로 불러왔어. "
                "소비기한이 임박한 재료를 먼저 활용하도록 요청할게."
            )

            if selected_items:
                st.caption(
                    "사용 후보: "
                    + " · ".join(
                        x.get("name", "")
                        for x in selected_items
                    )
                )
            else:
                st.warning(
                    "추천에 사용할 수 있는 재료가 없어. "
                    "날짜가 지난 재료는 자동으로 제외했어."
                )

        else:
            if labels:
                chosen_labels = st.multiselect(
                    "레시피에 사용할 재료를 선택해 줘",
                    options=list(labels.keys()),
                    help=(
                        "선택하지 않은 재료는 레시피의 보유 재료로 사용하지 않아."
                    )
                )

                selected_items = [
                    labels[x]
                    for x in chosen_labels
                ]
            else:
                selected_items = []
                st.warning(
                    "선택할 수 있는 재료가 없어. "
                    "내 냉장고에 재료를 등록해 줘."
                )

        st.divider()

        with st.form("foraging_recipe_form"):
            st.subheader("🍽️ 요리 조건")

            c1, c2 = st.columns(2)

            with c1:
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

            with c2:
                difficulty = st.selectbox(
                    "난이도",
                    ["전체", "쉬움", "보통"]
                )

                extra_request = st.text_input(
                    "추가 요청",
                    placeholder="예: 매콤하게, 설거지 적게"
                )

            allow_substitutes = st.checkbox(
                "재료가 부족하면 대체 재료도 추천받기",
                value=True,
                help=(
                    "선택 재료만으로 만들기 모드에서는 선택한 재료 외의 "
                    "재료를 필수 재료로 추가하지 않고 대체 아이디어를 "
                    "별도로 알려줘."
                )
            )

            generate = st.form_submit_button(
                "✨ 냉장고 재료로 요리 추천받기",
                use_container_width=True
            )

        if generate:
            if not selected_items:
                st.warning(
                    "먼저 사용할 재료를 선택하거나 냉장고에 재료를 등록해 줘."
                )
            else:
                ingredient_text = "\n".join(
                    f"- {x.get('name')} / "
                    f"수량: {x.get('quantity', '미입력')} / "
                    f"보관: {x.get('storage', '미입력')} / "
                    f"카테고리: {x.get('category', '기타')}"
                    for x in selected_items
                )

                urgent_names = [
                    x.get("name", "")
                    for x in selected_items
                    if safe_expiry_days(x) <= 3
                ]

                strict = mode.startswith("내가 선택한")

                with st.spinner(
                    "AI 셰프가 재료의 맛과 조합을 분석하고 새로운 요리를 창작하는 중이야..."
                ):
                    try:
                        result = generate_ai_recipes(
                            ingredient_text,
                            category,
                            max_time,
                            difficulty,
                            extra_request,
                            strict_selected=strict,
                            urgent_names=urgent_names,
                            allow_substitutes=allow_substitutes
                        )

                        st.session_state.recipe_results = result

                        if st.session_state.cloud_ready:
                            save_data()
                        else:
                            st.warning(
                                "레시피는 생성됐지만 클라우드 연결이 없어 "
                                "저장하지 못했어."
                            )

                    except ValueError as e:
                        st.error(str(e))

                    except OpenAIError as e:
                        st.error("Groq AI 요청에 실패했어.")
                        st.write(
                            "**오류 종류:**",
                            type(e).__name__
                        )
                        st.write(
                            "**오류 내용:**",
                            str(e)
                        )

                        status_code = getattr(e, "status_code", None)
                        error_code = getattr(e, "code", None)
                        request_id = getattr(e, "request_id", None)

                        if status_code:
                            st.write("**HTTP 상태 코드:**", status_code)

                        if error_code:
                            st.write("**오류 코드:**", error_code)

                        if request_id:
                            st.write("**요청 ID:**", request_id)

                        st.caption(
                            "Groq API 키, 모델 이름, 사용량 제한 및 API 상태를 확인해 줘."
                        )

                    except Exception as e:
                        st.error("예상하지 못한 오류가 발생했어.")
                        st.write(
                            "**오류 종류:**",
                            type(e).__name__
                        )
                        st.exception(e)

        if st.session_state.get("recipe_results"):
            st.divider()
            st.subheader("🍽️ 오늘의 냉장고 파먹기 레시피")
            st.markdown(st.session_state.recipe_results)

            st.caption(
                "AI가 제안한 조리법은 참고용이야. 알레르기, 식품 상태, "
                "제품별 조리 안내를 직접 확인하고 충분히 익혀야 하는 "
                "식재료는 안전한 조리 기준을 따라 줘."
            )

            if st.button("결과 지우기", key="clear_recipe_results"):
                st.session_state.recipe_results = None
                save_and_refresh()

    st.divider()
    save_profile_from_form()


# =====================================================
# 13. 소비기한 관리
# =====================================================

elif st.session_state.selected_menu == "소비기한 관리":
    st.title("소비기한 관리 📅")
    st.caption(
        "날짜를 기준으로 재료를 확인하고, 먼저 사용할 재료를 파악해 보세요."
    )

    items = st.session_state.fridge_items

    expired = [
        x for x in items
        if safe_expiry_days(x) < 0
    ]

    today_items = [
        x for x in items
        if safe_expiry_days(x) == 0
    ]

    soon = [
        x for x in items
        if 1 <= safe_expiry_days(x) <= 3
    ]

    later = [
        x for x in items
        if safe_expiry_days(x) > 3
    ]

    cols = st.columns(4)

    for col, title, count in zip(
        cols,
        ("날짜 지남", "오늘", "3일 이내", "여유 있음"),
        (len(expired), len(today_items), len(soon), len(later))
    ):
        col.metric(title, f"{count}개")

    for title, group in (
        ("🔴 날짜 확인이 필요한 재료", expired),
        ("🟠 오늘 확인할 재료", today_items),
        ("🟡 3일 이내 확인할 재료", soon),
        ("🟢 여유 있는 재료", later)
    ):
        st.subheader(title)

        if not group:
            st.caption("해당하는 재료가 없어요.")
        else:
            for item in sorted(group, key=safe_expiry_days):
                show_food_card(item)

    if not items:
        st.info("먼저 내 냉장고에 재료를 등록해 줘.")

    st.caption(
        "날짜 표시는 입력한 날짜를 기준으로 한 참고 정보야. "
        "실제 섭취 가능 여부는 제품 표시, 보관 온도·상태, "
        "개봉 여부 등을 함께 확인해 줘."
    )


# =====================================================
# 14. 장보기 목록
# =====================================================

elif st.session_state.selected_menu == "장보기 목록":
    st.title("장보기 목록 🛒")
    st.caption(
        "냉장고에 부족한 재료와 필요한 식재료를 정리해 보세요."
    )

    with st.form("grocery_form", clear_on_submit=True):
        left, right = st.columns(2)

        with left:
            name = st.text_input(
                "구매할 재료",
                placeholder="예: 우유"
            )

        with right:
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
            st.warning("재료 이름을 입력해 줘.")

    st.divider()

    groceries = st.session_state.grocery_items

    if not groceries:
        st.info("장보기 목록이 비어 있어.")
    else:
        for i, item in enumerate(groceries):
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])

                with c1:
                    checked = st.checkbox(
                        f"{item.get('name')} · "
                        f"{item.get('quantity', '미입력')}",
                        value=bool(item.get("done", False)),
                        key=f"grocery_{item.get('id', i)}"
                    )

                with c2:
                    delete = st.button(
                        "삭제",
                        key=f"delete_grocery_{item.get('id', i)}"
                    )

                if delete:
                    st.session_state.grocery_items.pop(i)
                    save_and_refresh()

                if checked != bool(item.get("done", False)):
                    item["done"] = checked

                    if save_data():
                        st.rerun()

        done_count = sum(
            1 for x in groceries
            if x.get("done")
        )

        st.divider()
        st.progress(done_count / len(groceries))

        st.caption(
            f"{done_count} / {len(groceries)}개 구매 완료"
        )

        if st.button("완료한 항목 모두 삭제"):
            st.session_state.grocery_items = [
                x for x in groceries
                if not x.get("done")
            ]

            save_and_refresh()


# =====================================================
# 15. 하단
# =====================================================

st.divider()
st.caption("🥬 FRIDGE MATE · Fresh food, better days.")
