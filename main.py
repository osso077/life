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
    "profile": {
        "nickname": "",
        "allergies": [],
        "other_allergies": "",
        "avoid_ingredients": ""
    }
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
PROBE_COOKIE = "fridge_mate_cookie_test"
COOKIE_DAYS = 30


def cookie_controller():
    # 기존 컴포넌트 키를 유지하여 이전 버전의 로그인 쿠키와 호환.
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
    """민감정보를 표시하지 않고 쿠키 읽기 경로만 검사한다."""
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
    # 컴포넌트가 첫 렌더에 준비되지 않을 수 있다.
    # None은 곧바로 계정 생성 사유가 아니다.
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
            raise ValueError("로그인 쿠키 구조가 올바르지 않아")

        return {
            "access_token": obj["access_token"],
            "refresh_token": obj["refresh_token"]
        }

    except Exception as exc:
        raise RuntimeError(
            "쿠키에 로그인 정보가 있지만 읽을 수 없어: " + str(exc)
        ) from exc


def write_cookie(name, value):
    # 라이브러리는 expires 기본값이 1일이므로 반드시 별도 명시한다.
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
    """브라우저에 쓰기를 요청한다. 실제 브라우저 저장 성공과는 구별한다."""
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
            "테스트 쿠키 저장 요청 완료. 이제 앱을 Ctrl+F5로 새로고침한 뒤 "
            "'테스트 쿠키 읽기'를 눌러줘. 요청 완료는 실제 저장 성공이 아니야."
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
                "다만 새 브라우저 연결에서도 유지되는지는 아직 확인이 필요해."
            )
        else:
            msg = (
                "테스트 쿠키를 읽지 못했어. "
                "브라우저 쿠키 차단 또는 컴포넌트 로딩 문제일 수 있어."
            )

        if expected and ctrl_value and ctrl_value != expected:
            msg += " (이번 실행 이전의 테스트 쿠키일 수 있어.)"

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

    # 데이터가 없다는 것은 신규 계정이라는 의미이고,
    # 조회 실패와 구분한다.
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
        if (
            existing_session is not None
            and st.session_state.get("supabase_user_id")
        ):
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
                    credentials["access_token"],
                    credentials["refresh_token"]
                )

                session = response.session

            elif create_new:
                # 신규 계정은 명시적으로 사용자가 버튼을 눌렀을 때만 생성.
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
    old_user = st.session_state.get("supabase_user_id")

    if old_user and old_user != session.user.id:
        # 계정이 변경된 경우 기존 사용자의 로컬 데이터 혼입 방지.
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
# 8. 개편 공통 함수
# =====================================================

def safe_expiry_days(item):
    try:
        return expiry_days(item.get("expiry", date.today()))

    except Exception:
        return 9999


def usable_fridge_items():
    """날짜가 지난 재료는 자동 추천 재료에서 제외하고 별도 확인하도록 한다."""
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
            "실제 제품의 원재료·알레르기 표시와 교차접촉 가능성을 반드시 확인해 줘."
        )


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
    try:
        api_key = st.secrets["OPENAI_API_KEY"]

    except Exception:
        raise ValueError(
            "OPENAI_API_KEY가 없어. Streamlit Secrets를 확인해 줘."
        )

    client = OpenAI(api_key=api_key)
    profile = st.session_state.get("profile") or {}
    urgent_names = urgent_names or []

    if strict_selected:
        ingredient_rule = (
            "사용자가 선택한 재료만 사용해. 목록에 없는 식재료를 필수 재료로 추가하지 마. "
            "물, 소금, 후추, 식용유 등 기본 조미료도 사용 가능하다고 가정하지 말고, "
            "필요하면 선택 재료만으로 가능한 조리법을 우선 제안해."
        )

    elif allow_substitutes:
        ingredient_rule = (
            "보유 재료를 최대한 활용하되 부족한 재료가 있으면 대체 재료를 구체적으로 제안해. "
            "대체 재료는 냉장고에 이미 있는 재료를 우선으로 하고, "
            "추가 구매가 필요한 재료는 따로 표시해."
        )

    else:
        ingredient_rule = (
            "보유 재료 안에서만 요리해. 없는 재료를 추가하지 말고, "
            "만들기 어려운 요리는 무리해서 추천하지 말고 부족한 점을 설명해."
        )

    instructions = f"""
너는 친절하고 꼼꼼한 한국어 냉장고 파먹기 요리 도우미야.
목표는 사용자가 이미 가진 식재료를 낭비하지 않고 현실적인 한 끼를 만드는 거야.

반드시 지킬 규칙:
1. {ingredient_rule}
2. 소비기한이 임박한 재료를 우선 활용해. 임박 재료 목록: {", ".join(urgent_names) if urgent_names else "없음"}.
3. 소비기한 또는 확인 날짜가 지난 재료는 안전하다고 가정하거나 추천 재료에 넣지 마.
4. 사용자가 적은 재료와 수량을 기준으로 1인분 분량을 현실적으로 제안해.
5. 조리 시간과 난이도를 지켜.
6. 초보자도 따라 할 수 있도록 순서를 구체적으로 써.
7. 재료가 부족하면 무엇이 부족한지, 무엇으로 대체할 수 있는지, 맛이나 식감이 어떻게 달라지는지 설명해.
8. 알레르기 항목과 기타 알레르기 관련 식재료를 사용하지 않는 방향으로 제안해. 알레르기 안전을 보장한다고 말하지 마.
9. 피하고 싶은 재료도 가능한 한 제외해.
10. 실제 제품의 원재료 표시와 교차접촉 확인이 필요하다고 안내해.
11. 최대 3개의 서로 다른 요리를 추천하고, 가능한 재료 조합이 적으면 억지로 개수를 채우지 마.
12. 모든 답변은 한국어로 작성해.

각 레시피 형식:
## 🍳 요리 이름
한 줄 소개
- 예상 조리 시간:
- 난이도:
- 활용하는 보유 재료:
- 소비기한 임박 재료 활용 여부:

### 필요한 재료와 분량
### 부족한 재료
없으면 '추가 재료 없음'이라고 표시
### 대체 재료 제안
대체 재료가 없으면 그렇게 표시
### 조리 순서
1.
2.
3.
### 요리 팁
### 주의사항

마지막에는 가장 추천하는 요리와 그 이유를 알려줘.
"""

    user_input = f"""
사용 가능한 재료와 수량:
{ingredients}

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


def open_page(page):
    st.session_state.selected_menu = page
    st.rerun()


# 기존 버전에서 저장된 메뉴명이 남아 있어도 새 메뉴로 자연스럽게 이동
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
        "지금 가진 재료를 최대한 활용해, 오늘 만들 수 있는 요리를 찾아봐요."
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
                    f"보관: {x.get('storage', '미입력')}"
                    for x in selected_items
                )

                urgent_names = [
                    x.get("name", "")
                    for x in selected_items
                    if safe_expiry_days(x) <= 3
                ]

                strict = mode.startswith("내가 선택한")

                with st.spinner(
                    "냉장고 속 재료를 살펴보고 레시피를 만드는 중이야..."
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
                        save_data()

                    except ValueError as e:
                        st.error(str(e))

                    except OpenAIError:
                        st.error(
                            "AI 요청에 실패했어. "
                            "OpenAI API 키와 사용 설정을 확인해 줘."
                        )

                    except Exception as e:
                        st.error(f"오류가 발생했어: {e}")

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
