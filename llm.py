from zhipuai import ZhipuAI
from openai import OpenAI
import json
import requests

ZhipuAI_client = ZhipuAI(api_key="216c94f2b634ad81f217f930639e8c05.CosGbnQAbNY0n34b")  # 请填写您自己的APIKey

alibaba_client = OpenAI(
        api_key="sk-14a1de8e32534bc58bf398780dce94ae", # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )
# 我的api_key sk-a77c07502a9b454c8e8c59e3d47dd9b9
deepseek_client = OpenAI(api_key="sk-a77c07502a9b454c8e8c59e3d47dd9b9",
                base_url="https://api.deepseek.com")

url = 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 926a172e-ca2a-4df4-8829-d3baf50c6fbb'  # 替换为你的实际Token
}
# dashscope.api_key = "sk-14a1de8e32534bc58bf398780dce94ae"

def get_intent(prompt, model_type):
    try:
        response = query_llm(prompt, model_type)
        intent_data = json.loads(response)
        if 'intent' not in intent_data:
            intent_data['intent'] = 0  # 设置默认 intent
        return json.dumps(intent_data)
    except json.JSONDecodeError:
        print(f"Invalid JSON from LLM: {response}")
        return json.dumps({"intent": 0})
    except Exception as e:
        print(f"Error in get_intent: {str(e)}")
        return json.dumps({"intent": 0})

def query_llm(msg,model_type):
    if model_type=='glm':
        response = ZhipuAI_client.chat.completions.create(
            model="glm-4-flash",  # 填写需要调用的模型编码
            messages=[
                {"role": "user", "content": msg},

            ],
        )
        return response.choices[0].message.content
    elif model_type=='doubao':
        data = {"model": "ep-20240822092702-jjp9v",
                "messages": [{"role": "assistant", "content": msg}]}
        response = requests.post(url, headers=headers, json=data)
        reply = response.json()['choices'][0]['message']['content']
        return reply
    elif model_type=='deepseek':
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "assistant", "content": msg},
            ],
            stream=False, response_format={
                'type': 'json_object'}
        )
        answer = response.choices[0].message.content
        print(answer)
        return answer
    elif model_type=='ali':
        completion =alibaba_client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {'role': 'user', 'content': msg}],
            response_format={
                "type": "json_object"
            }
        )
        answer =json.loads(completion.model_dump_json())['choices'][0]['message']['content']
        return answer
