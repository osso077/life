import streamlit as st
import json
import uuid
import copy
import hashlib
import secrets
import re
import base64
from html import escape as html_escape
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

/* FRIDGE MATE | 냉장고 그림: Streamlit + HTML/CSS only */
.fm-viz {margin: 6px 0 18px; color:#415244; font-family:inherit;}
.fm-viz * {box-sizing:border-box;}
.fm-viz-layout {display:grid;grid-template-columns:minmax(0,1.6fr) minmax(160px,.75fr);align-items:stretch;gap:18px;max-width:880px;margin:0 auto;}
.fm-appliance {position:relative;border-radius:30px 30px 23px 23px;border:5px solid #d7e2dc;padding:14px 15px 16px;background:linear-gradient(120deg,#fdfefe,#eff5f0 75%,#e8f0eb);box-shadow:0 14px 32px rgba(62,81,62,.10),inset -6px -5px 12px rgba(197,213,201,.34);}
.fm-appliance::before {content:"";position:absolute;top:22%;right:-5px;width:7px;height:24%;border-radius:6px;background:#b0beb7;opacity:.6;}
.fm-appliance-head {display:flex;justify-content:space-between;align-items:center;padding:1px 6px 10px;font-weight:800;font-size:14px;color:#62796a;letter-spacing:.025em;}
.fm-brand-tag {font-weight:700;font-size:10px;letter-spacing:.15em;color:#9baea0;}
.fm-section {position:relative;padding:11px 12px 12px;background:linear-gradient(140deg,#ffffff,#f8fbf9);border:2px solid #dae6de;}
.fm-section.fm-freezer {border-radius:15px 15px 11px 11px;min-height:105px;background:linear-gradient(140deg,#f4fbff,#e8f5fd);border-color:#ccdfeb;margin-bottom:10px;}
.fm-section.fm-chill {border-radius:11px 11px 0 0;border-bottom:0;min-height:102px;}
.fm-section.fm-chill-bottom {border-top:1px dashed #d2dcd5;border-radius:0;min-height:95px;}
.fm-section.fm-crisper {border-radius:0 0 13px 13px;background:linear-gradient(#f7fbef,#edf5e8);border-color:#d8e5ce;min-height:103px;}
.fm-section-heading {display:flex;align-items:center;justify-content:space-between;gap:9px;margin-bottom:10px;color:#5d7564;font-weight:800;font-size:13px;}
.fm-section-count {display:inline-block;color:#7b9681;background:rgba(255,255,255,.75);font-size:11px;border:1px solid #dfebe3;border-radius:99px;padding:1px 7px;white-space:nowrap;}
.fm-food-grid {display:flex;flex-wrap:wrap;gap:6px;align-content:flex-start;}
.fm-food {display:flex;align-items:center;gap:5px;max-width:100%;background:white;border:1px solid #e0ebe0;box-shadow:0 2px 4px rgba(30,50,30,.035);border-radius:12px;padding:6px 8px;line-height:1.25;}
.fm-food.fm-alert {border-color:#efc3be;background:#fff4f2;}
.fm-food.fm-soon {border-color:#f0d6a9;background:#fff9ec;}
.fm-food.fm-risk {border-color:#e2b885;background:#fff9ef;}
.fm-food.fm-risk-high {border-color:#df977d;background:#fff1e9;}
.fm-food.fm-allergy {border-color:#dca6b3;background:#fff1f4;}
.fm-food-emoji {font-size:20px;line-height:1;flex-shrink:0;}
.fm-food-text {display:flex;min-width:0;flex-direction:column;gap:3px;}
.fm-food-name {font-size:12px;color:#324739;font-weight:750;overflow-wrap:anywhere;}
.fm-food-sub {font-size:10px;color:#7a8c80;overflow-wrap:anywhere;}
.fm-food-badge {font-weight:750;color:#a94c40;font-size:10px;}
.fm-food.fm-soon .fm-food-badge {color:#a37727;}
.fm-food.fm-risk .fm-food-badge {color:#9f642b;}
.fm-food.fm-risk-high .fm-food-badge {color:#a34b30;}
.fm-food.fm-allergy .fm-food-badge {color:#a04058;}
.fm-food-empty {font-size:12px;color:#93a59c;padding:7px 3px;}
.fm-more {font-size:11px;font-weight:700;color:#5a7b61;background:#e8f0e7;padding:6px 9px;border-radius:99px;align-self:center;}
.fm-appliance-foot {display:flex;justify-content:space-between;margin:10px 8px 0;color:#96a9a0;font-size:10px;}
.fm-pantry {position:relative;background:linear-gradient(135deg,#f7f0e7,#eee2d4);border:4px solid #e1d3bd;box-shadow:0 12px 25px rgba(94,70,40,.06);border-radius:19px;padding:15px 13px;min-width:0;}
.fm-pantry-header {font-size:14px;color:#8d7559;font-weight:850;padding:4px 3px 12px;}
.fm-pantry .fm-section {background:#fffaf3;border:1px solid #e6dac8;border-bottom:5px solid #d6bea2;min-height:100px;border-radius:10px;margin-bottom:13px;}
.fm-pantry .fm-section-heading {color:#917b61;}
.fm-pantry .fm-section:last-child {margin-bottom:0;}
.fm-viz-note {font-size:11px;color:#718074;text-align:center;margin:10px 0 0;}
.fm-viz-key {display:flex;justify-content:center;flex-wrap:wrap;gap:6px 13px;color:#627669;font-size:11px;margin-top:9px;}
.fm-viz-key span {white-space:nowrap;}
.fm-viz-compact .fm-viz-layout {max-width:720px;gap:13px;}
.fm-viz-compact .fm-appliance {padding:10px 11px 13px;border-width:4px;}
.fm-viz-compact .fm-section {min-height:73px;padding:8px 10px;}
.fm-viz-compact .fm-food {padding:5px 6px;}
.fm-viz-compact .fm-food-emoji {font-size:17px;}
.fm-viz-compact .fm-food-sub {font-size:9px;}
.fm-viz-compact .fm-pantry {padding:10px;}
.fm-viz-compact .fm-pantry .fm-section {min-height:76px;}
.fm-viz-full .fm-food-grid {max-height:220px;overflow-y:auto;scrollbar-width:thin;}
@media (max-width:620px) {
 .fm-viz-layout {grid-template-columns:minmax(0,1fr);max-width:460px;gap:12px;}
 .fm-appliance {padding:10px 11px 13px;}
 .fm-pantry {padding:10px 12px;}
 .fm-pantry .fm-section {min-height:70px;}
 .fm-food-name {font-size:11px;}
 .fm-viz-note {font-size:10px;}
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. 세션 상태 초기화 — 기존 데이터 구조 유지
# =====================================================

DEFAULT_DATA = {
    "fridge_items": [],
    "grocery_items": [],
    "saved_recipes": [],
    "recipe_results": None,
    "profile": {
        "allergies": [],
        "other_allergies": "",
        "avoid_ingredients": ""
    }
}

for key, value in DEFAULT_DATA.items():
    if key not in st.session_state:
        st.session_state[key] = copy.deepcopy(value)

STORAGE_STATE = {
    "selected_menu": "냉장고 홈",
    "cloud_ready": False,
    "cloud_client": None,
    "browser_token": None,
    "browser_hash": None,
    "db_revision": 0,
    "last_saved_data": None,
    "cloud_error": "",
    "cloud_error_step": "",
    "cookie_warning": "",
    "cookie_probe_status": "",
    "last_save_time": "",
    "pending_browser_token": None,
    "last_connect_attempt": None,
    "browser_cookie_verified": False,
}
for key, value in STORAGE_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =====================================================
# 4. 브라우저 식별 및 Supabase 서버 전용 저장
# - 사용자 계정 생성 없이 브라우저별 데이터 저장
# - 브라우저 쿠키는 접근용 무작위 키. DB에는 SHA256 해시만 저장.
# - Secret key는 Streamlit 서버 Secrets에만 보관.
# =====================================================

DEVICE_TABLE = "fridge_mate_browser_data"
COOKIE_NAME = "fridge_mate_browser_key_v1"
PROBE_COOKIE = "fridge_mate_cookie_probe_v1"
COOKIE_DAYS = 180
TOKEN_REGEX = re.compile(r"^[A-Za-z0-9_-]{40,100}$")


def cookie_controller():
    # 한 세션에 같은 컴포넌트 키를 사용해야 정상 복원되기 쉬움.
    return CookieController(key="fridge_mate_browser_cookie_controller")


def write_cookie(name, value):
    cookie_controller().set(
        name,
        value,
        path="/",
        expires=datetime.now() + timedelta(days=COOKIE_DAYS),
        max_age=COOKIE_DAYS * 24 * 60 * 60,
        secure=True,
        same_site="lax",
    )


def cookie_snapshot():
    """쿠키 내용 자체를 UI나 로그에 표시하지 않도록 값의 존재만 확인."""
    output = {"request": None, "component": None, "component_error": ""}
    try:
        output["request"] = st.context.cookies.get(COOKIE_NAME)
    except Exception:
        pass
    try:
        output["component"] = cookie_controller().get(COOKIE_NAME)
    except Exception as exc:
        output["component_error"] = type(exc).__name__
    return output


def read_browser_token():
    snap = cookie_snapshot()
    token = snap["request"] or snap["component"]
    if not token:
        return None
    token = str(token).strip()
    if not TOKEN_REGEX.fullmatch(token):
        st.session_state.cookie_warning = "이 브라우저의 저장 키 형식을 읽지 못했어."
        return None
    return token


def digest_token(token):
    if not isinstance(token, str) or not TOKEN_REGEX.fullmatch(token):
        raise ValueError("브라우저 식별키 형식 오류")
    return hashlib.sha256(("fridge-mate-v1:" + token).encode("utf-8")).hexdigest()


def supabase_client():
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    key = str(st.secrets.get("SUPABASE_SERVER_KEY", "")).strip()
    if not url or not key:
        raise RuntimeError("Streamlit Secrets에 SUPABASE_URL / SUPABASE_SERVER_KEY가 필요해.")
    if not re.fullmatch(r"https://[A-Za-z0-9-]+\.supabase\.co", url):
        raise RuntimeError("SUPABASE_URL은 https://프로젝트ID.supabase.co 형태여야 해.")
    if key.startswith("sb_secret_"):
        pass
    elif key.count(".") == 2:
        try:
            part = key.split(".")[1]
            decoded = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
            role = json.loads(decoded).get("role")
        except Exception as exc:
            raise RuntimeError("서버 전용 API 키 형식이 올바르지 않아.") from exc
        if role != "service_role":
            raise RuntimeError("SUPABASE_SERVER_KEY에는 anon 키가 아닌 service_role 키를 설정해 줘.")
    else:
        raise RuntimeError("SUPABASE_SERVER_KEY에는 서버 전용 Secret key를 설정해 줘.")
    return create_client(url, key)


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return date.today()


def normalized_data(data):
    if not isinstance(data, dict):
        raise ValueError("저장 데이터는 JSON 객체여야 해.")
    cleaned = copy.deepcopy(DEFAULT_DATA)
    for key in ("fridge_items", "grocery_items", "saved_recipes"):
        values = data.get(key, [])
        if not isinstance(values, list) or len(values) > 500:
            raise ValueError(f"{key} 데이터 형식을 확인해 줘 (최대 500개).")
        if any(not isinstance(x, dict) for x in values):
            raise ValueError(f"{key}의 항목 형식이 올바르지 않아.")
        cleaned[key] = copy.deepcopy(values)
        for row in cleaned[key]:
            row.setdefault("id", str(uuid.uuid4()))
    for food in cleaned["fridge_items"]:
        food["purchase_date"] = parse_date(food.get("purchase_date"))
        food["expiry"] = parse_date(food.get("expiry"))
        # 예전 자료에 아래 필드가 없어도 이전 데이터는 그대로 유지돼.
        state = food.get("food_state", "일반")
        food["food_state"] = state if state in ("일반", "개봉", "조리 후 보관") else "일반"
        when = food.get("state_date")
        food["state_date"] = parse_date(when) if when and food["food_state"] != "일반" else None
    result = data.get("recipe_results")
    cleaned["recipe_results"] = result if isinstance(result, str) else None
    profile = data.get("profile")
    if isinstance(profile, dict):
        for field in ("other_allergies", "avoid_ingredients"):
            cleaned["profile"][field] = str(profile.get(field, ""))[:500]
        allergies = profile.get("allergies", [])
        if isinstance(allergies, list):
            cleaned["profile"]["allergies"] = [str(x)[:100] for x in allergies][:50]
    return cleaned


def apply_data(data):
    cleaned = normalized_data(data)
    for key, value in cleaned.items():
        st.session_state[key] = value


def serialize_data():
    payload = {key: copy.deepcopy(st.session_state[key]) for key in DEFAULT_DATA}
    for item in payload["fridge_items"]:
        for field in ("expiry", "purchase_date"):
            item[field] = parse_date(item.get(field)).isoformat()
        item["state_date"] = (
            parse_date(item["state_date"]).isoformat()
            if item.get("state_date") and item.get("food_state") != "일반" else None
        )
    return payload


def fetch_record(client, hashed):
    result = (client.table(DEVICE_TABLE)
              .select("data,revision")
              .eq("device_hash", hashed)
              .limit(1).execute())
    return result.data[0] if result.data else None


def set_cloud_error(stage, exc):
    st.session_state.cloud_error_step = stage
    st.session_state.cloud_error = f"{type(exc).__name__}: {exc}" if isinstance(exc, Exception) else str(exc)


def connect_browser(token):
    """실제 DB 조회 성공 뒤에만 연결 상태를 활성화."""
    try:
        hashed = digest_token(token)
        client = supabase_client()
        row = fetch_record(client, hashed)
        if row is None:
            # 새 방문 시에만 새 행 작성. 기존 데이터는 덮어쓰지 않음.
            try:
                client.table(DEVICE_TABLE).insert({
                    "device_hash": hashed,
                    "data": copy.deepcopy(DEFAULT_DATA),
                    "revision": 0,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).execute()
            except Exception:
                # 다른 탭에서 동시에 만들었을 수 있으므로 먼저 재조회
                if fetch_record(client, hashed) is None:
                    raise
            row = fetch_record(client, hashed)
        if row is None:
            raise RuntimeError("Supabase에 브라우저 데이터 행을 만들거나 불러오지 못했어.")
        cleaned = normalized_data(row.get("data"))
        for field, value in cleaned.items():
            st.session_state[field] = value
        st.session_state.cloud_client = client
        st.session_state.browser_token = token
        st.session_state.browser_hash = hashed
        st.session_state.db_revision = int(row.get("revision", 0))
        st.session_state.last_saved_data = serialize_data()
        st.session_state.cloud_ready = True
        st.session_state.cloud_error = ""
        st.session_state.cloud_error_step = ""
        return True
    except Exception as exc:
        st.session_state.cloud_ready = False
        set_cloud_error("브라우저 저장 DB 조회", exc)
        return False


def rollback_to_saved():
    snapshot = st.session_state.get("last_saved_data")
    if snapshot is not None:
        apply_data(snapshot)


def save_data():
    if not st.session_state.cloud_ready or st.session_state.cloud_client is None:
        rollback_to_saved()
        st.error("클라우드 연결이 없어 저장하지 못했어.")
        return False
    try:
        data = serialize_data()
        old_rev = int(st.session_state.db_revision)
        new_rev = old_rev + 1
        # 비교 후 업데이트(CAS): 다른 탭의 최신 내용을 덮어쓰지 않음.
        result = (st.session_state.cloud_client.table(DEVICE_TABLE)
                  .update({
                      "data": data,
                      "revision": new_rev,
                      "updated_at": datetime.now(timezone.utc).isoformat(),
                  })
                  .eq("device_hash", st.session_state.browser_hash)
                  .eq("revision", old_rev)
                  .select("revision").execute())
        if len(result.data or []) != 1:
            raise RuntimeError("다른 탭의 변경사항과 충돌했어. '최신 데이터 다시 불러오기'를 눌러 줘.")
        readback = fetch_record(st.session_state.cloud_client, st.session_state.browser_hash)
        if (not readback or readback.get("data") != data
                or int(readback.get("revision", -1)) != new_rev):
            # 쓰기 자체가 성공했을 수 있으므로 추가 저장을 멈추도록 표시
            st.session_state.cloud_ready = False
            raise RuntimeError("저장 후 재조회에 문제가 생겼어. 새 저장 전 재연결이 필요해.")
        st.session_state.db_revision = new_rev
        st.session_state.last_saved_data = copy.deepcopy(data)
        st.session_state.last_save_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.cloud_error = ""
        return True
    except Exception as exc:
        rollback_to_saved()
        set_cloud_error("저장·재조회", exc)
        st.error("저장 실패: " + str(exc))
        return False


def save_and_refresh():
    if save_data():
        st.rerun()


def test_cookie_write():
    try:
        marker = str(uuid.uuid4())
        write_cookie(PROBE_COOKIE, marker)
        st.session_state.cookie_probe_status = (
            "테스트 쿠키 저장 요청 완료. 새로고침 후 쿠키 읽기를 검사해 줘."
        )
    except Exception as exc:
        st.session_state.cookie_probe_status = "쿠키 쓰기 오류: " + str(exc)


def test_cookie_read():
    try:
        value1 = st.context.cookies.get(PROBE_COOKIE)
        value2 = cookie_controller().get(PROBE_COOKIE)
        if value1:
            message = "브라우저 새 연결에서 테스트 쿠키를 읽었어."
        elif value2:
            message = "쿠키 컴포넌트에서 테스트 값을 읽었어."
        else:
            message = "테스트 쿠키가 보이지 않아. 브라우저 차단 여부를 확인해 줘."
        st.session_state.cookie_probe_status = message
    except Exception as exc:
        st.session_state.cookie_probe_status = "쿠키 읽기 오류: " + str(exc)


def diagnostic_summary():
    snap = cookie_snapshot()
    return {
        "브라우저 쿠키 (새 연결)": "있음" if snap["request"] else "없음",
        "쿠키 컴포넌트": "읽힘" if snap["component"] else "읽히지 않음",
        "브라우저 식별 번호": (
            str(st.session_state.browser_hash)[:10] + "…"
            if st.session_state.browser_hash else "없음"
        ),
        "DB 연결": "조회 성공" if st.session_state.cloud_ready else "연결 필요",
        "저장 버전": st.session_state.db_revision,
        "실패 단계": st.session_state.cloud_error_step or "없음",
    }


# 기존 데이터가 보이는 상태에서 쿠키 확인을 기다렸다가 시도.
# 쿠키가 없다는 이유로 새 ID를 자동 생성하지 않음.
if not st.session_state.cloud_ready:
    discovered_token = read_browser_token()
    if discovered_token and discovered_token != st.session_state.last_connect_attempt:
        st.session_state.last_connect_attempt = discovered_token
        connect_browser(discovered_token)


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


def food_emoji(item):
    name = str(item.get("name", ""))
    for words, emoji in [
        (("삼겹", "목살", "항정", "갈비", "소고기", "한우", "돼지", "스테이크"), "🥩"),
        (("닭", "치킨"), "🍗"),
        (("계란", "달걀"), "🥚"),
        (("새우", "게살", "꽃게"), "🦐"),
        (("연어", "고등어", "참치", "생선", "오징어", "조개"), "🐟"),
        (("우유", "치즈", "버터", "요거트"), "🥛"),
        (("사과", "딸기", "바나나", "포도", "귤", "복숭아"), "🍎"),
        (("밥", "쌀", "국수", "라면", "파스타", "밀가루"), "🍚"),
        (("간장", "고추장", "된장", "소금", "설탕", "소스"), "🧂"),
    ]:
        if any(word in name for word in words):
            return emoji
    return {"채소": "🥬", "과일": "🍎", "난류(계란)": "🥚", "육류": "🥩", "해산물": "🐟",
            "유제품": "🥛", "곡류·면류": "🍚", "소스·양념": "🧂",
            "가공식품": "🥫"}.get(item.get("category"), "🍽️")


def show_food_card(item):
    with st.container(border=True):
        left, right = st.columns([4, 1])

        with left:
            st.subheader(f"{food_emoji(item)} {item.get('name', '이름 없음')}")
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
        if item.get("food_state", "일반") != "일반":
            st.caption(f"상태: {item['food_state']} · 관련 날짜: {item.get('state_date') or '미입력'}")
        advisory = freshness_notice(item)
        if advisory:
            st.caption(f"🍃 {advisory['title']} · {advisory['detail']}")






# =====================================================
# 5-1. 보관 상태 점검 알림
# 식품 안전 판정이 아닌 참고 알림. 원물/생식재료라는 가정이 맞지
# 않는 가공·살균·진공포장 제품은 제품의 표시사항을 우선 확인.
# 냉장 4°C 이하를 전제로 한 FoodSafety.gov의 일반 보관 안내 참고:
# https://www.foodsafety.gov/food-safety-charts/cold-food-storage-charts
# =====================================================
FOOD_STATES = ["일반", "개봉", "조리 후 보관"]


def freshness_notice(item, today=None):
    """문제 가능성에 대한 점검 제안만 반환하며 먹어도 되는지 판정하지 않는다."""
    today = today or date.today()
    storage = str(item.get("storage", ""))
    if storage == "냉동":
        # 실제로 계속 -18°C 이하에서 냉동됐는지 알 수 없으므로 알림 없음=안전이 아님
        return None

    raw_name = str(item.get("name", ""))
    name = re.sub(r"\s+", "", raw_name.lower())
    category = str(item.get("category", ""))
    state = item.get("food_state", "일반")
    if state not in FOOD_STATES:
        state = "일반"
    started = (item.get("state_date") if state != "일반" else None) or item.get("purchase_date")
    age = max(0, (today - parse_date(started)).days)

    def notice(level, title, detail, kind="보관 상태 점검", elapsed=None):
        return {"level": level, "title": title, "detail": detail, "kind": kind,
                "days": age if elapsed is None else elapsed}

    # 가공/조리/통조림 등은 생식품 보관 기간을 일괄 적용하지 않는다.
    processed = any(x in name for x in (
        "통조림", "캔", "훈제", "소시지", "햄", "베이컨", "육포", "냉동식품",
        "살균", "멸균", "젓갈", "새우젓", "어묵", "치킨너겟", "닭가슴살소시지",
        "구이", "볶음", "조림", "삶은", "익힌", "레토르트", "즉석", "완제품", "육수"
    ))
    dairy = any(x in name for x in ("우유", "요거트", "요구르트", "생크림", "크림치즈"))
    seafood = category == "해산물" or any(x in name for x in (
        "생선", "고등어", "연어", "광어", "대구", "조기", "삼치", "참치", "회",
        "새우", "오징어", "굴", "홍합", "조개", "전복", "가리비", "낙지"
    ))
    poultry = any(x in name for x in ("생닭", "닭고기", "닭가슴살", "닭다리", "오리고기", "생오리"))
    ground_meat = any(x in name for x in ("다짐육", "다진고기", "다진소고기", "다진돼지고기", "민찌", "다진육"))
    meat = category == "육류" or any(x in name for x in (
        "삼겹살", "목살", "항정살", "소고기", "쇠고기", "돼지고기", "한우", "차돌", "스테이크", "갈비"
    ))
    raw_perishable = not processed and (seafood or poultry or ground_meat or meat)

    # 냉장이 필요한 식품이 실온에 기록된 경우 시간을 추정하지 않고 확인을 요청.
    if storage == "실온":
        if state == "조리 후 보관" or raw_perishable:
            return notice("높음", "실온 보관 상태 확인", "육류·수산물이나 조리 음식이 실온으로 등록돼 있어요. 노출 시간과 제품 표시를 즉시 확인해 주세요.")
        if state == "개봉" and dairy:
            return notice("높음", "개봉한 유제품 보관 확인", "개봉한 유제품이 실온으로 등록돼 있어요. 제품 보관 지침과 실온 노출 시간을 확인해 주세요.")
        return None
    if storage != "냉장":
        return None

    if state == "조리 후 보관":
        if age >= 3:
            return notice("높음" if age >= 4 else "점검", "조리한 음식 보관 기간 확인",
                          f"조리일로부터 {age}일 지났어요. 냉장 보관한 남은 음식은 일반적으로 3~4일 내 확인·소비가 권장돼요.")
        return None

    def by_window(first, last, label):
        # 생식재료는 개봉일을 새 보관 시작일로 취급하지 않는다.
        purchase_age = max(0, (today - parse_date(item.get("purchase_date"))).days)
        if purchase_age < first:
            return None
        return notice("높음" if purchase_age >= last else "점검", f"{label} 신선도 확인",
                      f"구매일 기준 {purchase_age}일 경과했어요. 일반적인 냉장 보관 참고 기간은 {first}~{last}일이에요. 제품 상태·표시를 확인해 주세요.", elapsed=purchase_age)

    if not processed:
        if ground_meat:
            return by_window(1, 2, "다짐육")
        if poultry:
            return by_window(1, 2, "생닭·가금류")
        if seafood:
            return by_window(1, 2, "생선·해산물")
        if meat:
            return by_window(3, 5, "생고기")

    if state == "개봉" and dairy and age >= 3:
        return notice("점검", "개봉한 유제품 확인",
                      f"개봉한 지 {age}일 지났어요. 개봉 후 보관 기간은 제품마다 달라요. 표시된 개봉 후 보관 방법을 확인해 주세요.")

    # 잎채소/버섯/딸기는 균일한 안전 기한을 설정하지 않고 상태 확인만 권유.
    delicate = any(x in name for x in ("상추", "깻잎", "시금치", "콩나물", "숙주", "버섯", "딸기", "라즈베리"))
    if not processed and delicate and age >= 3:
        return notice("점검", "무르기 쉬운 신선식품 점검",
                      f"구매일 기준 {age}일 경과했어요. 짓무름·곰팡이·누액·보관 온도를 확인해 주세요. 재료별 실제 보관 가능 기간은 달라요.", "신선도 점검")
    return None


def freshness_alerts(items):
    result = [(item, freshness_notice(item)) for item in items]
    result = [(item, alert) for item, alert in result if alert]
    return sorted(result, key=lambda pair: (0 if pair[1]["level"] == "높음" else 1,
                                                  -pair[1]["days"], str(pair[0].get("name", ""))))


# =====================================================
# 5-1. 내 냉장고 시각화: 브라우저 자료를 그려주는 순수 HTML/CSS
#     냉동칸/냉장선반/채소서랍 + 별도 실온 선반
# =====================================================

def fridge_visual_html(items, compact=False):
    """보관 장소에 따라 실제 냉장고 형태로 칩을 배치한 HTML 문자열 반환.

    단순 출력 기능이며 재료 데이터나 DB를 변경하지 않는다.
    사용자 입력 이름과 수량은 HTML escape 처리해 코드 실행을 방지한다.
    """
    def sort_key(item):
        days = safe_expiry_days(item)
        flagged = bool(ingredient_allergy_flags(item))
        return (0 if flagged else 1 if days < 0 else 2 if days <= 3 else 3, days)

    freezer = sorted((x for x in items if x.get("storage") == "냉동"), key=sort_key)
    chilled = sorted((x for x in items if x.get("storage") == "냉장"), key=sort_key)
    room = sorted((x for x in items if x.get("storage") == "실온"), key=sort_key)
    produce = [x for x in chilled if x.get("category") in ("채소", "과일")]
    chilled_other = [x for x in chilled if x.get("category") not in ("채소", "과일")]

    # Display recommendation only; it is not a record of actual shelf position.
    # Raw meat and seafood go on the lower shelf to reduce cross-contamination
    # risk from leaking juices. Eggs, dairy and ready-to-eat foods go above.
    def lower_shelf_candidate(item):
        if item.get("food_state") == "조리 후 보관":
            return False
        name = re.sub(r"\s+", "", str(item.get("name", "")).lower())
        prepared = (
            "익힌", "삶은", "조리", "구이", "볶음", "찌개", "탕", "국",
            "도시락", "완제품", "레토르트", "통조림", "캔", "훈제", "소시지",
            "베이컨", "햄", "어묵", "육포", "너겟", "참치마요", "치킨너겟",
        )
        if any(word in name for word in prepared):
            return False
        raw_terms = (
            "삼겹", "목살", "항정", "소고기", "쇠고기", "한우", "돼지고기",
            "닭고기", "닭가슴살", "닭다리", "생닭", "생오리", "스테이크",
            "다짐육", "다진고기", "갈비", "연어", "고등어", "생선", "광어",
            "대구", "조기", "새우", "오징어", "조개", "굴", "전복", "회",
        )
        return item.get("category") in ("육류", "해산물") or any(word in name for word in raw_terms)

    bottom_shelf = [x for x in chilled_other if lower_shelf_candidate(x)]
    top_shelf = [x for x in chilled_other if not lower_shelf_candidate(x)]
    pantry_top = room[::2]
    pantry_bottom = room[1::2]
    limit = 4 if compact else None

    def chip(item):
        name = html_escape(str(item.get("name", "재료")), quote=True)
        quantity = html_escape(str(item.get("quantity", "미입력")), quote=True)
        emoji = html_escape(food_emoji(item))
        days = safe_expiry_days(item)
        flags = ingredient_allergy_flags(item)
        freshness = freshness_notice(item)
        classes = ["fm-food"]
        badges = []
        if flags:
            classes.append("fm-allergy")
            badges.append("🚨 알레르기 확인")
        if days < 0:
            classes.append("fm-alert")
            badges.append("⚠ 날짜 경과")
        elif days <= 3:
            classes.append("fm-soon")
            badges.append("⏰ 오늘 확인" if days == 0 else f"⏰ D-{days}")
        if freshness:
            classes.append("fm-risk-high" if freshness["level"] == "높음" else "fm-risk")
            badges.append("🍃 보관 점검")
        badge = "".join(f'<span class="fm-food-badge">{html_escape(t)}</span>' for t in badges)
        tooltip = html_escape(
            f"{item.get('name', '재료')} | {item.get('quantity', '')} | {item.get('expiry', '')}",
            quote=True,
        )
        return (
            f'<div class="{" ".join(classes)}" title="{tooltip}">'
            f'<span class="fm-food-emoji" aria-hidden="true">{emoji}</span>'
            f'<span class="fm-food-text"><span class="fm-food-name">{name}</span>'
            f'<span class="fm-food-sub">{quantity}</span>{badge}</span></div>'
        )

    def section(title, foods, extra_class=""):
        count = len(foods)
        visible = foods[:limit] if limit is not None else foods
        content = "".join(chip(item) for item in visible)
        if count > len(visible):
            content += f'<span class="fm-more">외 {count - len(visible)}개</span>'
        if not count:
            content = '<span class="fm-food-empty">아직 비어 있어요</span>'
        return (
            f'<div class="fm-section {extra_class}">'
            f'<div class="fm-section-heading"><span>{title}</span>'
            f'<span class="fm-section-count">{count}개</span></div>'
            f'<div class="fm-food-grid">{content}</div></div>'
        )

    variant = "fm-viz-compact" if compact else "fm-viz-full"
    total = len(items)
    return (
        f'<div class="fm-viz {variant}" role="group" aria-label="내 보관 재료 현황">'
        '<div class="fm-viz-layout">'
        '<div class="fm-appliance">'
        '<div class="fm-appliance-head"><span>🧊 MY FRIDGE</span>'
        f'<span class="fm-brand-tag">{total} ITEMS</span></div>'
        + section("❄️ 냉동실", freezer, "fm-freezer")
        + section("🥛 냉장실 · 윗선반 (계란·유제품·일반식품)", top_shelf, "fm-chill")
        + section("🥩 냉장실 · 아랫선반 (육류·해산물)", bottom_shelf, "fm-chill-bottom")
        + section("🥬 신선 보관 서랍", produce, "fm-crisper")
        + '<div class="fm-appliance-foot"><span>FRIDGE MATE</span><span>Fresh food, better days.</span></div>'
        '</div>'
        '<div class="fm-pantry"><div class="fm-pantry-header">🌿 실온 보관 선반</div>'
        + section("🍞 윗선반", pantry_top)
        + section("🧂 아랫선반", pantry_bottom)
        + '</div></div>'
        '<div class="fm-viz-key">'
        '<span>🚨 알레르기 참고 알림</span><span>⏰ 날짜 임박</span><span>⚠ 날짜 경과</span><span>🍃 보관 점검</span>'
        '</div>'
        '<div class="fm-viz-note">선반 위치는 재료 종류에 따른 권장 표시예요. 육류·해산물은 밀폐해 아래쪽에 보관하고, 제품별 보관 지침을 확인해 주세요.</div>'
        '</div>'
    )


def render_fridge_visual(items, compact=False):
    st.markdown(fridge_visual_html(items, compact=compact), unsafe_allow_html=True)


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


# -----------------------------------------------------
# 레시피 개별 저장 및 이름 기준 알레르기 참고 검사
# -----------------------------------------------------
ALLERGY_WORDS = {
    "난류(계란)": ("계란", "달걀"),
    "우유": ("우유", "치즈", "버터", "요거트", "크림"),
    "땅콩": ("땅콩",), "호두": ("호두",), "잣": ("잣",),
    "대두": ("두부", "대두", "두유", "콩", "된장", "간장"),
    "밀": ("밀가루", "식빵", "국수", "파스타", "라면"),
    "메밀": ("메밀",), "새우": ("새우",), "게": ("꽃게", "게살"),
    "고등어": ("고등어",), "오징어": ("오징어",),
    "조개류": ("조개", "홍합", "굴", "전복", "바지락"),
    "복숭아": ("복숭아",), "토마토": ("토마토", "케첩"),
    "돼지고기": ("돼지", "삼겹", "목살", "베이컨", "햄"),
    "쇠고기": ("소고기", "쇠고기", "한우", "차돌"),
    "닭고기": ("닭", "치킨"),
    "아황산류": ("아황산",),
}


def ingredient_allergy_flags(item):
    profile = st.session_state.get("profile") or {}
    name = str(item.get("name", "")).replace(" ", "").lower()
    labels = []
    for allergen in profile.get("allergies", []):
        category_matches = (allergen == "난류(계란)" and item.get("category") == "난류(계란)")
        name_matches = any(token in name for token in ALLERGY_WORDS.get(allergen, ()))
        if category_matches or name_matches:
            labels.append(allergen)
    other = re.split(r"[,，/\n]", profile.get("other_allergies", ""))
    if any(x.strip().replace(" ", "").lower() in name
           for x in other if x.strip()):
        labels.append("기타 알레르기")
    return labels


def individual_recipes(result):
    """원본 Groq Markdown 형식을 유지하면서 요리별 저장만 가능하게 분할."""
    pattern = re.compile(r"(?m)^##\s*🍳\s*(.+?)\s*$")
    matches = list(pattern.finditer(result))
    if not matches:
        return [("AI 추천 레시피", result)]
    recipes = []
    for i, match in enumerate(matches):
        stop = matches[i + 1].start() if i + 1 < len(matches) else len(result)
        body = result[match.start():stop].strip()
        # 마지막 요리 아래 붙는 전체 요약은 개별 카드에 포함하지 않음
        body = re.split(r"(?m)^##\s*(?:🏆|🧠)", body)[0].strip()
        if body:
            recipes.append((match.group(1).strip(), body))
    return recipes or [("AI 추천 레시피", result)]


# =====================================================
# 7. 알레르기 및 요리 선호 설정
# =====================================================

def save_profile_from_form(expanded=False):
    profile = st.session_state.get("profile") or {}

    allergy_choices = [
        "난류(계란)", "우유", "땅콩", "호두", "잣", "대두", "밀", "메밀",
        "새우", "게", "고등어", "오징어", "조개류", "복숭아", "토마토",
        "돼지고기", "쇠고기", "닭고기", "아황산류"
    ]

    with st.expander("⚠️ 알레르기 정보 설정", expanded=expanded):
        with st.form("foraging_profile_form"):
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
                "알레르기 정보 저장",
                use_container_width=True
            )

        if submitted:
            st.session_state.profile = {
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
# 8. 이전 메뉴명과 새 메뉴 호환
# =====================================================
if st.session_state.selected_menu == "대시보드":
    st.session_state.selected_menu = "냉장고 홈"
if st.session_state.selected_menu == "AI 레시피":
    st.session_state.selected_menu = "냉장고 파먹기"
if st.session_state.selected_menu == "내 정보":
    st.session_state.selected_menu = "알레르기 정보"

# =====================================================
# 9. 사이드바 / 브라우저 데이터 진단과 백업
# =====================================================
pages = [
    ("냉장고 홈", "🏠"),
    ("내 냉장고", "🥬"),
    ("냉장고 파먹기", "🍳"),
    ("소비기한 관리", "📅"),
    ("장보기 목록", "🛒"),
    ("나의 요리책", "📖"),
    ("알레르기 정보", "⚠️"),
]

with st.sidebar:
    st.caption("S M A R T   K I T C H E N")
    st.title("FRIDGE MATE 🥬")
    st.caption("나만의 작은 키친 매니저")
    st.divider()

    for menu, emoji in pages:
        selected = st.session_state.selected_menu == menu
        if st.button(
            f"{emoji}  {menu}",
            key=f"nav_{menu}",
            use_container_width=True,
            type="primary" if selected else "secondary"
        ):
            open_page(menu)

    st.divider()
    if st.session_state.cloud_ready:
        st.success("☁️ 브라우저 냉장고 연결됨")
        st.caption("브라우저 식별: " + st.session_state.browser_hash[:10] + "…")
        if st.session_state.last_save_time:
            st.caption("최근 저장: " + st.session_state.last_save_time)
    else:
        st.warning("☁️ 저장 연결 확인 필요")
        if st.session_state.cloud_error:
            st.error(st.session_state.cloud_error)

        if st.button("기존 브라우저 정보 다시 확인", use_container_width=True):
            value = read_browser_token() or st.session_state.pending_browser_token
            if value and connect_browser(value):
                st.session_state.last_connect_attempt = value
                st.rerun()
            else:
                st.error(st.session_state.cloud_error or "저장된 브라우저 키가 없어.")

        if st.button("🥬 이 브라우저에서 시작하기", use_container_width=True):
            value = (read_browser_token()
                     or st.session_state.pending_browser_token
                     or secrets.token_urlsafe(32))
            st.session_state.pending_browser_token = value
            if connect_browser(value):
                try:
                    write_cookie(COOKIE_NAME, value)
                    st.session_state.cookie_warning = ""
                    st.session_state.pending_browser_token = None
                    st.info("브라우저 키 저장 요청 완료. 새로고침 후 ID가 같은지 확인해 줘.")
                except Exception as exc:
                    # DB 행이 만들어졌어도 쿠키 쓰기를 실패했다면 다시 복구 가능하게 남김
                    st.session_state.cookie_warning = "브라우저 저장 실패: " + str(exc)
                    st.error(st.session_state.cookie_warning)
            else:
                st.error(st.session_state.cloud_error)

    with st.expander("🔎 브라우저 저장 진단", expanded=not st.session_state.cloud_ready):
        st.caption("비밀 API 키와 브라우저 접근키 자체는 화면에 표시하지 않아.")
        for name, value in diagnostic_summary().items():
            st.write(f"**{name}:** {value}")
        if st.session_state.cookie_warning:
            st.warning(st.session_state.cookie_warning)

        cols = st.columns(2)
        if cols[0].button("테스트 쿠키 저장", use_container_width=True):
            test_cookie_write()
        if cols[1].button("테스트 쿠키 읽기", use_container_width=True):
            test_cookie_read()
        if st.session_state.cookie_probe_status:
            st.info(st.session_state.cookie_probe_status)

        if st.session_state.cloud_ready:
            if st.button("클라우드 저장·재조회 검사", use_container_width=True):
                remote = fetch_record(st.session_state.cloud_client, st.session_state.browser_hash)
                if (remote is not None and
                    remote.get("data") == serialize_data() and
                    int(remote.get("revision", -1)) == st.session_state.db_revision):
                    st.success("Supabase 데이터와 현재 화면이 일치해.")
                else:
                    st.warning("다른 탭의 수정 또는 데이터 불일치가 있어.")
            if st.button("최신 데이터 다시 불러오기", use_container_width=True):
                if connect_browser(st.session_state.browser_token):
                    st.rerun()
                else:
                    st.error(st.session_state.cloud_error)

    with st.expander("📦 JSON 백업·복원"):
        st.caption("브라우저 쿠키를 지우면 기존 냉장고를 자동 복원할 수 없어.")
        if st.session_state.cloud_ready:
            backup = json.dumps(serialize_data(), ensure_ascii=False, indent=2)
            st.download_button(
                "내 냉장고 백업 내려받기",
                data=backup,
                file_name="fridge_mate_backup.json",
                mime="application/json",
                use_container_width=True
            )
            upload = st.file_uploader("JSON 백업에서 데이터 복원", type=["json"])
            if upload is not None and st.button("백업 데이터 복원하기"):
                try:
                    if upload.size > 2_000_000:
                        raise ValueError("JSON 파일은 2MB 이하여야 해.")
                    obj = json.loads(upload.getvalue().decode("utf-8"))
                    apply_data(obj)
                    save_and_refresh()
                except Exception as exc:
                    st.error("복원 실패: " + str(exc))
        else:
            st.info("연결한 다음 백업·복원을 이용할 수 있어.")

    st.caption("Fresh food, better days.")

if not st.session_state.cloud_ready:
    st.info("사이드바에서 '이 브라우저에서 시작하기'를 눌러 냉장고를 이용해 줘.")
    st.stop()


# =====================================================
# 10. 냉장고 홈 — 필요한 알림만 간결하게 표시
# =====================================================

if st.session_state.selected_menu == "냉장고 홈":
    items = st.session_state.fridge_items
    expired = sorted(
        [item for item in items if safe_expiry_days(item) < 0],
        key=safe_expiry_days
    )
    urgent = urgent_fridge_items()  # 오늘부터 3일 이내까지
    allergy_alerts = [
        (item, ingredient_allergy_flags(item))
        for item in items
        if ingredient_allergy_flags(item)
    ]
    freshness_warnings = freshness_alerts(items)

    st.title("오늘의 냉장고 🥬")
    st.caption("소비기한뿐 아니라 보관 중 확인이 필요한 재료도 알려줄게요.")

    # 알레르기 설정에 해당하는 재료가 등록되어 있을 때만 노출
    if allergy_alerts:
        st.error(f"🚨 알레르기 주의 · 확인할 재료 {len(allergy_alerts)}개")
        for item, flags in allergy_alerts[:5]:
            st.write(
                f"{food_emoji(item)} **{item.get('name', '이름 없음')}**"
                f" · 확인 항목: {', '.join(flags)}"
            )
        if len(allergy_alerts) > 5:
            with st.expander(f"나머지 {len(allergy_alerts) - 5}개 재료 보기"):
                for item, flags in allergy_alerts[5:]:
                    st.write(f"• {item.get('name', '이름 없음')} · {', '.join(flags)}")
        st.caption(
            "재료 이름과 저장된 알레르기 설정을 비교한 참고 알림이에요. "
            "가공식품 원재료 표시와 교차접촉 여부를 반드시 직접 확인해 주세요."
        )

    # 소비기한과 별개: 구매·개봉·조리 시점에 따른 보관 상태 점검
    if freshness_warnings:
        high = sum(1 for _, alert in freshness_warnings if alert["level"] == "높음")
        label = f"🍃 신선도·보관 주의 · 확인할 재료 {len(freshness_warnings)}개"
        if high:
            st.warning(label + f" (우선 확인 {high}개)")
        else:
            st.info(label)
        for item, alert in freshness_warnings[:4]:
            st.write(f"{food_emoji(item)} **{item.get('name', '재료')}** · {alert['title']}")
            st.caption(alert["detail"])
        if len(freshness_warnings) > 4:
            with st.expander(f"나머지 {len(freshness_warnings) - 4}개 보관 상태 알림 보기"):
                for item, alert in freshness_warnings[4:]:
                    st.write(f"• {food_emoji(item)} {item.get('name', '재료')} · {alert['title']}")
                    st.caption(alert["detail"])
        st.caption("일반적인 냉장 보관 기준을 이용한 점검 알림이에요. 식품 부패 여부를 자동 판단하지 않아요. 제품 표시와 실제 온도·상태를 우선 확인해 주세요.")

    # 날짜가 지난 재료는 임박 재료보다 먼저 알림
    if expired:
        st.warning(f"⚠️ 날짜 확인 필요 · 기한이 지난 재료 {len(expired)}개")
        for item in expired[:5]:
            st.write(
                f"{food_emoji(item)} **{item.get('name', '이름 없음')}**"
                f" · {abs(safe_expiry_days(item))}일 경과"
            )
        if len(expired) > 5:
            with st.expander(f"나머지 {len(expired) - 5}개 재료 보기"):
                for item in expired[5:]:
                    st.write(f"• {item.get('name', '이름 없음')} · {abs(safe_expiry_days(item))}일 경과")
        st.caption(
            "입력한 소비기한·확인 날짜를 기준으로 표시해요. "
            "실제 제품 표시와 보관 상태를 확인하고, 의심스러운 식품은 먹지 마세요."
        )

    if urgent:
        st.warning(f"⏰ 소비기한 임박 · 3일 이내 재료 {len(urgent)}개")
        for item in urgent[:5]:
            days = safe_expiry_days(item)
            when = "오늘 확인" if days == 0 else f"D-{days}"
            st.write(f"{food_emoji(item)} **{item.get('name', '이름 없음')}** · {when}")
        if len(urgent) > 5:
            with st.expander(f"나머지 {len(urgent) - 5}개 재료 보기"):
                for item in urgent[5:]:
                    days = safe_expiry_days(item)
                    when = "오늘 확인" if days == 0 else f"D-{days}"
                    st.write(f"• {item.get('name', '이름 없음')} · {when}")

    # 정상일 때는 통계·미리보기·바로가기 대신 한 줄만 표시
    if not (allergy_alerts or freshness_warnings or expired or urgent):
        if items:
            st.success("✅ 지금 확인해야 할 알림이 없어요.")
        else:
            st.info("아직 등록한 재료가 없어요.")
            if st.button("🥬 재료 등록하러 가기", use_container_width=True):
                open_page("내 냉장고")

    # 홈은 알림 우선: 간단한 냉장고 그림만 아래에 배치.
    st.divider()
    st.subheader("🧊 내 냉장고 한눈에 보기")
    render_fridge_visual(items, compact=True)

    # 나머지 냉장고·레시피·장보기 기능은 좌측 메뉴에서 이용


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
    st.subheader("🧊 냉장고 시각화")
    st.caption("재료를 등록하거나 보관 장소를 바꾸면 냉장고 그림에도 바로 반영돼요.")
    render_fridge_visual(items, compact=False)

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
                    "채소", "과일", "난류(계란)", "육류", "해산물",
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

        st.caption("🍃 보관 상태 알림 정확도를 높이기 위한 선택 항목")
        state_left, state_right = st.columns(2)
        with state_left:
            food_state = st.selectbox("식품 상태", FOOD_STATES,
                                      help="일반은 구매일, 개봉/조리한 경우는 오른쪽 날짜를 기준으로 점검해요.")
        with state_right:
            state_date = st.date_input("개봉·조리 날짜 (해당할 때만)", value=date.today(),
                                       help="식품 상태가 '일반'이면 이 날짜는 사용하지 않아요.")

        note = st.text_input(
            "메모",
            placeholder="예: 냉장 배송, 포장 상태"
        )

        submitted = st.form_submit_button(
            "＋ 냉장고에 추가하기",
            use_container_width=True
        )

    if submitted:
        if not name.strip():
            st.warning("재료 이름을 입력해 주세요.")
        elif len(st.session_state.fridge_items) >= 500:
            st.error("냉장고 재료는 최대 500개까지 등록할 수 있어.")
        else:
            st.session_state.fridge_items.append({
                "id": str(uuid.uuid4()),
                "name": name.strip(),
                "category": category,
                "quantity": quantity.strip() or "미입력",
                "storage": storage,
                "purchase_date": purchase_date,
                "expiry": expiry,
                "food_state": food_state,
                "state_date": state_date if food_state != "일반" else None,
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
                    f"{food_emoji(item)} {item.get('name', '이름 없음')}"
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
                            "채소", "과일", "난류(계란)", "육류", "해산물",
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

                        states = FOOD_STATES
                        old_state = item.get("food_state", "일반")
                        new_state = st.selectbox(
                            "식품 상태", states,
                            index=states.index(old_state) if old_state in states else 0,
                            key=f"state_{item.get('id', index)}"
                        )
                        new_state_date = st.date_input(
                            "개봉·조리 날짜 (해당할 때만)",
                            value=parse_date(item.get("state_date") or date.today()),
                            key=f"state_date_{item.get('id', index)}"
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
                                "food_state": new_state,
                                "state_date": new_state_date if new_state != "일반" else None,
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
    flagged_items = [(food, ingredient_allergy_flags(food)) for food in usable]
    excluded = [(food, flags) for food, flags in flagged_items if flags]
    usable = [food for food, flags in flagged_items if not flags]
    urgent = [food for food in usable if 0 <= safe_expiry_days(food) <= 3]

    if excluded:
        st.warning("알레르기 설정과 이름이 일치하는 재료를 추천 후보에서 제외했어. "
                   "가공품의 실제 성분은 제품 라벨로 확인해야 해.")
        with st.expander("제외된 재료 보기"):
            for food, flags in excluded:
                st.write(f"{food.get('name', '')} · {', '.join(flags)}")

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

        # 고유 ID 기준으로 선택해 같은 재료/수량/날짜의 중복 항목도 구분
        labels = {str(x.get("id")): x for x in usable}

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
                    format_func=lambda fid: ingredient_label(labels[fid]),
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

            st.subheader("💚 마음에 드는 요리 저장")
            for idx, (title, content) in enumerate(
                individual_recipes(st.session_state.recipe_results)
            ):
                with st.container(border=True):
                    st.write(f"**{title}**")
                    if st.button("이 요리를 나의 요리책에 저장", key=f"save_piece_{idx}"):
                        if any(
                            r.get("content") == content
                            for r in st.session_state.saved_recipes
                        ):
                            st.info("이미 저장한 레시피야.")
                        else:
                            st.session_state.saved_recipes.append({
                                "id": str(uuid.uuid4()),
                                "title": title,
                                "content": content,
                                "created_at": date.today().isoformat()
                            })
                            save_and_refresh()

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
                    save_and_refresh()

                if item.get("done"):
                    with st.expander("🥬 구매한 재료를 냉장고에 등록"):
                        with st.form(f"move_grocery_{item.get('id', i)}"):
                            cat = st.selectbox("카테고리", [
                                "채소", "과일", "난류(계란)", "육류", "해산물", "유제품",
                                "곡류·면류", "소스·양념", "가공식품", "기타"
                            ])
                            storage = st.selectbox("보관 장소", ["냉장", "냉동", "실온"])
                            bought = st.date_input("구매일", value=date.today())
                            expiry = st.date_input("제품 표기 날짜/확인일", value=date.today())
                            st.caption("날짜는 실제 제품을 보고 입력해 줘.")
                            moved = st.form_submit_button("냉장고로 옮기기")
                        if moved:
                            st.session_state.fridge_items.append({
                                "id": str(uuid.uuid4()),
                                "name": item.get("name", ""),
                                "category": cat,
                                "quantity": item.get("quantity", "미입력"),
                                "storage": storage,
                                "purchase_date": bought,
                                "expiry": expiry,
                                "food_state": "일반",
                                "state_date": None,
                                "note": "장보기에서 옮긴 재료"
                            })
                            st.session_state.grocery_items.pop(i)
                            save_and_refresh()

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
# 15. 나의 요리책 (저장한 개별 레시피)
# =====================================================

elif st.session_state.selected_menu == "나의 요리책":
    st.title("나의 작은 요리책 📖")
    st.caption("AI 셰프가 추천한 요리 중 마음에 드는 요리를 모아 두는 공간이야.")

    recipes = st.session_state.saved_recipes
    if not recipes:
        st.info("아직 저장한 레시피가 없어. 냉장고 파먹기에서 저장해 봐.")
    else:
        st.subheader(f"💚 저장한 레시피 {len(recipes)}개")
        for recipe in reversed(list(recipes)):
            rid = str(recipe.get("id", ""))
            with st.expander(
                f"🍳 {recipe.get('title', 'AI 추천 레시피')} · "
                f"{recipe.get('created_at', '날짜 미상')}"
            ):
                st.markdown(recipe.get("content", ""))
                if st.button("🗑️ 이 레시피 삭제", key=f"recipe_delete_{rid}"):
                    recipes.remove(recipe)
                    save_and_refresh()


# =====================================================
# 16. 알레르기 정보 (기존 알레르기·선호 설정 폼 유지)
# =====================================================

elif st.session_state.selected_menu == "알레르기 정보":
    st.title("알레르기 정보 ⚠️")
    st.caption("알레르기와 피하고 싶은 재료를 등록하면 요리 추천에 반영해.")
    save_profile_from_form(expanded=True)


# =====================================================
# 17. 하단
# =====================================================

st.divider()
st.caption("🥬 FRIDGE MATE · Fresh food, better days.")
