from datetime import datetime
import json
import os


class AgentMemory:
    def __init__(self, filename):
        self.filename = filename
        self.short_term_memory = {
            "chat_history": [],
            "context_info": {}  # 用于存储额外的上下文信息
        }
        self.load_memory()

    def add_chat_history(self, role, content):
        """添加聊天记录"""
        self.short_term_memory["chat_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.short_term_memory["chat_history"]) > 20:  # 保留最近20条记录
            self.short_term_memory["chat_history"].pop(0)

    def get_chat_history(self):
        """获取聊天历史"""
        return self.short_term_memory["chat_history"]

    def get_context(self):
        """获取当前上下文信息"""
        chat_history = "\n".join(
            [f"{item['role']}: {item['content']}" for item in self.short_term_memory["chat_history"]])
        context_info = json.dumps(self.short_term_memory["context_info"], ensure_ascii=False)
        return f"聊天历史:\n{chat_history}\n\n上下文信息:\n{context_info}"

    def update_context_info(self, key, value):
        """更新上下文信息"""
        self.short_term_memory["context_info"][key] = value

    def clear_memory(self):
        """清空短期记忆"""
        self.short_term_memory = {
            "chat_history": [],
            "context_info": {}
        }

    def save_memory(self):
        """将短期记忆保存到文件"""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.short_term_memory, file, ensure_ascii=False, indent=4)

    def load_memory(self):
        """从文件加载短期记忆"""
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename, 'r', encoding='utf-8') as file:
                loaded_memory = json.load(file)
                self.short_term_memory = {
                    "chat_history": loaded_memory.get("chat_history", []),
                    "context_info": loaded_memory.get("context_info", {})
                }
        return self.short_term_memory

    def update_memory(self, query, result):
        """更新记忆"""
        self.add_chat_history("user", query)
        
        # 检查 result 是否为字典类型
        if isinstance(result, dict):
            answer = result.get('answer', '')
        else:
            answer = str(result)  # 如果不是字典，将整个 result 转换为字符串
        
        self.add_chat_history("assistant", answer)

        # 更新上下文信息
        if isinstance(result, dict):
            if 'leave_info' in result:
                self.update_context_info('leave_info', result['leave_info'])
            if 'trip_info' in result:
                self.update_context_info('trip_info', result['trip_info'])

        self.save_memory()