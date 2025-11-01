from __future__ import annotations

import json
from typing import Any, Dict, Optional

from prompt_mangement import intent_prompt
from llm import get_intent


class IntentRecognizer:
    """
    Wrapper for robust intent recognition with schema validation and fallback.
    """

    def __init__(self, model_type: str = 'deepseek', max_retries: int = 2):
        self.model_type = model_type
        self.max_retries = max_retries

    def recognize(self, user_query: str, context: str = '') -> Dict[str, Any]:
        prompt = intent_prompt.replace('<CONTEXT>', context).replace('<INPUT>', user_query)
        raw: Optional[str] = None
        last_error: Optional[str] = None
        for _ in range(self.max_retries + 1):
            try:
                raw = get_intent(prompt, self.model_type)
                data = self._parse(raw)
                return data
            except Exception as e:
                last_error = str(e)
                continue
        return {"query": user_query, "intent": 0, "confidence": 0.0, "reasoning": f"fallback: {last_error or 'unknown error'}"}

    def _parse(self, raw: str) -> Dict[str, Any]:
        obj = json.loads(raw)
        # Normalize minimal fields
        if 'intent' not in obj:
            obj['intent'] = 0
        if 'query' not in obj:
            obj['query'] = ''
        # Optional improvements
        if 'confidence' not in obj:
            obj['confidence'] = 0.7 if obj.get('intent', 0) != 0 else 0.5
        if 'reasoning' not in obj:
            obj['reasoning'] = ''
        return obj


