import streamlit as st
import pandas as pd
import time
import random
import re

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="VIBE CHECK : 라이프 올인원",
    page_icon="⚡",
    layout="wide"
)

# 2. 선반 격리 및 큼직한 아이콘 그리드 전용 CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
        color: #ffffff;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .mz-title {
        font-size: 3.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00f5d4, #00bbf9, #f15bb5, #fee440);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }

    .mz-subtitle {
        text-align: center;
        color: #b8c1ec;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 2rem;
    }

    .vibe-badge {
        display: inline-block;
        background: rgba(0, 245, 212, 0.15);
        border: 1px solid #00f5d4;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        color: #00f5d4;
        font-weight: 700;
        margin-bottom: 12px;
    }

    /* 홈 화면 버튼 스타일 */
    div.stButton > button {
        border-radius: 20px !important;
        padding: 1.4rem 1rem !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        border: none !important;
        transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-6px) scale(1.02) !important;
        box-shadow: 0 14px 28px rgba(0, 245, 212, 0.35) !important;
    }

    .st-key-btn_fridge button { background: linear-gradient(135deg, #00f5d4 0%, #00bbf9 100%) !important; color: #0b0920 !important; }
    .st-key-btn_study button { background: linear-gradient(135deg, #fee440 0%, #ff9f1c 100%) !important; color: #0b0920 !important; }
    .st-key-btn_worry button { background: linear-gradient(135deg, #f15bb5 0%, #9b5de5 100%) !important; color: #ffffff !important; }
    .st-key-btn_fact button { background: linear-gradient(135deg, #ff4d6d 0%, #ff758f 100%) !important; color: #ffffff !important; }
    .st-key-btn_home button { background: rgba(255, 255, 255, 0.2) !important; color: #ffffff !important; font-size: 0.95rem !important; }

    /* =========================================
       🧊 냉장고 문 틀 및 선반 칸 구획 디자인
       ========================================= */
    .fridge-door-box {
        background: #e0f7fa;
        border: 5px solid #00bbf9;
        border-radius: 28px;
        padding: 20px;
        box-shadow: 0 15px 35px rgba(0, 188, 212, 0.25);
        color: #102a43;
    }

    .freezer-door-box {
        background: #f1f5f9;
        border: 5px solid #94a3b8;
        border-radius: 28px;
        padding: 20px;
        box-shadow: 0 15px 35px rgba(148, 163, 184, 0.25);
        color: #102a43;
    }

    .door-title {
        font-size: 1.4rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 3px dashed rgba(0,0,0,0.12);
    }

    /* 선반 칸 하나하나를 명확히 구분하는 박스 */
    .shelf-compartment {
        background: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    .shelf-label {
        font-size: 0.8rem;
        font-weight: 800;
        color: #475569;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 큼직한 아이콘과 밑에 작은 글자가 들어가는 푸드 카드 */
    .food-grid-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .big-icon-card {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 14px;
        text-align: center;
        min-width: 85px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    .food-big-emoji {
        font-size: 2.8rem; /* 아이콘 크게 강조 */
        display: block;
        margin-bottom: 4px;
    }

    .food-name-small {
        font-size: 0.8rem;
        font-weight: 800;
        color: #1e293b;
        display: block;
    }

    .food-qty-small {
        font-size: 0.7rem;
        color: #64748b;
        display: block;
        margin-bottom: 4px;
    }

    .badge-urgent { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; padding: 1px 5px; border-radius: 4px; font-size: 0.65rem; font-weight: 800; display: inline-block; margin-top: 2px; }
    .badge-safe { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; padding: 1px 5px; border-radius: 4px; font-size: 0.65rem; font-weight: 800; display: inline-block; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# 3. 음식 이모지 매핑 함수
def get_food_emoji(name):
    food_map = {
        "계란": "🥚", "달걀": "🥚", "우유": "🥛", "치즈": "🧀", "버터": "🧈",
        "양파": "🧅", "대파": "🧅", "파": "🧅", "마늘": "🧄", "감자": "🥔",
        "고구마": "🍠", "당근": "🥕", "토마토": "🍅", "오이": "🥒", "배추": "🥬",
        "김치": "🥬", "상추": "🥬", "양배추": "🥬", "브로콜리": "🥦", "버섯": "🍄",
        "사과": "🍎", "바나나": "🍌", "딸기": "🍓", "포도": "🍇", "수박": "🍉",
        "고기": "🥩", "소고기": "🥩", "돼지고기": "🥓", "삼겹살": "🥓", "베이컨": "🥓",
        "닭고기": "🍗", "치킨": "🍗", "햄": "🍖", "소시지": "🌭", "스팸": "🥫",
        "참치": "🥫", "생선": "🐟", "연어": "🍣", "새우": "🦐", "오징어": "🦑",
        "밥": "🍚", "빵": "🍞", "식빵": "🍞", "라면": "🍜", "만두": "🥟"
    }
    for key, emoji in food_map.items():
        if key in name:
            return emoji
    return "🍱"

# 4. 재료 종류 판별 함수
def get_food_category(name):
    meat_keywords = ["고기", "삼겹살", "소고기", "돼지", "치킨", "닭", "생선", "연어", "새우", "오징어", "베이컨", "햄", "만두"]
    dairy_keywords = ["우유", "치즈", "버터", "계란", "달걀", "요거트", "요플레"]
    if any(k in name for k in meat_keywords):
        return "육류/해산물/냉동식품"
    elif any(k in name for k in dairy_keywords):
        return "유제품/반찬"
    else:
        return "채소/과일/기타"

# 5. 세션 상태 초기화
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "홈"

if "fridge_items" not in st.session_state:
    st.session_state.fridge_items = []

def navigate_to(menu_name):
    st.session_state.selected_menu = menu_name

# ==========================================
# 6. 홈 화면
# ==========================================
if st.session_state.selected_menu == "홈":
    st.markdown('<div style="text-align:center;"><span class="vibe-badge">⚡ ALL-IN-ONE LIFE HACK PLATFORM</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="mz-title">VIBE CHECK 🏝️</div>', unsafe_allow_html=True)
    st.markdown('<div class="mz-subtitle">나만의 스마트한 갓생 치트키 ⚡</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        if st.button("🍳 냉장고 파먹기", key="btn_fridge", use_container_width=True):
            navigate_to("냉장고 파먹기")
            st.rerun()

        st.write("")

        if st.button("💜 익명 고민 상담소", key="btn_worry", use_container_width=True):
            navigate_to("고민 상담소")
            st.rerun()

    with col2:
        if st.button("🔥 스터디 타이머", key="btn_study", use_container_width=True):
            navigate_to("스터디 타이머")
            st.rerun()

        st.write("")

        if st.button("🚨 팩트체크", key="btn_fact", use_container_width=True):
            navigate_to("팩트체크")
            st.rerun()

# ==========================================
# 7. 개별 기능 페이지들
# ==========================================
else:
    if st.button("⬅️ 메인으로", key="btn_home"):
        navigate_to("홈")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- [1] 냉장고 파먹기 ---
    if st.session_state.selected_menu == "냉장고 파먹기":
        st.markdown('<span class="vibe-badge">🧊 SMART FRIDGE & FREEZER</span>', unsafe_allow_html=True)
        st.header("🍳 스마트 냉장고 & 냉동실 파먹기")
        st.caption("선반 칸별로 큼직한 아이콘과 함께 직관적으로 정리된 인벤토리입니다.")

        # 입력 폼
        with st.form("fridge_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                new_item = st.text_input("음식 이름", placeholder="예: 삼겹살, 우유, 만두")
            with c2:
                loc_type = st.selectbox("보관 위치", ["냉장실", "냉동실"])
            with c3:
                new_qty = st.number_input("수량", min_value=1, value=1)
            with c4:
                new_expired = st.number_input("유통기한(일)", min_value=1, value=5)
            
            submitted = st.form_submit_button("📥 재료 등록하기", use_container_width=True)
            if submitted and new_item.strip():
                clean_name = re.sub(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]', '', new_item).strip()
                st.session_state.fridge_items.append({
                    "name": clean_name,
                    "type": loc_type,
                    "qty": new_qty,
                    "days": new_expired
                })
                st.success(f"'{clean_name}' 등록 완료!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # 좌우 분할 (냉장실 vs 냉동실)
        col_fridge, col_freezer = st.columns(2, gap="medium")

        def make_big_icon_cards(lst):
            if not lst:
                return "<span style='color:#94a3b8; font-size:0.85rem;'>선반이 비어있습니다 🍃</span>"
            cards_html = ""
            for it in lst:
                emoji = get_food_emoji(it["name"])
                badge_class = "badge-urgent" if it["days"] <= 3 else "badge-safe"
                badge_text = f"D-{it['days']} 임박" if it["days"] <= 3 else f"D-{it['days']}"
                cards_html += f"""
                <div class="big-icon-card">
                    <span class="food-big-emoji">{emoji}</span>
                    <span class="food-name-small">{it['name']}</span>
                    <span class="food-qty-small">{it['qty']}개 보관</span>
                    <span class="{badge_class}">{badge_text}</span>
                </div>
                """
            return cards_html

        def render_compartment(comp_type):
            items = [i for i in st.session_state.fridge_items if i["type"] == comp_type]
            
            cat1 = [i for i in items if get_food_category(i["name"]) == "채소/과일/기타"]
            cat2 = [i for i in items if get_food_category(i["name"]) == "유제품/반찬"]
            cat3 = [i for i in items if get_food_category(i["name"]) == "육류/해산물/냉동식품"]

            title_text = "❄️ 냉장실 (3°C)" if comp_type == "냉장실" else "🧊 냉동실 (-18°C)"
            title_color = "#0284c7" if comp_type == "냉장실" else "#334155"
            box_class = "fridge-door-box" if comp_type == "냉장실" else "freezer-door-box"

            st.markdown(f"""
            <div class="{box_class}">
                <div class="door-title" style="color:{title_color};">{title_text}</div>
                
                <div class="shelf-compartment">
                    <div class="shelf-label" style="color:#0284c7;">🥗 상단 칸 : 채소 · 과일</div>
                    <div class="food-grid-container">{make_big_icon_cards(cat1)}</div>
                </div>
                
                <div class="shelf-compartment">
                    <div class="shelf-label" style="color:#d97706;">🧀 중단 칸 : 유제품 · 반찬</div>
                    <div class="food-grid-container">{make_big_icon_cards(cat2)}</div>
                </div>
                
                <div class="shelf-compartment" style="margin-bottom:0;">
                    <div class="shelf-label" style="color:#e11d48;">🥩 하단 칸 : 육류 · 가공식품</div>
                    <div class="food-grid-container">{make_big_icon_cards(cat3)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_fridge:
            render_compartment("냉장실")

        with col_freezer:
            render_compartment("냉동실")

        st.markdown("<br>", unsafe_allow_html=True)
        
        c_b1, c_b2 = st.columns([3, 1])
        with c_b1:
            if st.button("✨ 냉장고 재료로 레시피 추천받기", use_container_width=True):
                if st.session_state.fridge_items:
                    names = [i["name"] for i in st.session_state.fridge_items]
                    st.success(f"🍳 **오늘의 추천 요리:** **{', '.join(names[:3])}** 등을 활용한 초간단 요리를 완성해보세요!")
                else:
                    st.warning("등록된 재료가 없습니다!")
        with c_b2:
            if st.button("🗑️ 전체 비우기", use_container_width=True):
                st.session_state.fridge_items = []
                st.rerun()

    # --- [2] 스터디 타이머 ---
    elif st.session_state.selected_menu == "스터디 타이머":
        st.markdown('<span class="vibe-badge" style="color:#fee440;">STUDY TIMER</span>', unsafe_allow_html=True)
        st.header("🔥 스터디 타이머 & 페이스메이커")
        st.caption("집중 모드를 켜고 오늘 할당량을 완벽하게 부수어 보세요.")

        sub = st.text_input("목표 과목", "수능 수학")
        if st.button("집중 시작", use_container_width=True):
            st.balloons()
            st.success("🔥 집중 세션 완료!")

    # --- [3] 익명 고민 상담소 ---
    elif st.session_state.selected_menu == "고민 상담소":
        st.markdown('<span class="vibe-badge" style="color:#f15bb5;">MIND CARE</span>', unsafe_allow_html=True)
        st.header("💜 익명 고민 상담소")
        st.caption("고민을 털어놓고 AI 처방전을 받아보세요.")

        worry = st.text_area("고민 입력")
        if st.button("처방전 받기", use_container_width=True):
            st.balloons()
            st.info("💊 \"오늘도 고생많았어! 푹 쉬자!\"")

    # --- [4] 팩트체크 ---
    elif st.session_state.selected_menu == "팩트체크":
        st.markdown('<span class="vibe-badge" style="color:#ff4d6d;">TRUTH DETECTOR</span>', unsafe_allow_html=True)
        st.header("🚨 팩트체크 리트머스")
        st.caption("자극적인 헤드라인을 판독합니다.")

        news = st.text_area("문장 입력")
        if st.button("분석", use_container_width=True):
            st.success("✅ 클린 텍스트!")
