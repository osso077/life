import streamlit as st
import pandas as pd
from datetime import date

# 페이지 기본 설정
st.set_page_config(
    page_title="프레시 아일랜드 (Fresh Island)",
    page_icon="🏝️",
    layout="centered"
)

# 세션 상태 초기화 (페이지 네비게이션용)
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "홈"

# 냉장고 재료 리스트 임시 저장용 세션 상태
if "fridge_items" not in st.session_state:
    st.session_state.fridge_items = [
        {"재료": "계란", "수량": 4, "유통기한(일남음)": 2},
        {"재료": "양파", "수량": 2, "유통기한(일남음)": 5}
    ]

def navigate_to(menu_name):
    st.session_state.selected_menu = menu_name

# ==========================================
# 1. 홈 화면 (메인 대시보드)
# ==========================================
if st.session_state.selected_menu == "홈":
    st.title("🏝️ 프레시 아일랜드 (Fresh Island)")
    st.markdown("### 일상의 자원(식재료, 시간, 마음, 정보)을 똑똑하게 관리하고 정화하는 올인원 플랫폼")
    st.write("---")
    
    st.info("💡 아래 버튼 중 원하는 기능을 선택하여 시작하세요!")
    
    # 2x2 그리드로 기능 선택 버튼 배치
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🍳 스마트 냉장고 파먹기", use_container_width=True):
            navigate_to("냉장고 파먹기")
            st.rerun()
            
        if st.button("🧠 익명 고민 상담소", use_container_width=True):
            navigate_to("고민 상담소")
            st.rerun()
            
    with col2:
        if st.button("⏰ 공부 페이스메이커", use_container_width=True):
            navigate_to("공부 페이스메이커")
            st.rerun()
            
        if st.button("🔍 팩트체크 리트머스", use_container_width=True):
            navigate_to("팩트체크")
            st.rerun()

# ==========================================
# 2. 개별 기능 페이지들
# ==========================================
else:
    # 상단 홈으로 가기 버튼
    if st.button("🏠 홈으로 돌아가기"):
        navigate_to("홈")
        st.rerun()
    
    st.write("---")

    # --- [Tab 1] 스마트 냉장고 파먹기 ---
    if st.session_state.selected_menu == "냉장고 파먹기":
        st.header("🍳 스마트 냉장고 파먹기 (Eco-Kitchen)")
        st.write("남은 식재료를 등록하고 유통기한 임박 식재료를 확인해 보세요.")
        
        # 식재료 추가 입력 폼
        with st.form("fridge_form"):
            new_item = st.text_input("식재료 이름 (예: 참치캔, 우유)")
            new_qty = st.number_input("수량", min_value=1, value=1)
            new_expired = st.number_input("남은 유통기한 (일)", min_value=1, value=3)
            submitted = st.form_submit_button("식재료 등록하기")
            
            if submitted and new_item:
                st.session_state.fridge_items.append({"재료": new_item, "수량": new_qty, "유통기한(일남음)": new_expired})
                st.success(f"'{new_item}'이(가) 냉장고에 등록되었습니다!")

        st.subheader("🧊 현재 나의 냉장고 현황")
        df_fridge = pd.DataFrame(st.session_state.fridge_items)
        st.dataframe(df_fridge, use_container_width=True)
        
        if st.button("✨ 남은 재료로 추천 레시피 보기"):
            st.info("🍳 **추천 레시피:** 등록된 재료들을 활용해 간단하게 만들 수 있는 '자취생 특제 볶음밥'을 추천합니다!")

    # --- [Tab 2] 공부 페이스메이커 ---
    elif st.session_state.selected_menu == "공부 페이스메이커":
        st.header("⏰ D-Day 역산 공부 페이스메이커")
        st.write("시험 날짜와 남은 분량을 입력하면 오늘 해야 할 학습량을 계산해 드립니다.")
        
        target_subject = st.text_input("공부할 과목명 (예: 수능 수학)", "수학")
        total_pages = st.number_input("총 학습 분량 (페이지 또는 문제 수)", min_value=1, value=250)
        days_left = st.number_input("시험까지 남은 날수 (D-Day)", min_value=1, value=15)
        
        if st.button("학습 페이스 계산하기"):
            daily_goal = total_pages / days_left
            st.success(f"🎯 **{target_subject} 목표 달성 플랜:**")
            st.metric(label="하루 권장 학습량", value=f"{daily_goal:.1f} 페이지 / 일")
            st.write(f"오늘부터 매일 꾸준히 하시면 D-Day에 완벽하게 끝낼 수 있습니다!")

    # --- [Tab 3] 익명 고민 상담소 ---
    elif st.session_state.selected_menu == "고민 상담소":
        st.header("🧠 마음 날씨 예보 (익명 고민 상담소)")
        st.write("오늘 겪은 학업이나 인간관계 고민을 익명으로 털어놓고 따뜻한 위로를 받아보세요.")
        
        mood = st.selectbox("오늘 나의 기분 날씨는?", ["☀️ 맑음 (평온함)", "⛅ 구름 조금 (소소한 걱정)", "🌧️ 비 (지치고 힘듦)", "⚡ 천둥 번개 (스트레스 폭발)"])
        worry_text = st.text_area("자세한 고민을 적어주세요 (익명 보장)")
        
        if st.button("마음 치유받기"):
            if worry_text:
                st.balloons()
                st.info("💬 **마음 위로 봇의 메시지:**\n\n"
                        "\"힘든 순간 속에서도 이렇게 기록하고 이겨내려 하는 모습 자체가 정말 멋져요. "
                        "오늘 하루도 애썼으니, 너무 무리하지 말고 따뜻한 차 한 잔 마시며 쉬어가는 건 어떨까요? 당신의 내일을 응원합니다! 🌿\"")
            else:
                st.warning("고민 내용을 짧게라도 입력해 주세요!")

    # --- [Tab 4] 팩트체크 리트머스 ---
    elif st.session_state.selected_menu == "팩트체크":
        st.header("🔍 미디어 팩트체크 리트머스")
        st.write("인터넷 기사나 자극적인 문구를 입력해 자극성 및 객관성 지수를 분석해 보세요.")
        
        news_input = st.text_area("검증하고 싶은 문장이나 기사 제목을 입력하세요")
        
        if st.button("팩트체크 분석 실행"):
            if news_input:
                # 간단한 키워드 기반 시뮬레이션 로직
                warning_keywords = ["대충격", "경악", "무조건", "절대", "전격", "폭발"]
                found_keywords = [kw for kw in warning_keywords if kw in news_input]
                
                if found_keywords:
                    st.warning(f"⚠️ **주의:** 자극적/선동성 표현({', '.join(found_keywords)})이 감지되었습니다.")
                    st.metric(label="예상 객관성 지수", value="45% (주의 필요)")
                    st.write("해당 문장은 감정적 어휘가 포함되어 있으므로, 원본 출처나 교차 검증을 통해 팩트를 다시 확인하는 것을 권장합니다.")
                else:
                    st.success("✅ 비교적 차분하고 객관적인 서술형 문장입니다.")
                    st.metric(label="예상 객관성 지수", value="88% (양호)")
            else:
                st.warning("분석할 텍스트를 입력해 주세요!")
