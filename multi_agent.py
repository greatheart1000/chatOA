from util import *
import time
import dashscope
import requests
import json
import os
import uuid
from flask import url_for
import requests
from zhipuai import ZhipuAI
from openai import OpenAI
from memory import AgentMemory
from llm import query_llm,get_intent
from context_memory import ConversationMemoryManager
from intent_service import IntentRecognizer
from prompt_mangement import prompts,intent_prompt,chat_prompt,SQL_prompt,bussiness_prompt
from datetime import datetime
from module.calendar import *
from collections import deque

current_time = datetime.now()
# 格式化输出为"年-月-日 小时:分钟"
formatted_time = current_time.strftime("%Y-%m-%d %H:%M")
print('formatted_time', formatted_time)
now_time  = datetime.now()
now_time  = now_time.strftime("%Y-%m-%d %H:%M:%S")
USER_INFO = {
    'employee_id': '12345',
    'employee_name': '张三',
    'department': '技术部',
    'position': '软件工程师'
}

model_type='deepseek'

class WorkAssistant:
    def __init__(self, user_name, filename):
        self.user_name = user_name
        self.memory = AgentMemory(filename)
        # 简化架构：不再需要具体的助手实例，只需要意图识别即可
        self.chat_history = deque(maxlen=20)  # 保存最新20条聊天记录
        self.memory_manager = ConversationMemoryManager(
            short_term_path='short_term_memory.json',
            long_term_path='long_term_memory.json',
            max_messages=20
        )
        self.intent_recognizer = IntentRecognizer(model_type=model_type)

    def add_to_chat_history(self, role, content):
        self.chat_history.append({"role": role, "content": content})

    def get_chat_history_string(self):
        return "\n".join([f"{item['role']}: {item['content']}" for item in self.chat_history])

    def handle_chat(self, query, context):
        chat_response = query_llm(chat_prompt.replace('<INPUT>', query), model_type)
        try:
            response_data = json.loads(chat_response)
            answer = f"{response_data['response']} {response_data['suggestion']}"
            return {'query': query, 'answer': answer, 'intent': 0}
        except json.JSONDecodeError:
            return {'query': query, 'answer': '抱歉，我没有理解您的意思。请问您需要申请请假、查询通讯录或者处理其他工作相关事务吗？', 'intent': 0}

    def get_intent_with_context(self, query, context):
        result = self.intent_recognizer.recognize(query, context)
        return json.dumps(result, ensure_ascii=False)

    def handle_intent(self, num, query, context):
        """简化处理：识别到意图后直接返回链接"""
        # 意图到链接的映射
        intent_links = {
            1: '/quick/leave',      # 请假申请
            2: '/quick/contact',    # 通讯录查询
            3: '/quick/email',      # 邮件发送
            4: '/quick/trip',       # 出差申请
            5: '/quick/schedule'    # 日程管理
        }
        
        if num == 0:
            # 闲聊，正常聊天处理
            return self.handle_chat(query, context)
        elif num in intent_links:
            # 业务意图，直接返回链接
            link = intent_links[num]
            intent_names = {
                1: '请假申请',
                2: '通讯录查询',
                3: '邮件发送',
                4: '出差申请',
                5: '日程管理'
            }
            answer = f"我已识别到您的意图：**{intent_names[num]}**。"
            return {
                'query': query,
                'answer': answer,
                'link': link,
                'intent': num
            }
        else:
            return {'query': query, 'answer': '抱歉,我无法处理这个请求', 'intent': num}

    def process_query(self, query, context=''):
        start = time.time()
        self.add_to_chat_history("user", query)
        self.memory_manager.add_user_message(query)
        context = self.memory_manager.get_context_string()
        intent_msg = self.get_intent_with_context(query, context)
        print('intent_msg', intent_msg)
        
        try:
            intent_data = json.loads(intent_msg)
            num = intent_data['intent']
        except json.JSONDecodeError:
            print(f"Invalid JSON: {intent_msg}")
            # 设置一个默认的 intent，比如 0 表示普通对话
            num = 0
        except KeyError:
            print(f"No 'intent' key in JSON: {intent_msg}")
            num = 0

        print(f'cost intent: {time.time() - start}')
        response = self.handle_intent(num, query, context)
        
        # 确保返回的是一个字典
        if not isinstance(response, dict):
            response = {'answer': str(response), 'intent': num}
        elif 'answer' not in response:
            response['answer'] = response.get('response', '无回答')
        
        # 确保返回的response包含intent
        response['intent'] = num
        
        self.add_to_chat_history("assistant", response['answer'])
        self.memory_manager.add_assistant_message(response['answer'])
        print(f'cost intent: {time.time()-start}')
        
        return response


# 如果有其他辅助函数或类，请在这里添加