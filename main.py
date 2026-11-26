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
# 4. 로그인 없는 브라우저 식별 + Supabase 저장
# =====================================================
# 주의: SUPABASE_SERVER_KEY는 Secret 또는 service_role 키여야 하고,
# Streamlit Secrets에만 보관해야 해. GitHub에 절대 넣으면 안 돼.
# 브라우저에는 무작위 비밀값, DB에는 그 SHA-256 해시만 저장해.

DEVICE_COOKIE = "fridge_mate_browser_key_v1"
DEVICE_COOKIE_DAYS = 180
DEVICE_TABLE = "fridge_mate_browser_data"
DEVICE_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{40,100}$")


def cookie_controller():
    return CookieController(key="fridge_mate_browser_cookie_controller_v1")


def set_cloud_error(step, error):
    st.session_state.cloud_ready = False
    st.session_state.cloud_error_step = step
    st.session_state.cloud_error = str(error)


def get_server_client():
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    server_key = str(st.secrets.get("SUPABASE_SERVER_KEY", "")).strip()
    if not url or not server_key:
        raise RuntimeError(
            "Streamlit Secrets에 SUPABASE_URL과 SUPABASE_SERVER_KEY를 설정해 줘."
        )
    if url.endswith("/rest/v1") or url.endswith("/auth/v1"):
        raise RuntimeError("SUPABASE_URL은 /rest/v1 등이 없는 프로젝트 기본 주소여야 해.")
    if server_key.startswith("sb_secret_"):
        pass  # 새 형식의 서버 전용 Secret key
    elif server_key.count(".") == 2:
        # 구형 JWT 키도 허용하지만 role=service_role인지 반드시 검사한다.
        try:
            encoded = server_key.split(".")[1]
            decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
            role = json.loads(decoded.decode("utf-8")).get("role")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("SUPABASE_SERVER_KEY의 형식을 확인해 줘.") from exc
        if role != "service_role":
            raise RuntimeError(
                "현재 키는 service_role이 아니야. 서버 전용 Secret/service_role 키가 필요해."
            )
    else:
        raise RuntimeError(
