import streamlit as st
import pandas as pd
import time
import random

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="VIBE CHECK : 라이프 올인원",
    page_icon="⚡",
    layout="centered"
)

# 2. MZ 감성 커스텀 CSS 주입
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
        font-size: 1.05rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }

    .vibe-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        color: #00f5d4;
        font-weight: 700;
        margin-bottom: 12px;
    }

    div.stButton > button {
        border-radius: 20px !important;
        padding: 1.6rem 1rem !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        border: none !important;
        transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-6px) scale(1.02) !important;
        box-shadow: 0 14px 28px rgba(0, 245, 212, 0.35) !important;
    }

    .st-key-btn_fridge button {
        background: linear-gradient(135deg, #00f5d4 0%, #00bbf9 100%) !important;
        color: #0b0920 !important;
    }
    .st-key-btn_study button {
        background: linear-gradient(135deg, #fee440 0%, #ff9f1c 100%) !important;
        color: #0b0920 !important;
    }
    .st-key-btn_worry button {
        background: linear-gradient(135deg, #f15bb5 0%, #9b5de5 100%) !important;
        color: #ffffff !important;
    }
    .st-key-btn_fact button {
        background: linear-gradient(135deg, #ff4d6d 0%, #ff758f 100%) !important;
        color: #ffffff !important;
    }

    .st-key-btn_home button {
        background: rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
        padding: 0.6rem 1.2rem !important;
        font-size: 0.95rem !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 24px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 세션 상태 초기화
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "홈"

if "fridge_items" not in st.session_state:
    st.session_state.fridge_items = [
        {"재료": "🥚 계란", "수량": 4, "남은 유통기한(일)": 2},
        {"재료": "🧅 양파", "수량": 2, "남은 유통기한(일)": 5},
        {"재료": "🧀 치즈", "수량": 3, "남은 유통기한(일)": 1}
    ]

def navigate_to(menu_name):
    st.session_state.selected_menu = menu_name

# ==========================================
# 4. 홈 화면 (오타 수정 및 깔끔한 버튼 배치)
# ==========================================
if st.session_state.selected_menu == "홈":
    st.markdown('<div style="text-align:center;"><span class="vibe-badge">⚡ ALL-IN-ONE LIFE HACK PLATFORM</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="mz-title">VIBE CHECK 🏝️</div>', unsafe_allow_html=True)
    st.markdown('<div class="mz-subtitle">나만의 스마트한 일상 관리 치트키</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        if st.button("🍳 냉장고 파먹기", key="btn_fridge", use_container_width=True):
            navigate_to("냉장고 파먹기")
            st.rerun()

        st.write("")

        # 오타 수정 완료: '익명 고민 상담소'
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card" style="text-align:center; padding: 16px;">
        <span style="color:#00f5d4; font-weight:700;">💡 QUICK TIP</span><br>
        <span style="color:#e0e0e0; font-size:0.9rem;">버튼을 눌러 원하는 기능을 실행해 보세요. 데이터는 실시간으로 반영됩니다!</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 개별 기능 페이지들
# ==========================================
else:
    if st.button("⬅️ 메인으로", key="btn_home"):
        navigate_to("홈")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- [1] 냉장고 파먹기 ---
    if st.session_state.selected_menu == "냉장고 파먹기":
        st.markdown('<span class="vibe-badge">ECO-KITCHEN</span>', unsafe_allow_html=True)
        st.header("🍳 스마트 냉장고 파먹기")
        st.caption("유통기한 임박 재료를 파악하고 맞춤형 레시피를 추천받으세요.")

        with st.form("fridge_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                new_item = st.text_input("식재료 이름", placeholder="예: 스팸, 김치")
            with c2:
                new_qty = st.number_input("수량", min_value=1, value=1)
            with c3:
                new_expired = st.number_input("유통기한(일)", min_value=1, value=3)
            
            submitted = st.form_submit_button("➕ 식재료 추가", use_container_width=True)
            if submitted and new_item:
                st.session_state.fridge_items.append({
                    "재료": f"🥗 {new_item}",
                    "수량": new_qty,
                    "남은 유통기한(일)": new_expired
                })
                st.toast(f"'{new_item}'이(가) 추가되었습니다!", icon="✅")

        st.subheader("🧊 인벤토리 현황")
        df_fridge = pd.DataFrame(st.session_state.fridge_items).sort_values(by="남은 유통기한(일)")
        st.dataframe(df_fridge, use_container_width=True, hide_index=True)

        if st.button("✨ 맞춤형 레시피 조합 생성", use_container_width=True):
            recipes = [
                "🔥 **치즈 계란볶음밥:** 남은 계란과 치즈, 양파를 잘게 썰어 버터에 볶아낸 초간단 요리!",
                "🍲 **만능 재료 찌개:** 냉장고 속 자투리 재료를 모두 때려 넣고 고추장으로 간을 맞춘 얼큰한 찌개!",
                "🥪 **토스트 브런치:** 식빵(또는 남은 빵)에 치즈와 계란을 얹어 오븐이나 프라이팬에 구워낸 브런치!"
            ]
            st.success(random.choice(recipes))

    # --- [2] 스터디 타이머 ---
    elif st.session_state.selected_menu == "스터디 타이머":
        st.markdown('<span class="vibe-badge" style="color:#fee440;">STUDY TIMER & GOAL</span>', unsafe_allow_html=True)
        st.header("🔥 스터디 타이머 & 페이스메이커")
        st.caption("집중 모드를 켜고 오늘 할당량을 완벽하게 부수어 보세요.")

        tab_timer, tab_goal = st.tabs(["⏱️ 집중 뽀모도로 타이머", "📊 D-Day 학습 플래너"])

        with tab_timer:
            st.markdown("### 🍅 뽀모도로 집중 세션")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                focus_time = st.selectbox("모드 선택", ["집중 25분 / 휴식 5분", "딥다이브 50분 / 휴식 10분"])
            with col_t2:
                st.write("")
                st.write("")
                start_btn = st.button("🚀 타이머 시뮬레이션 시작", use_container_width=True)
            
            if start_btn:
                with st.status("🔥 집중 세션 진행 중...", expanded=True) as status:
                    st.write("몰입 상태 진입... 잡생각 차단 중 🧠")
                    time.sleep(1)
                    st.write("시간이 순삭되는 중입니다 ⏳")
                    time.sleep(1)
                    status.update(label="🎉 세션 완료! 수고하셨습니다!", state="complete", expanded=False)
                st.balloons()

        with tab_goal:
            sub = st.text_input("학습 과목 / 목표", "수능 수학 기출 분석")
            c_a, c_b = st.columns(2)
            with c_a:
                total = st.number_input("총 분량", min_value=1, value=200)
                done = st.number_input("완료한 분량", min_value=0, value=50)
            with c_b:
                days = st.number_input("남은 일수", min_value=1, value=10)

            if st.button("계산하기", use_container_width=True):
                remain = max(0, total - done)
                daily = remain / days
                st.progress(min(1.0, done / total))
                st.metric(label=f"[{sub}] 하루 권장 학습량", value=f"{daily:.1f} 분량 / 일")

    # --- [3] 익명 고민 상담소 ---
    elif st.session_state.selected_menu == "고민 상담소":
        st.markdown('<span class="vibe-badge" style="color:#f15bb5;">MIND CARE</span>', unsafe_allow_html=True)
        st.header("💜 익명 고민 상담소")
        st.caption("누구에게도 말 못 할 고민을 적어주시면 AI 카운슬러가 맞춤 위로를 건네드립니다.")

        mood = st.select_slider("현재 나의 멘탈 상태는?", options=["⚡ 번개 폭발", "🌧️ 비 내림", "⛅ 구름 낀 날", "☀️ 맑음"], value="⛅ 구름 낀 날")
        worry = st.text_area("고민 내용을 적어주세요", placeholder="학업, 인간관계, 미래에 대한 막막함 등...")

        if st.button("💌 위로 처방전 발급받기", use_container_width=True):
            if worry.strip():
                prescriptions = [
                    "\"지금 겪는 고민은 네가 더 멋진 사람으로 성장하기 위한 성장통이야. 오늘 밤은 아무 생각 말고 좋아하는 음악과 함께 푹 쉬자! 🎧\"",
                    "\"산더미 같아 보이는 일들도 결국 하루하루 지나가기 마련이야. 너는 지금까지도 잘 해내왔고, 앞으로도 그럴 거야. 🌿\"",
                    "\"너무 완벽하려고 애쓰지 않아도 괜찮아. 조금 서툴러도 네 속도대로 나아가는 네 모습 자체가 빛나고 있어! ✨\""
                ]
                with st.spinner("마음의 안정을 찾는 중..."):
                    time.sleep(0.6)
                st.balloons()
                st.markdown(f"""
                <div class="glass-card" style="border-color: #f15bb5;">
                    <h4 style="color:#f15bb5; margin-top:0;">💊 AI 시크릿 처방 메시지</h4>
                    <p style="font-size:1.05rem; line-height:1.6;">{random.choice(prescriptions)}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("고민 내용을 짧게라도 입력해 주세요!")

    # --- [4] 팩트체크 ---
    elif st.session_state.selected_menu == "팩트체크":
        st.markdown('<span class="vibe-badge" style="color:#ff4d6d;">TRUTH DETECTOR</span>', unsafe_allow_html=True)
        st.header("🚨 팩트체크 리트머스")
        st.caption("자극적인 헤드라인과 루머의 객관성 지수를 정밀 스캔합니다.")

        news = st.text_area("분석할 문장이나 기사 제목 입력", placeholder="예: [단독] 이거 안 보면 평생 후회합니다!!")

        if st.button("🔍 정밀 분석 스캔 실행", use_container_width=True):
            if news.strip():
                bad_words = ["대충격", "경악", "무조건", "절대", "전격", "폭발", "단독", "긴급", "실화"]
                detected = [w for w in bad_words if w in news]
                score = max(10, 92 - len(detected) * 25)

                st.markdown("### 📊 분석 리포트")
                st.progress(score / 100)

                c1, c2 = st.columns(2)
                with c1:
                    st.metric("객관성 신뢰 지수", f"{score}점 / 100점")
                with c2:
                    st.metric("자극성(어그로) 레벨", f"{len(detected) * 30}%")

                if detected:
                    st.error(f"⚠️ 감지된 선동성 키워드: `{', '.join(detected)}`\n\n조회수를 높이기 위한 과장 표현이 포함되어 있으니 주의하세요!")
                else:
                    st.success("✅ 클린하고 객관적인 서술형 문장으로 판정되었습니다.")
            else:
                st.warning("분석할 텍스트를 입력해 주세요!")
