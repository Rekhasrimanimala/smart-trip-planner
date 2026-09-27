import json
from typing import Any

from backend.config import get_settings


def invoke_json(system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    try:
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0.2)
        response = model.invoke([
            ("system", system_prompt + " Return only valid JSON."),
            ("human", user_prompt),
        ])
        content = response.content
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        return json.loads(str(content))
    except Exception:
        return None
