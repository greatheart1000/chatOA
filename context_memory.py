from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class ConversationMemoryManager:
    """
    High-level memory manager combining short-term rolling chat history and
    lightweight slot memory per intent. Persists to JSON files.
    """

    def __init__(self,
                 short_term_path: str = 'short_term_memory.json',
                 long_term_path: str = 'long_term_memory.json',
                 max_messages: int = 20):
        self.short_term_path = short_term_path
        self.long_term_path = long_term_path
        self.max_messages = max_messages

        self.short_term: Dict[str, Any] = {
            "chat_history": [],  # List[{role, content, timestamp}]
            "context_info": {}   # Free-form key-value
        }
        self.long_term: Dict[str, Any] = {
            "slots": {}  # intent(int)-> { key: value }
        }

        self._load()

    # ---------- Public API ----------
    def add_user_message(self, content: str) -> None:
        self._append_history("user", content)

    def add_assistant_message(self, content: str) -> None:
        self._append_history("assistant", content)

    def get_history_pairs(self, limit: Optional[int] = None) -> List[Tuple[str, str]]:
        pairs: List[Tuple[str, str]] = []
        buf: List[Dict[str, str]] = self.short_term["chat_history"][-(limit or self.max_messages):]
        last_user: Optional[str] = None
        for item in buf:
            if item["role"] == "user":
                last_user = item["content"]
            elif item["role"] == "assistant" and last_user is not None:
                pairs.append((last_user, item["content"]))
                last_user = None
        return pairs

    def get_context_string(self) -> str:
        history = "\n".join([
            f"{m['role']}: {m['content']}" for m in self.short_term["chat_history"][-self.max_messages:]
        ])
        context_info = json.dumps(self.short_term["context_info"], ensure_ascii=False)
        return f"聊天历史:\n{history}\n\n上下文信息:\n{context_info}"

    def update_context_info(self, key: str, value: Any) -> None:
        self.short_term["context_info"][key] = value
        self._persist()

    def remember_slot(self, intent: int, key: str, value: Any) -> None:
        intent_key = str(intent)
        if intent_key not in self.long_term["slots"]:
            self.long_term["slots"][intent_key] = {}
        self.long_term["slots"][intent_key][key] = value
        self._persist()

    def recall_slots(self, intent: int) -> Dict[str, Any]:
        return dict(self.long_term["slots"].get(str(intent), {}))

    def save(self) -> None:
        self._persist()

    # ---------- Internal ----------
    def _append_history(self, role: str, content: str) -> None:
        self.short_term["chat_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.short_term["chat_history"]) > self.max_messages:
            self.short_term["chat_history"].pop(0)
        self._persist()

    def _load(self) -> None:
        if os.path.exists(self.short_term_path) and os.path.getsize(self.short_term_path) > 0:
            try:
                with open(self.short_term_path, 'r', encoding='utf-8') as f:
                    st = json.load(f)
                    if isinstance(st, dict):
                        self.short_term.update(st)
            except Exception:
                pass
        if os.path.exists(self.long_term_path) and os.path.getsize(self.long_term_path) > 0:
            try:
                with open(self.long_term_path, 'r', encoding='utf-8') as f:
                    lt = json.load(f)
                    if isinstance(lt, dict):
                        self.long_term.update(lt)
            except Exception:
                pass

    def _persist(self) -> None:
        try:
            with open(self.short_term_path, 'w', encoding='utf-8') as f:
                json.dump(self.short_term, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        try:
            with open(self.long_term_path, 'w', encoding='utf-8') as f:
                json.dump(self.long_term, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


