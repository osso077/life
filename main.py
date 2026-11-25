
import json
from openai import OpenAI, OpenAIError


def generate_ai_recipes(
    ingredients,
    category="자유롭게 추천",
    max_time="제한 없음",
    difficulty="상관없음",
    extra_request="",
    strict_selected=False,
    urgent_names=None,
    allow_substitutes=True
):
    api_key = str(
        st.secrets.get("GROQ_API_KEY", "")
    ).strip()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY가 없어. Streamlit Secrets를 확인해 줘."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    urgent_names = urgent_names or []

    ingredient_list = []

    for item in ingredients:
        if isinstance(item, dict):
            name = (
                item.get("name")
                or item.get("food")
                or item.get("ingredient")
            )
            if name:
                ingredient_list.append(str(name))
        else:
            ingredient_list.append(str(item))

    system_prompt = """
너는 FRIDGE MATE의 창의적인 AI 셰프다.

사용자가 가진 재료를 분석하고 새로운 요리를 창작한다.

다음 원칙을 지켜라.

1. 저장된 레시피만 검색하지 말고 새로운 요리를 창작한다.
2. 재료의 맛, 향, 식감, 조리 특성을 분석한다.
3. 재료끼리 어울리는 이유를 설명한다.
4. 실제로 조리할 수 있는 현실적인 조리법을 만든다.
5. 냉장고에 없는 재료는 별도로 표시한다.
6. 대체할 수 있는 재료를 제안한다.
7. 소비기한 임박 재료를 우선 활용한다.
8. 육류와 달걀 등은 안전하게 충분히 익히도록 한다.
9. 서로 다른 특징을 가진 요리를 제안한다.

반드시 JSON 객체만 출력한다.

출력 형식:
{
  "analysis": "재료 분석",
  "recipes": [
    {
      "name": "요리 이름",
      "description": "요리 설명",
      "reason": "재료 궁합 분석",
      "ingredients": [
        {
          "name": "재료",
          "amount": "사용량",
          "owned": true
        }
      ],
      "missing_ingredients": [],
      "substitutions": [
        {
          "original": "원래 재료",
          "alternative": "대체 재료"
        }
      ],
      "steps": [
        "조리 단계 1",
        "조리 단계 2"
      ],
      "cooking_time": "20분",
      "difficulty": "쉬움",
      "taste": "맛과 식감 설명"
    }
  ]
}

서로 다른 요리 5개를 창작한다.
"""

    user_prompt = f"""
[냉장고 재료]
{json.dumps(ingredient_list, ensure_ascii=False)}

[소비기한 임박 재료]
{json.dumps(urgent_names, ensure_ascii=False)}

[요리 종류]
{category}

[최대 조리 시간]
{max_time}

[희망 난이도]
{difficulty}

[선택 재료만 사용]
{strict_selected}

[대체 재료 허용]
{allow_substitutes}

[추가 요청]
{extra_request}

재료의 특성을 분석하고 창의적인 요리 5가지를 만들어라.
"""

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
        max_tokens=5000,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content

    # JSON 유효성 확인
    parsed = json.loads(result)

    return json.dumps(parsed, ensure_ascii=False)
