
                with col2:

                    delete = st.button(
                        "삭제",
                        key=f"delete_grocery_{item['id']}"
                    )

                if delete:
                    st.session_state.grocery_items.pop(i)
                    save_and_refresh()

                if checked != item["done"]:
                    item["done"] = checked
                    save_data()

        done_count = sum(
            1 for x in groceries if x["done"]
        )

        st.divider()
        st.progress(done_count / len(groceries))
        st.caption(f"{done_count} / {len(groceries)}개 구매 완료")

        if st.button("완료한 항목 모두 삭제"):

            st.session_state.grocery_items = [
                x for x in groceries if not x["done"]
            ]

            save_and_refresh()


# =====================================================
# 14. 나의 요리책
# =====================================================

elif st.session_state.selected_menu == "나의 요리책":

    st.title("나의 작은 요리책 📖")
    st.caption("마음에 드는 레시피를 모아 나만의 요리책을 만들어 보세요.")

    recipes = st.session_state.saved_recipes

    if not recipes:

        st.info(
            "아직 저장한 레시피가 없어요. "
            "AI 레시피에서 마음에 드는 요리를 저장해 보세요!"
        )

    else:

        st.subheader(f"💚 저장한 레시피 {len(recipes)}개")

        for i, recipe in enumerate(recipes):

            with st.expander(
                f"🍳 {recipe['title']} · {recipe['created_at']}"
            ):

                st.markdown(recipe["content"])

                if st.button(
                    "🗑️ 이 레시피 삭제",
                    key=f"delete_recipe_{recipe['id']}"
                ):

                    st.session_state.saved_recipes.pop(i)
                    save_and_refresh()



# =====================================================
# 15. 내 정보 (기존 데이터에 profile 필드만 추가)
# =====================================================

elif st.session_state.selected_menu == "내 정보":
    st.title("내 정보 👤")
    st.caption("닉네임과 식재료 선호 정보를 관리해 보세요.")
    profile = st.session_state.profile or {}
    allergy_choices = ["난류(계란)", "우유", "땅콩", "호두", "잣", "대두", "밀", "메밀", "새우", "게", "고등어", "오징어", "조개류", "복숭아", "토마토", "돼지고기", "쇠고기", "닭고기", "아황산류"]
    with st.form("profile_form"):
        nickname = st.text_input("닉네임", value=profile.get("nickname", ""))
        allergies = st.multiselect("알레르기 유발 식재료", allergy_choices,
                                   default=[x for x in profile.get("allergies", []) if x in allergy_choices])
        other_allergies = st.text_input("기타 알레르기", value=profile.get("other_allergies", ""))
        avoid_ingredients = st.text_area("피하고 싶은 재료 (알레르기와 별개)", value=profile.get("avoid_ingredients", ""))
        update_profile = st.form_submit_button("내 정보 저장", use_container_width=True)
    if update_profile:
        st.session_state.profile = {"nickname": nickname.strip(), "allergies": allergies,
                                    "other_allergies": other_allergies.strip(), "avoid_ingredients": avoid_ingredients.strip()}
        save_and_refresh()
    st.info("AI 레시피는 알레르기 안전을 보장할 수 없어. 실제 포장지의 알레르기 표기와 교차접촉 여부를 반드시 확인해 줘.")


# =====================================================
# 16. 하단
# =====================================================

st.divider()

st.caption("🥬 FRIDGE MATE · Fresh food, better days.")
