
elif st.session_state.selected_menu == "소비기한 관리":
    st.title("소비기한 관리 📅")
    st.caption("날짜를 기준으로 재료를 확인하고, 먼저 사용할 재료를 파악해 보세요.")

    items = st.session_state.fridge_items
    expired = [x for x in items if safe_expiry_days(x) < 0]
    today_items = [x for x in items if safe_expiry_days(x) == 0]
    soon = [x for x in items if 1 <= safe_expiry_days(x) <= 3]
    later = [x for x in items if safe_expiry_days(x) > 3]

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
        "날짜 표시는 입력한 날짜를 기준으로 한 참고 정보야. 실제 섭취 가능 여부는 "
        "제품 표시, 보관 온도·상태, 개봉 여부 등을 함께 확인해 줘."
    )


# =====================================================
# 14. 장보기 목록
# =====================================================

elif st.session_state.selected_menu == "장보기 목록":
    st.title("장보기 목록 🛒")
    st.caption("냉장고에 부족한 재료와 필요한 식재료를 정리해 보세요.")

    with st.form("grocery_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            name = st.text_input("구매할 재료", placeholder="예: 우유")
        with right:
            quantity = st.text_input("수량", placeholder="예: 1개, 2팩")
        add = st.form_submit_button("＋ 장보기 목록에 추가", use_container_width=True)

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
                        f"{item.get('name')} · {item.get('quantity', '미입력')}",
                        value=bool(item.get("done", False)),
                        key=f"grocery_{item.get('id', i)}"
                    )
                with c2:
                    delete = st.button("삭제", key=f"delete_grocery_{item.get('id', i)}")
                if delete:
                    st.session_state.grocery_items.pop(i)
                    save_and_refresh()
                if checked != bool(item.get("done", False)):
                    item["done"] = checked
                    if save_data():
                        st.rerun()

        done_count = sum(1 for x in groceries if x.get("done"))
        st.divider()
        st.progress(done_count / len(groceries))
        st.caption(f"{done_count} / {len(groceries)}개 구매 완료")
        if st.button("완료한 항목 모두 삭제"):
            st.session_state.grocery_items = [x for x in groceries if not x.get("done")]
            save_and_refresh()


# =====================================================
# 15. 하단
# =====================================================

st.divider()
st.caption("🥬 FRIDGE MATE · Fresh food, better days.")
