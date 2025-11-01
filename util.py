import time
import dashscope
import requests
import json
import os
import uuid
import requests
from zhipuai import ZhipuAI
from openai import OpenAI
import pymysql
from pymysql.cursors import DictCursor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

client = ZhipuAI(api_key="216c94f2b634ad81f217f930639e8c05.CosGbnQAbNY0n34b")  # 请填写您自己的APIKey

alibaba_client = OpenAI(
        api_key="sk-14a1de8e32534bc58bf398780dce94ae", # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )


url = 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 926a172e-ca2a-4df4-8829-d3baf50c6fbb'  # 替换为你的实际Token
}
dashscope.api_key = "sk-14a1de8e32534bc58bf398780dce94ae"
from openai import OpenAI

# target_format = """
#   {
#     msg:{"假期类型": xxx,
#         "开始时间": "2024-09-11 09:00",
#         "结束时间": "2024-09-12 18:00"
#         "事由": xxxx,
#         "备岗": xxx
#         },
#     '建议':xxx
#     }
# """


target_format = """
  { 'query':xxx ,  
    msg:{"假期类型": xxx,
        "开始时间": "2024-09-11 09:00",
        "结束时间": "2024-09-12 18:00"
        "事由": xxxx,
        "备岗": xxx
        },
    '建议': {
            "信息完整": True/False,
            "补充建议": "请补充缺失的字段信息"
            }
    }
"""
reasoning_format= """
  { 'query':xxx ,   
    msg:  {"假期类型": xxx,
            "开始时间": "2024-09-11 09:00",
            "结束时间": "2024-09-12 18:00"
            "事由": xxxx,
            "备岗": xxx
          },
    '推理':{
            "隐含信息":{
                  "假期类型":xxx,
                  "事由": xxx
                    },
            "时间隐含信息": {
                  "开始时间": xxx,
                  "结束时间": xx
                    },
            "合理性检查": {
              "请假时间是否合理": "合理",
              "请假事由是否合规": "合规"
            }
        },
    '建议':xxx
    }
"""


bussiness_format= """
  { 'query':xxx ,   
    msg:  {
            "出发日期": "2024-09-11 09:00",
            "返回日期": "2024-09-12 18:00"
            "目的地": xxxx,
            "出差目的": xxx,
            "交通方式":xxx,
            "备注":xxx(选填)
          },
    '推理':{
            "时间隐含信息": {
                  "出发日期": xxx,
                  "返回日期": xx
                    },
            "合理性检查": {
              "出差时间是否合理": "合理",
              "出差目的": "合规"
            }
        },
    '建议':xxx
    }
"""


def determine_category(query):
    """根据查询内容确定类别"""
    # 这里需要实现一个简单的分类逻辑
    if "请假" in query or "休假" in query:
        return "请假申请"
    elif "电话" in query or "联系方式" in query:
        return "通讯录查询"
    else:
        return "闲聊"



import urllib.parse

def generate_link(msg):
    base_url = "/submit_leave_application"
    params = {
        'type': msg['假期类型'],
        'start': msg['开始时间'],
        'end': msg['结束时间'],
        'reason': msg['事由']
    }
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"


def generate_business_trip_link(trip_info, employee_info):
    base_url = "http://127.0.0.1:5000/business_trip"
    params = {
        'name': employee_info['姓名'],
        'employee_id': employee_info['工号'],
        'department': employee_info['部门'],
        'position': employee_info['职位'],
        'start_date': trip_info['出发日期'],
        'end_date': trip_info['返回日期'],
        'destination': trip_info['目的地'],
        'purpose': trip_info['出差目的'],
        'transportation': trip_info['交通方式']
    }
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'world',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def excute_sql(sql):
    data =[]
    try:
        # 连接到数据库
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # 检查 SQL 语句类型
            if sql.strip().upper().startswith('SELECT'):
                # 如果是 SELECT 语句,获取所有结果
                result = cursor.fetchall()
                print("查询结果:")
                for row in result:
                    print(row)
                    data.append(row)
                return data
            else:
                # 如果是其他类型的语句 (INSERT, UPDATE, DELETE 等)
                affected_rows = cursor.rowcount
                connection.commit()
                print(f"受影响的行数: {affected_rows}")
                return affected_rows

    except pymysql.Error as e:
        print(f"发生错误: {e}")
    finally:
        if connection:
            connection.close()
            print("数据库连接已关闭")


class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_emails, subject, body):
        # 创建邮件对象
        message = MIMEMultipart()
        message['From'] = Header(self.sender_email)
        message['Subject'] = Header(subject, 'utf-8')
        # 添加邮件正文
        message.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            # 连接到SMTP服务器
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 启用TLS加密
                server.login(self.sender_email, self.sender_password)

                # 发送邮件
                server.sendmail(self.sender_email, recipient_emails, message.as_string())
            print("邮件发送成功")
            return True
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False



weather_dict = {
    "weather": {
        "2024-09-27": "☁️",
        "2024-09-28": "🌧️",
        "2024-09-29": "☀️",
        "2024-09-30": "☁️",
        "2024-10-01": "☁️",
        "2024-10-02": "☁️",
        "2024-10-03": "☀️",
        "2024-10-04": "☀️",
        "2024-10-05": "☀️",
        "2024-10-06": "☀️",
        "2024-10-07": "☁️",
        "2024-10-08": "☁️",
        "2024-10-09": "☁️",
        "2024-10-10": "☁️",
        "2024-10-11": "☁️",
        "2024-10-12": "☀️",
        "2024-10-13": "☀️",
        "2024-10-14": "☀️",
        "2024-10-15": "☀️",
        "2024-10-16": "☀️",
        "2024-10-17": "☀️",
        "2024-10-18": "☀️",
        "2024-10-19": "☀️",
        "2024-10-20": "☀️",
        "2024-10-21": "☀️",
        "2024-10-22": "☀️",
        "2024-10-23": "☀️",
        "2024-10-24": "☀️",
        "2024-10-25": "☁️",
        "2024-10-26": "☀️",
        "2024-10-27": "☀️",
        "2024-10-28": "☀️",
        "2024-10-29": "☀️",
        "2024-10-30": "☁️",
        "2024-10-31": "☀️"
    }
}

# 定义天气图标映射
icon_mapping = {
    '晴': '☀️',
    '多云': '☁️',
    '阵雨': '🌧️',
    '阴': '🌥️',
    '小雨': '🌧️',
    '少云': '🌤️',
    '雷阵雨': '⛈️',
    '大雨': '🌧️',
    '暴雨': '🌧️',
    '雪': '❄️',
    '小雪': '🌨️',
    '大雪': '🌨️',
    '霜': '🌫️',
    '雾': '🌫️',
    '沙尘暴': '🌪️',
    '台风': '🌀',
    '热带风暴': '🌀',
    '冰雹': '🌨️',
    '强风': '💨',
    '极端天气': '🌪️'
}

def merge_schedule_and_weather(schedules):
    # 创建目标格式的字典
    result = {
        "schedules": [],
        "weather": weather_dict['weather']
    }
    # 处理日程信息
    for schedule in schedules:
        date = schedule['date']  # 日期
        activity_time = schedule['activity_time']  # 活动开始时间
        activity_description = schedule['activity_description']  # 活动描述
        activity_type = schedule['activity_type']  # 活动类型
        all_day = bool(schedule['allDay'])  # 是否全天
        out_of_town = bool(schedule['outOfTown'])  # 是否出城

        result["schedules"].append({
            "date": date,
            "activity_time": activity_time,
            "activity_description": activity_description,
            "activity_type": activity_type,
            "allDay": all_day,
            "outOfTown": out_of_town
        })
        # 查找对应的天气信息
        weather_icon = weather_dict["weather"].get(date, '☀️')  # 默认天气为晴朗
        result["weather"][date] = weather_icon
    return result