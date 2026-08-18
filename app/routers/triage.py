import json
import os

from fastapi import APIRouter, HTTPException

from app.llm.client import get_llm_client
from app.llm.schema import TriageRequest, TriageResponse

router = APIRouter()


@router.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    if os.getenv("LLM_ENABLED", "true").lower() != "true":
        return {
            "category": "other",
            "urgency": "normal",
            "confidence": 0.5,
            "reason": "LLM is disabled."
        }

    client = get_llm_client()

    prompt = f"""
Classify the following customer support message.

Choose:
category: billing, bug, feature, other
urgency: low, normal, high

Return ONLY valid JSON with this exact structure:
{{
  "category": "billing|bug|feature|other",
  "urgency": "low|normal|high",
  "confidence": 0.0,
  "reason": "short explanation"
}}

Customer message:
{request.text}
"""

    try:
        response = client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[
                {
                    "role": "system",
                    "content": "You are a customer support triage classifier."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        result = json.loads(content)

        return TriageResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM request failed: {str(e)}"
        )