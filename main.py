            selected_items = []
            st.warning('선택할 수 있는 재료가 없어. 내 냉장고에 재료를 등록해 줘.')
        st.divider()
        with st.form('foraging_recipe_form'):
            st.subheader('🍽️ 요리 조건')
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox('음식 종류', ['전체', '한식', '양식', '중식', '일식', '간식', '간단식'])
                max_time = st.selectbox('조리 시간', [10, 20, 30, 60], index=2, format_func=lambda x: f'{x}분 이내')
            with c2:
                difficulty = st.selectbox('난이도', ['전체', '쉬움', '보통'])
                extra_request = st.text_input('추가 요청', placeholder='예: 매콤하게, 설거지 적게')
            allow_substitutes = st.checkbox('재료가 부족하면 대체 재료도 추천받기', value=True, help='선택 재료만으로 만들기 모드에서는 선택한 재료 외의 재료를 필수 재료로 추가하지 않고 대체 아이디어를 별도로 알려줘.')
            generate = st.form_submit_button('✨ 냉장고 재료로 요리 추천받기', use_container_width=True)
        if generate:
            if not selected_items:
                st.warning('먼저 사용할 재료를 선택하거나 냉장고에 재료를 등록해 줘.')
            else:
                ingredient_text = '\n'.join((f"- {x.get('name')} / 수량: {x.get('quantity', '미입력')} / 보관: {x.get('storage', '미입력')} / 카테고리: {x.get('category', '기타')}" for x in selected_items))
                urgent_names = [x.get('name', '') for x in selected_items if safe_expiry_days(x) <= 3]
                strict = mode.startswith('내가 선택한')
                with st.spinner('AI 셰프가 재료의 맛과 조합을 분석하고 새로운 요리를 창작하는 중이야...'):
                    try:
                        result = generate_ai_recipes(ingredient_text, category, max_time, difficulty, extra_request, strict_selected=strict, urgent_names=urgent_names, allow_substitutes=allow_substitutes)
                        st.session_state.recipe_results = result
                        if st.session_state.cloud_ready:
                            save_data()
                        else:
                            st.warning('레시피는 생성됐지만 클라우드 연결이 없어 저장하지 못했어.')
                    except ValueError as e:
                        st.error(str(e))
                    except OpenAIError as e:
                        st.error('Groq AI 요청에 실패했어.')
                        st.write('**오류 종류:**', type(e).__name__)
                        st.write('**오류 내용:**', str(e))
                        status_code = getattr(e, 'status_code', None)
                        error_code = getattr(e, 'code', None)
                        request_id = getattr(e, 'request_id', None)
                        if status_code:
                            st.write('**HTTP 상태 코드:**', status_code)
                        if error_code:
                            st.write('**오류 코드:**', error_code)
                        if request_id:
                            st.write('**요청 ID:**', request_id)
                        st.caption('Groq API 키, 모델 이름, 사용량 제한 및 API 상태를 확인해 줘.')
                    except Exception as e:
                        st.error('예상하지 못한 오류가 발생했어.')
                        st.write('**오류 종류:**', type(e).__name__)
                        st.exception(e)
        if st.session_state.get('recipe_results'):
            st.divider()
            st.subheader('🍽️ 오늘의 냉장고 파먹기 레시피')
            st.markdown(st.session_state.recipe_results)
            st.caption('AI가 제안한 조리법은 참고용이야. 알레르기, 식품 상태, 제품별 조리 안내를 직접 확인하고 충분히 익혀야 하는 식재료는 안전한 조리 기준을 따라 줘.')
            if st.button('결과 지우기', key='clear_recipe_results'):
                st.session_state.recipe_results = None
                save_and_refresh()
    st.divider()
    save_profile_from_form()
elif st.session_state.selected_menu == '소비기한 관리':
    st.title('소비기한 관리 📅')
    st.caption('날짜를 기준으로 재료를 확인하고, 먼저 사용할 재료를 파악해 보세요.')
    items = st.session_state.fridge_items
    expired = [x for x in items if safe_expiry_days(x) < 0]
    today_items = [x for x in items if safe_expiry_days(x) == 0]
    soon = [x for x in items if 1 <= safe_expiry_days(x) <= 3]
    later = [x for x in items if safe_expiry_days(x) > 3]
    cols = st.columns(4)
    for col, title, count in zip(cols, ('날짜 지남', '오늘', '3일 이내', '여유 있음'), (len(expired), len(today_items), len(soon), len(later))):
        col.metric(title, f'{count}개')
    for title, group in (('🔴 날짜 확인이 필요한 재료', expired), ('🟠 오늘 확인할 재료', today_items), ('🟡 3일 이내 확인할 재료', soon), ('🟢 여유 있는 재료', later)):
        st.subheader(title)
        if not group:
            st.caption('해당하는 재료가 없어요.')
        else:
            for item in sorted(group, key=safe_expiry_days):
                show_food_card(item)
    if not items:
        st.info('먼저 내 냉장고에 재료를 등록해 줘.')
    st.caption('날짜 표시는 입력한 날짜를 기준으로 한 참고 정보야. 실제 섭취 가능 여부는 제품 표시, 보관 온도·상태, 개봉 여부 등을 함께 확인해 줘.')
elif st.session_state.selected_menu == '장보기 목록':
    st.title('장보기 목록 🛒')
    st.caption('냉장고에 부족한 재료와 필요한 식재료를 정리해 보세요.')
    with st.form('grocery_form', clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            name = st.text_input('구매할 재료', placeholder='예: 우유')
        with right:
            quantity = st.text_input('수량', placeholder='예: 1개, 2팩')
        add = st.form_submit_button('＋ 장보기 목록에 추가', use_container_width=True)
    if add:
        if name.strip():
            st.session_state.grocery_items.append({'id': str(uuid.uuid4()), 'name': name.strip(), 'quantity': quantity.strip() or '미입력', 'done': False})
            save_and_refresh()
        else:
            st.warning('재료 이름을 입력해 줘.')
    st.divider()
    groceries = st.session_state.grocery_items
    if not groceries:
        st.info('장보기 목록이 비어 있어.')
    else:
        for i, item in enumerate(groceries):
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    checked = st.checkbox(f"{item.get('name')} · {item.get('quantity', '미입력')}", value=bool(item.get('done', False)), key=f"grocery_{item.get('id', i)}")
                with c2:
                    delete = st.button('삭제', key=f"delete_grocery_{item.get('id', i)}")
                if delete:
                    st.session_state.grocery_items.pop(i)
                    save_and_refresh()
                if checked != bool(item.get('done', False)):
                    item['done'] = checked
                    if save_data():
                        st.rerun()
        done_count = sum((1 for x in groceries if x.get('done')))
        st.divider()
        st.progress(done_count / len(groceries))
        st.caption(f'{done_count} / {len(groceries)}개 구매 완료')
        if st.button('완료한 항목 모두 삭제'):
            st.session_state.grocery_items = [x for x in groceries if not x.get('done')]
            save_and_refresh()
st.divider()
st.caption('🥬 FRIDGE MATE · Fresh food, better days.')
