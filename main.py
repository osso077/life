import streamlit as st
import pandas as pd
import time

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="VIBE CHECK : 라이프 올인원",
    page_icon="⚡",
    layout="centered"
)

# 2. MZ 감성 커스텀 CSS 주입 (네온 그라데이션 + 3D 팝 버튼 + 호버 애니메이션)
st.markdown("""
<style>
    /* 전체 배경: 딥 다크 퍼플-네이비 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
        color: #ffffff;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 힙한 그라데이션 메인 타이틀 */
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

    /* 배지 스타일 */
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

    /* 기본 스트림릿 버튼 커스텀 (크고 둥글고 입체감 있게) */
    div.stButton > button {
        border-radius: 20px !important;
        padding: 1.4rem 1rem !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        border: none !important;
        transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-6px) scale(1.02) !important;
        box-shadow: 0 14px 28px rgba(0, 245, 212, 0.35) !important;
    }

    /* 4가지 기능별 개별 버튼 컬러링 (key 기반 타겟팅) */
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

    /* 홈으로 돌아가기 버튼 */
    .st-key-btn_home button {
        background: rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
        padding: 0.6rem 1.2rem !important;
        font-size: 0.95rem !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    /* 글래스모피즘 카드 컨테이너 */
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
# 4. 홈 화면 (다이나믹 MZ 대시보드)
# ==========================================
if st.session_state.selected_menu == "홈":
    st.markdown('<div style="text-align:center;"><span class="vibe-badge">⚡ ALL-IN-ONE LIFE HACK PLATFORM</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="mz-title">VIBE CHECK 🏝️</div>', unsafe_allow_html=True)
    st.markdown('<div class="mz-subtitle">식재료 · 시간 · 멘탈 · 팩트까지 한 번에 케어하는 갓생 치트키</div>', unsafe_allow_html=True)

    # 2x2 비비드 컬러 카드 버튼 그리드
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        if st.button("🍳 냉장고 파먹기\n\n남은 재료로 뚝딱 레시피", key="btn_fridge", use_container_width=True):
            navigate_to("냉장고 파먹기")
            st.rerun()

        st.write("") # 간격

        if st.button("💜 익명 고민 상담소\n\n오늘의 멘탈 날씨 예보", key="btn_worry", use_container_width=True):
            navigate_to("고민 상담소")
            st.rerun()

    with col2:
        if st.button("🔥 공부 페이스메이커\n\nD-Day 역산 갓생 플래너", key="btn_study", use_container_width=True):
            navigate_to("공부 페이스메이커")
            st.rerun()

        st.write("") # 간격

        if st.button("🚨 팩트체크 리트머스\n\n어그로·가짜뉴스 판별기", key="btn_fact", use_container_width=True):
            navigate_to("팩트체크")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card" style="text-align:center; padding: 16px;">
        <span style="color:#00f5d4; font-weight:700;">✨ TODAY'S VIBE TIP</span><br>
        <span style="color:#e0e0e0; font-size:0.95rem;">원하는 카드를 클릭하면 바로 실행됩니다. 오늘도 갓생 살자! 🚀</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 개별 기능 페이지들
# ==========================================
else:
    if st.button("⬅️ 메인 허브로 돌아가기", key="btn_home"):
        navigate_to("홈")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- [1] 스마트 냉장고 파먹기 ---
    if st.session_state.selected_menu == "냉장고 파먹기":
        st.markdown('<span class="vibe-badge">ECO-KITCHEN</span>', unsafe_allow_html=True)
        st.header("🍳 스마트 냉장고 파먹기")
        st.caption("냉장고 속 잠자는 식재료를 깨워 맛있는 한 끼로 변신시켜 보세요!")

        with st.form("fridge_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                new_item = st.text_input("식재료 이름", placeholder="예: 스팸, 대파")
            with c2:
                new_qty = st.number_input("수량", min_value=1, value=1)
            with c3:
                new_expired = st.number_input("유통기한(일)", min_value=1, value=3)
            
            submitted = st.form_submit_button("➕ 냉장고에 넣기", use_container_width=True)
            if submitted and new_item:
                st.session_state.fridge_items.append({
                    "재료": f"🥗 {new_item}",
                    "수량": new_qty,
                    "남은 유통기한(일)": new_expired
                })
                st.toast(f"'{new_item}' 등록 완료! 🧊", icon="✅")

        st.subheader("🧊 실시간 냉장고 인벤토리")
        df_fridge = pd.DataFrame(st.session_state.fridge_items).sort_values(by="남은 유통기한(일)")
        st.dataframe(df_fridge, use_container_width=True, hide_index=True)

        if st.button("✨ 유통기한 임박 재료로 레시피 추천받기", use_container_width=True):
            urgent_item = df_fridge.iloc[0]["재료"]
            st.success(f"🔥 **긴급 구출 레시피:** 유통기한이 가장 짧은 **{urgent_item}**을(를) 메인으로 한 **'초간단 10분 자취생 특제 볶음밥'**을 추천합니다!")

    # --- [2] 공부 페이스메이커 ---
    elif st.session_state.selected_menu == "공부 페이스메이커":
        st.markdown('<span class="vibe-badge" style="color:#fee440;">STUDY PACEMAKER</span>', unsafe_allow_html=True)
        st.header("🔥 D-Day 역산 갓생 플래너")
        st.caption("막막한 시험 범위, 수학적으로 쪼개서 오늘 할 분량만 딱 알려드려요.")

        col_a, col_b = st.columns(2)
        with col_a:
            target_subject = st.text_input("과목 / 프로젝트명", "수능 수학 기출")
            days_left = st.number_input("D-Day까지 남은 일수", min_value=1, value=14)
        with col_b:
            total_pages = st.number_input("총 분량 (페이지/문제)", min_value=1, value=280)
            done_pages = st.number_input("현재까지 완료한 분량", min_value=0, value=70)

        if st.button("⚡ 나의 갓생 페이스 계산하기", use_container_width=True):
            remain = max(0, total_pages - done_pages)
            daily_goal = remain / days_left
            progress = min(1.0, done_pages / total_pages)

            st.markdown("### 📊 현재 달성률")
            st.progress(progress)
            st.write(f"전체 **{total_pages}** 중 **{done_pages}** 완료! (**{progress*100:.1f}%** 달성)")

            st.metric(
                label=f"🎯 [{target_subject}] 오늘의 필수 할당량",
                value=f"{daily_goal:.1f} 개 / 일",
                delta=f"남은 분량: {remain}"
            )

    # --- [3] 익명 고민 상담소 ---
    elif st.session_state.selected_menu == "고민 상담소":
        st.markdown('<span class="vibe-badge" style="color:#f15bb5;">MIND CARE</span>', unsafe_allow_html=True)
        st.header("💜 마음 날씨 예보 (익명 고민 상담소)")
        st.caption("아무도 모르게 털어놓는 오늘의 감정. 다 털어놓고 가볍게 나가세요.")

        mood = st.select_slider(
            "지금 내 마음의 기압은?",
            options=["⚡ 번개 쾅쾅", "🌧️ 비 주룩주룩", "⛅ 구름 조금", "☀️ 맑고 화창", "🌈 무지개 뿜뿜"],
            value="⛅ 구름 조금"
        )
        worry_text = st.text_area("오늘 어떤 일이 있었나요?", placeholder="성적, 친구 관계, 진로 고민 무엇이든 좋아요...")

        if st.button("💌 위로 처방전 받기", use_container_width=True):
            if worry_text.strip():
                with st.spinner("마음 주파수를 맞추는 중..."):
                    time.sleep(0.8)
                st.balloons()
                st.markdown(f"""
                <div class="glass-card" style="border-color: #f15bb5;">
                    <h4 style="color:#f15bb5; margin-top:0;">✨ 당신만을 위한 시크릿 처방전</h4>
                    <p style="font-size:1.05rem; line-height:1.6;">
                        "지금 느끼는 불안함이나 지침은 네가 그만큼 진심으로 잘해내고 싶다는 증거야. 
                        잠시 숨 한 번 크게 쉬고, 좋아하는 노래 한 곡 들으면서 텐션 다시 끌어올리자! 
                        넌 이미 충분히 잘하고 있어. 🎧💜"
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("짧게라도 마음을 적어주면 처방전을 드릴 수 있어요!")

    # --- [4] 팩트체크 리트머스 ---
    elif st.session_state.selected_menu == "팩트체크":
        st.markdown('<span class="vibe-badge" style="color:#ff4d6d;">TRUTH DETECTOR</span>', unsafe_allow_html=True)
        st.header("🚨 미디어 팩트체크 리트머스")
        st.caption("자극적인 낚시성 기사나 루머, 어그로 지수를 판독해 드립니다.")

        news_input = st.text_area("검증할 헤드라인이나 SNS 글을 붙여넣으세요", placeholder="예: [대충격] 내일부터 당장 이것 안 하면 무조건 손해본다?!")

        if st.button("🔍 어그로 & 객관성 스캔 시작", use_container_width=True):
            if news_input.strip():
                warning_keywords = ["대충격", "경악", "무조건", "절대", "전격", "폭발", "충격", "실화", "미쳤다", "단독"]
                found = [kw for kw in warning_keywords if kw in news_input]

                score = max(15, 95 - len(found) * 20)
                st.markdown("### 🧪 리트머스 판독 결과")
                st.progress(score / 100)

                if found:
                    st.error(f"🚨 **어그로 경보 발령!** 자극적 키워드 감지: `{', '.join(found)}`")
                    st.metric("객관성 신뢰 지수", f"{score}점 / 100점", delta="-주의 필요", delta_color="inverse")
                    st.write("감정을 자극해 클릭을 유도하는 전형적인 표현이 섞여 있습니다. 원문 출처를 꼭 교차 검증하세요!")
                else:
                    st.success("✅ **클린 텍스트 판정!** 자극적인 선동 어휘가 발견되지 않았습니다.")
                    st.metric("객관성 신뢰 지수", f"{score}점 / 100점", delta="+양호함")
            else:
                st.warning("판독할 문장을 먼저 입력해 주세요!")
