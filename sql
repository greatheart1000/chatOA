# from flask import Flask, render_template
#
# app = Flask(__name__)
#
# @app.route('/')
# def home():
#     return render_template('index.html')
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=6000,debug=True)
import pymysql
from pymysql.cursors import DictCursor

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'world',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}
# 创建表的 SQL 语句
create_table_sql = """
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    position VARCHAR(50) NOT NULL,
    gender ENUM('男', '女') NOT NULL,
    phone VARCHAR(20) NOT NULL,
    wechat VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    education VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

employee_data = [
    ('张伟', '研发部', '软件工程师', '男', '13812345678', 'zhangwei_dev', 'zhangwei@company.com', '1988-07-15', '本科'),
    ('王芳', '研发部', '前端开发', '女', '13923456789', 'wangfang_frontend', 'wangfang@company.com', '1992-03-21', '硕士'),
    ('李强', '研发部', '后端开发', '男', '13734567890', 'liqiang_backend', 'liqiang@company.com', '1990-11-30', '本科'),
    ('赵静', '研发部', '测试工程师', '女', '13645678901', 'zhaojing_test', 'zhaojing@company.com', '1993-09-12', '本科'),
    ('陈明', '研发部', '架构师', '男', '13556789012', 'chenming_architect', 'chenming@company.com', '1985-05-08', '硕士'),

    ('杨丽', '市场营销部', '市场专员', '女', '13467890123', 'yangli_market', 'yangli@company.com', '1991-12-25', '本科'),
    ('周鹏', '市场营销部', '销售代表', '男', '13378901234', 'zhoupeng_sales', 'zhoupeng@company.com', '1989-08-18', '大专'),
    ('吴婷', '市场营销部', '市场分析师', '女', '13289012345', 'wuting_analyst', 'wuting@company.com', '1987-04-05', '硕士'),

    ('徐涛', '人力资源部', '招聘专员', '男', '13190123456', 'xutao_hr', 'xutao@company.com', '1992-06-14', '本科'),
    ('孙颖', '人力资源部', '培训经理', '女', '13001234567', 'sunying_training', 'sunying@company.com', '1986-02-09', '硕士'),
    ('胡杰', '人力资源部', '薪酬福利专员', '男', '13912345678', 'hujie_compensation', 'hujie@company.com', '1994-10-30', '本科'),

    ('郭敏', '财务部', '会计', '女', '13823456789', 'guomin_accounting', 'guomin@company.com', '1990-07-17', '本科'),
    ('林峰', '财务部', '财务分析师', '男', '13734567890', 'linfeng_finance', 'linfeng@company.com', '1988-01-22', '硕士'),
    ('何婷', '财务部', '审计师', '女', '13645678901', 'heting_audit', 'heting@company.com', '1991-11-08', '本科'),

    ('高磊', '客户服务部', '客服代表', '男', '13556789012', 'gaolei_service', 'gaolei@company.com', '1993-03-26', '大专'),
    ('朱莉', '客户服务部', '技术支持', '女', '13467890123', 'zhuli_support', 'zhuli@company.com', '1989-09-11', '本科'),
    ('梁辉', '客户服务部', '客户关系经理', '男', '13378901234', 'lianghui_crm', 'lianghui@company.com', '1987-05-03', '硕士'),

    ('郑璐', '产品设计部', 'UI设计师', '女', '13289012345', 'zhenglu_ui', 'zhenglu@company.com', '1992-08-15', '本科'),
    ('谢军', '产品设计部', 'UX设计师', '男', '13190123456', 'xiejun_ux', 'xiejun@company.com', '1990-04-07', '硕士'),
    ('韩雪', '产品设计部', '产品经理', '女', '13001234567', 'hanxue_pm', 'hanxue@company.com', '1988-12-23', '本科'),

    ('潘勇', '质量控制部', '质量检测员', '男', '13912345678', 'panyong_qa', 'panyong@company.com', '1991-06-09', '大专'),
    ('曹秀英', '质量控制部', '质量保证工程师', '女', '13823456789', 'caoxiuying_qe', 'caoxiuying@company.com', '1989-02-01', '本科'),
    ('冯伟', '质量控制部', '质量控制经理', '男', '13734567890', 'fengwei_qc', 'fengwei@company.com', '1985-10-18', '硕士'),

    ('董娟', '法务部', '法务专员', '女', '13645678901', 'dongjuan_legal', 'dongjuan@company.com', '1993-07-30', '本科'),
    ('蒋浩', '法务部', '合同管理师', '男', '13556789012', 'jianghao_contract', 'jianghao@company.com', '1988-03-14', '硕士'),
    ('余婉婷', '法务部', '知识产权专员', '女', '13467890123', 'yuwanting_ip', 'yuwanting@company.com', '1992-11-26', '本科'),

    ('魏凯', '公关部', '公关专员', '男', '13378901234', 'weikai_pr', 'weikai@company.com', '1990-09-05', '本科'),
    ('秦茜', '公关部', '媒体关系经理', '女', '13289012345', 'qinqian_media', 'qinqian@company.com', '1987-05-19', '硕士'),
    ('邓勇', '公关部', '危机管理专家', '男', '13190123456', 'dengyong_crisis', 'dengyong@company.com', '1984-01-08', '博士'),

    ('丁婷', '采购部', '采购专员', '女', '13001234567', 'dingting_purchase', 'dingting@company.com', '1991-11-22', '本科'),
    ('沈峰', '采购部', '供应链分析师', '男', '13912345678', 'shenfeng_supply', 'shenfeng@company.com', '1989-07-14', '硕士'),
    ('姜静', '采购部', '采购经理', '女', '13823456789', 'jiangjing_procurement', 'jiangjing@company.com', '1986-03-30', '本科'),

    ('范飞', '物流部', '物流专员', '男', '13734567890', 'fanfei_logistics', 'fanfei@company.com', '1992-10-11', '大专'),
    ('卢琳', '物流部', '仓储管理', '女', '13645678901', 'lulin_warehouse', 'lulin@company.com', '1990-06-25', '本科'),
    ('蔡刚', '物流部', '运输协调员', '男', '13556789012', 'caigang_transport', 'caigang@company.com', '1988-02-08', '本科'),

    ('田鑫', '信息技术部', 'IT支持', '男', '13467890123', 'tianxin_it', 'tianxin@company.com', '1993-04-03', '本科'),
    ('方芳', '信息技术部', '系统管理员', '女', '13378901234', 'fangfang_sysadmin', 'fangfang@company.com', '1991-08-16', '本科'),
    ('石阳', '信息技术部', '网络工程师', '男', '13289012345', 'shiyang_network', 'shiyang@company.com', '1988-12-29', '硕士'),

    ('熊婷', '战略规划部', '战略分析师', '女', '13190123456', 'xiongting_strategy', 'xiongting@company.com', '1990-01-07', '硕士'),
    ('贾博', '战略规划部', '业务发展经理', '男', '13001234567', 'jiabo_bizdev', 'jiabo@company.com', '1988-05-20', '本科'),
    ('龙晨', '战略规划部', '战略规划总监', '男', '13912345678', 'longchen_planning', 'longchen@company.com', '1983-09-02', '博士'),

    ('阎莉', '培训发展部', '培训师', '女', '13823456789', 'yanli_trainer', 'yanli@company.com', '1992-07-15', '本科'),
    ('邹强', '培训发展部', '课程开发专员', '男', '13734567890', 'zouqiang_course', 'zouqiang@company.com', '1990-11-28', '硕士'),
    ('汪婉', '培训发展部', '学习发展顾问', '女', '13645678901', 'wangwan_learning', 'wangwan@company.com', '1989-03-10', '本科'),

    ('金宇', '国际业务部', '国际销售', '男', '13556789012', 'jinyu_intlsales', 'jinyu@company.com', '1991-06-22', '本科'),
    ('萧茜', '国际业务部', '跨文化沟通专家', '女', '13467890123', 'xiaoqian_crosscultural', 'xiaoqian@company.com', '1988-10-05', '硕士'),
    ('严峰', '国际业务部', '国际市场开发', '男', '13378901234', 'yanfeng_intlmarket', 'yanfeng@company.com', '1987-02-17', '本科'),

    ('覃婷', '行政部', '行政助理', '女', '13289012345', 'qinting_admin', 'qinting@company.com', '1993-04-13', '大专'),
    ('廖勇', '行政部', '办公室管理', '男', '13190123456', 'liaoyong_office', 'liaoyong@company.com', '1990-08-26', '本科'),
    ('贺洁', '行政部', '前台接待', '女', '13001234567', 'hejie_reception', 'hejie@company.com', '1994-12-09', '大专'),

    ('袁峰', '安全管理部', '安全主管', '男', '13912345678', 'yuanfeng_safety', 'yuanfeng@company.com', '1988-06-01', '本科'),
    ('康玲', '安全管理部', '风险评估专员', '女', '13823456789', 'kangling_risk', 'kangling@company.com', '1991-10-14', '硕士'),
    ('江强', '安全管理部', '安全培训师', '男', '13734567890', 'jiangqiang_safetytrainer', 'jiangqiang@company.com', '1993-02-27', '本科'),

    ('傅芳', '环保部', '环保工程师', '女', '13645678901', 'fufang_environment', 'fufang@company.com', '1990-07-09', '本科'),
    ('钟明', '环保部', '可持续发展专员', '男', '13556789012', 'zhongming_sustainable', 'zhongming@company.com', '1992-11-22', '硕士'),
    ('唐婉', '环保部', '环境影响评估师', '女', '13467890123', 'tangwan_eia', 'tangwan@company.com', '1988-03-05', '硕士'),

    ('黄辉', '研究院', '研究员', '男', '13378901234', 'huanghui_researcher', 'huanghui@company.com', '1986-09-18', '博士'),
    ('尹琳', '研究院', '实验室技术员', '女', '13289012345', 'yinlin_labtech', 'yinlin@company.com', '1991-01-30', '硕士'),
    ('毛阳', '研究院', '项目主管', '男', '13190123456', 'maoyang_project', 'maoyang@company.com', '1985-05-12', '博士'),

    ('齐婷', '品牌管理部', '品牌专员', '女', '13001234567', 'qiting_brand', 'qiting@company.com', '1992-08-20', '本科'),
    ('文凯', '品牌管理部', '创意总监', '男', '13912345678', 'wenkai_creative', 'wenkai@company.com', '1987-12-03', '硕士'),
    ('叶莉', '品牌管理部', '品牌策略师', '女', '13823456789', 'yeli_strategy', 'yeli@company.com', '1989-04-16', '本科')
]
employee_data = [
    # 研发部
    ('刘志强', '研发部', '高级软件工程师', '男', '13912345670', 'liuzhiqiang_dev', 'liuzhiqiang@company.com', '1987-06-18', '硕士'),
    ('周雅婷', '研发部', '数据科学家', '女', '13823456781', 'zhouyating_data', 'zhouyating@company.com', '1991-09-22', '博士'),
    ('孙宇轩', '研发部', '移动开发工程师', '男', '13734567892', 'sunyuxuan_mobile', 'sunyuxuan@company.com', '1993-03-15', '本科'),
    ('林思颖', '研发部', 'DevOps工程师', '女', '13645678903', 'linsiying_devops', 'linsiying@company.com', '1990-11-30', '硕士'),
    ('王浩然', '研发部', '人工智能工程师', '男', '13556789014', 'wanghaoran_ai', 'wanghaoran@company.com', '1989-08-05', '博士'),
    ('张梦琪', '研发部', '前端开发主管', '女', '13467890125', 'zhangmengqi_frontend', 'zhangmengqi@company.com', '1988-12-10', '本科'),
    ('陈俊杰', '研发部', '后端开发主管', '男', '13378901236', 'chenjunjie_backend', 'chenjunjie@company.com', '1986-04-25', '硕士'),
    ('李雨欣', '研发部', '测试自动化工程师', '女', '13289012347', 'liyuxin_qa', 'liyuxin@company.com', '1992-07-20', '本科'),

    # 市场营销部
    ('郭晓峰', '市场营销部', '数字营销专员', '男', '13190123458', 'guoxiaofeng_digital', 'guoxiaofeng@company.com', '1993-01-08', '本科'),
    ('赵雪梅', '市场营销部', '品牌推广经理', '女', '13001234569', 'zhaoxuemei_brand', 'zhaoxuemei@company.com', '1989-05-17', '硕士'),
    ('钱俊豪', '市场营销部', '市场调研分析师', '男', '13912345670', 'qianjunhao_research', 'qianjunhao@company.com', '1991-10-03', '硕士'),
    ('唐佳怡', '市场营销部', '社交媒体运营', '女', '13823456781', 'tangjiayisocial', 'tangjiayi@company.com', '1994-02-28', '本科'),
    ('徐志远', '市场营销部', '产品营销经理', '男', '13734567892', 'xuzhiyuan_product', 'xuzhiyuan@company.com', '1987-09-12', '本科'),
    ('马思琪', '市场营销部', '客户关系主管', '女', '13645678903', 'masiqi_crm', 'masiqi@company.com', '1990-06-23', '硕士'),
    ('洪明亮', '市场营销部', '销售总监', '男', '13556789014', 'hongmingliang_sales', 'hongmingliang@company.com', '1985-11-15', '硕士')
]


insert_data_sql = "INSERT INTO employees (name, department, position, gender, phone, wechat, email, birth_date, education) VALUES " + ",".join(str(employee) for employee in employee_data)
try:
    # 连接到数据库
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        # # 创建表
        # cursor.execute(create_table_sql)
        # print("表创建成功")

        # 插入数据
        cursor.execute(insert_data_sql)
        connection.commit()
        print("数据插入成功")
        # 验证插入的数据
        cursor.execute("SELECT * FROM employees")
        results = cursor.fetchall()
        print(f"总共插入了 {len(results)} 条记录")
        for row in results:
            print(row)

except pymysql.Error as e:
    print(f"发生错误: {e}")

finally:
    if connection:
        connection.close()
        print("数据库连接已关闭")

