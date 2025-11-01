from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, make_response
from multi_agent import WorkAssistant
import json
from memory import AgentMemory
from util import determine_category
import urllib.parse
import requests
from datetime import datetime
import os
import base64
from functools import wraps

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache

app = Flask(__name__)
app.secret_key = 'your_secret_key'
assistant = WorkAssistant(user_name="张三", filename='short_term_memory.json')
memory = AgentMemory('short_term_memory.json')

USER_INFO = {
    'employee_id': '12345',
    'employee_name': '张三',
    'department': '技术部',
    'position': '软件工程师'
}

@app.route('/')
def index():
    session['user_info'] = USER_INFO
    return render_template('index.html')

# 快捷入口路由 - 使用stitch风格的页面
@app.route('/quick/leave')
@nocache
def quick_leave():
    """快捷请假入口"""
    return render_template('leaveForm.html',
                           leave_type='',
                           start_time='',
                           end_time='',
                           reason='',
                           name=USER_INFO['employee_name'],
                           employee_id=USER_INFO['employee_id'])

@app.route('/quick/contact')
@nocache
def quick_contact():
    """快捷通讯录查询入口"""
    return render_template('contact.html', user_info=USER_INFO)

@app.route('/quick/email')
@nocache
def quick_email():
    """快捷邮箱入口"""
    return render_template('quick_email.html', user_info=USER_INFO)

@app.route('/quick/trip')
@nocache
def quick_trip():
    """快捷出差入口"""
    return render_template('business_trip.html',
                           name=USER_INFO['employee_name'],
                           employeeId=USER_INFO['employee_id'],
                           department=USER_INFO['department'],
                           position=USER_INFO['position'],
                           startDate='',
                           endDate='',
                           destination='',
                           purpose='',
                           transportation='')

@app.route('/quick/schedule')
@nocache
def quick_schedule():
    """快捷日程查询入口"""
    return render_template('schedule.html', schedule_data=json.dumps({"schedules": [], "weather": {}}))

@app.route('/get_user_info')
def get_user_info():
    return jsonify(USER_INFO)

@app.route('/submit_leave', methods=['POST'])
def submit_leave():
    data = request.json
    leave_data = {**USER_INFO, **data}
    result = assistant.submit_leave_application(leave_data)
    return jsonify(result)

@app.route('/submit_business_trip', methods=['POST'])
def submit_business_trip():
    data = request.json
    trip_data = {**USER_INFO, **data}
    result = assistant.submit_business_trip_application(trip_data)
    return jsonify(result)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    query = data.get('message', '')
    context = memory.get_context()
    response = assistant.process_query(query, context)
    print('后端发送给前端的响应:', response)
    
    memory.update_memory(query, response)
    memory.save_memory()

    # 如果有链接，添加到答案中
    if 'link' in response and response['link']:
        link_texts = {
            1: '点击打开请假申请页面',
            2: '点击打开通讯录查询页面',
            3: '点击打开邮件发送页面',
            4: '点击打开出差申请页面',
            5: '点击打开日程管理页面'
        }
        link_text = link_texts.get(response.get('intent', 0), '点击打开页面')
        response['answer'] += f' <a href="{response["link"]}" target="_blank" class="bot-link">**{link_text}**</a>'

    print('最终的response', response)
    return jsonify(response)

@app.route('/business_trip')
def business_trip():
    trip_info = {
        'employeeName': request.args.get('name'),
        'employeeId': request.args.get('employee_id'),
        'department': request.args.get('department'),
        'position': request.args.get('position'),
        'startDate': request.args.get('start_date'),
        'endDate': request.args.get('end_date'),
        'destination': request.args.get('destination'),
        'purpose': request.args.get('purpose'),
        'transportation': request.args.get('transportation')
    }
    return render_template('business_trip.html', **trip_info)

@app.route('/leave_application')
def leave_application():
    """请假申请路由"""
    leave_type = request.args.get('leave_type', '')
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')
    reason = request.args.get('reason', '')
    return render_template('leaveForm.html',
                           leave_type=leave_type,
                           start_time=start_time,
                           end_time=end_time,
                           reason=reason,
                           name=USER_INFO['employee_name'],
                           employee_id=USER_INFO['employee_id'])

@app.route('/leaveForm')
def leave_form():
    """请假表单路由"""
    leave_type = request.args.get('type', '')
    start_time = request.args.get('start', '')
    end_time = request.args.get('end', '')
    reason = request.args.get('reason', '')
    return render_template('leaveForm.html',
                           leave_type=leave_type,
                           start_time=start_time,
                           end_time=end_time,
                           reason=reason,
                           name=USER_INFO['employee_name'],
                           employee_id=USER_INFO['employee_id'])

# 已简化：通讯录查询现在通过 /quick/contact 直接跳转页面
# 如需查询功能，可以在聊天中识别意图后跳转到 /quick/contact 页面

@app.route('/show_contact_info/<encrypted_data>')
def show_contact_info(encrypted_data):
    try:
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode()).decode()
        data = json.loads(decoded_data)
        if isinstance(data, list):
            if len(data) == 1:
                # 单个人的查询结果
                return render_template('person_info.html', person=data[0])
            else:
                # 多人（部门）查询结果
                return render_template('department_info.html', persons=data)
        else:
            # 单个人的查询结果（当数据直接是一个字典时）
            return render_template('person_info.html', person=data)
    except Exception as e:
        return jsonify({"error": "Invalid data"}), 400

@app.route('/schedule_search', methods=['POST'])
def schedule_search():
    query = request.form.get('query')
    print('schedule_search query',query)
    context = request.form.get('context', '')
    response = assistant.process_query(query, context)
    print('response',response)
    return jsonify(response)

@app.route('/calendar/<encrypted_data>')
def calendar(encrypted_data):
    """日程路由"""
    try:
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode()).decode()
        schedule_data = json.loads(decoded_data)
        return render_template('schedule.html', schedule_data=json.dumps(schedule_data))
    except Exception as e:
        return jsonify({"error": "Invalid data"}), 400

@app.route('/get_schedule_data')
def get_schedule_data():
    schedule_data = session.get('schedule_data', [])
    return jsonify(schedule_data)

@app.route('/get_weather_data')
def get_weather_data():
    month = int(request.args.get('month', datetime.now().month))
    year = int(request.args.get('year', datetime.now().year))
    weather_data = get_or_fetch_weather_data(year, month)
    return jsonify(weather_data)

def get_or_fetch_weather_data(year, month):
    file_name = f"weather_data_{year}_{month:02d}.json"
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    else:
        url = "https://api.qweather.com/v7/weather/30d"
        params = {
            "location": "101280601",  # 深圳的LocationID
            "key": "64109ff4f3c04780878d413b7db1be5d"  # 您的API密钥
        }
        try:
            response = requests.get(url, params=params)
            weather_data = response.json()
            simplified_data = []
            for day in weather_data['daily']:
                if day['fxDate'].startswith(f"{year}-{month:02d}"):
                    simplified_data.append({
                        'date': day['fxDate'],
                        'weather': day['textDay'],
                        'tempMin': day['tempMin'],
                        'tempMax': day['tempMax'],
                        'iconDay': day['iconDay']
                    })
            with open(file_name, 'w') as file:
                json.dump(simplified_data, file)
            return simplified_data
        except Exception as e:
            print(f"获取天气数据时发生错误: {e}")
            return []

#和风天气 Private KEY   319a785af03b493da8cb8090f15d8179

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon1.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/show_leave_form/<encrypted_data>')
@nocache
def show_leave_form(encrypted_data):
    try:
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode()).decode()
        leave_info = json.loads(decoded_data)
        print("Decoded leave info:", leave_info)  # 添加调试输出
        return render_template('leaveForm.html',
                               leave_type=leave_info.get('假期类型', ''),
                               start_time=leave_info.get('开始时间', ''),
                               end_time=leave_info.get('结束时间', ''),
                               reason=leave_info.get('事由', ''),
                               name=USER_INFO['employee_name'],
                               employee_id=USER_INFO['employee_id'])
    except Exception as e:
        print(f"Error in show_leave_form: {e}")  # 添加错误日志
        return jsonify({"error": str(e)}), 400

@app.route('/show_business_trip_form/<encrypted_data>')
@nocache
def show_business_trip_form(encrypted_data):
    try:
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode()).decode()
        trip_info = json.loads(decoded_data)
        print("Decoded trip info:", trip_info)  # 添加调试输出
        return render_template('business_trip.html',
                               name=USER_INFO['employee_name'],
                               employeeId=USER_INFO['employee_id'],
                               department=USER_INFO['department'],
                               position=USER_INFO['position'],
                               startDate=trip_info.get('出发日期', ''),
                               endDate=trip_info.get('返回日期', ''),
                               destination=trip_info.get('目的地', ''),
                               purpose=trip_info.get('出差目的', ''),
                               transportation=trip_info.get('交通方式', ''))
    except Exception as e:
        print(f"Error in show_business_trip_form: {e}")  # 添加错误日志
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)