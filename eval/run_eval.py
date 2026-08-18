import json
import os

from app.llm.client import get_llm_client
from app.llm.prompts import TRIAGE_PROMPT
from app.llm.schema import TriageResponse


def clean_json(content: str) -> str:
    """
    Membersihkan response LLM dari markdown code fence.
    """
    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    return content


def repair_response(client, content: str):
    """
    Meminta LLM memperbaiki response yang bukan JSON valid.
    """

    repair_prompt = f"""
The following response is NOT valid JSON:

{content}

Convert it into ONLY valid JSON using EXACTLY this schema:

{{
  "category": "billing|bug|feature|other",
  "urgency": "low|normal|high",
  "confidence": 0.0,
  "reason": "short explanation"
}}

Rules:
- Return ONLY JSON.
- No markdown.
- No explanation.
- Do not add fields.
"""

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[
            {
                "role": "system",
                "content": (
                    "You repair invalid LLM output. "
                    "Return only valid JSON."
                )
            },
            {
                "role": "user",
                "content": repair_prompt
            }
        ],
        temperature=0
    )

    repaired = response.choices[0].message.content

    if not repaired:
        raise ValueError("Repair returned empty response")

    return clean_json(repaired)


def main():

    with open("eval/triage_cases.json", "r") as file:
        cases = json.load(file)

    client = get_llm_client()

    correct_category = 0
    correct_urgency = 0

    total = len(cases)

    print(f"Running evaluation on {total} cases...\n")

    for index, case in enumerate(cases, start=1):

        prompt = TRIAGE_PROMPT.format(
            text=case["text"]
        )

        try:

            # ============================================
            # FIRST LLM CALL
            # ============================================

            response = client.chat.completions.create(
                model=os.environ["LLM_MODEL"],
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a customer support "
                            "triage classifier. "
                            "Return only valid JSON."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("Empty LLM response")

            content = clean_json(content)

            # ============================================
            # VALIDATE FIRST RESPONSE
            # ============================================

            try:

                result = TriageResponse.model_validate_json(
                    content
                )

            except Exception:

                print(
                    f"{index}. Invalid JSON → "
                    f"attempting repair..."
                )

                # ========================================
                # REPAIR RETRY
                # ========================================

                repaired_content = repair_response(
                    client,
                    content
                )

                result = TriageResponse.model_validate_json(
                    repaired_content
                )

                print(
                    f"{index}. Repair successful"
                )

            # ============================================
            # COMPARE RESULT
            # ============================================

            category_ok = (
                result.category.value
                == case["category"]
            )

            urgency_ok = (
                result.urgency.value
                == case["urgency"]
            )

            if category_ok:
                correct_category += 1

            if urgency_ok:
                correct_urgency += 1

            print(
                f"{index}. "
                f"category="
                f"{'PASS' if category_ok else 'FAIL'}"
                f" | "
                f"urgency="
                f"{'PASS' if urgency_ok else 'FAIL'}"
            )

        except Exception as e:

            print(
                f"{index}. ERROR: {e}"
            )

    # ================================================
    # FINAL SCORE
    # ================================================

    category_score = correct_category / total
    urgency_score = correct_urgency / total

    print("\n==============================")
    print("EVALUATION RESULT")
    print("==============================")

    print(
        f"Category accuracy: "
        f"{correct_category}/{total} "
        f"({category_score:.0%})"
    )

    print(
        f"Urgency accuracy: "
        f"{correct_urgency}/{total} "
        f"({urgency_score:.0%})"
    )


if __name__ == "__main__":
    main()