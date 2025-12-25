"""
课程配置中心
统一管理所有课程信息，便于扩展
"""

# 课程列表
COURSES = {
    # 体验课程
    'character': {
        'title': '第 1 节课：人物',
        'desc': '从五官、发型、衣着等要素开始，组合出清晰的人物描述。',
        'section': 'character',
        'type': 'trial',  # trial=体验课, formal=正式课
        'order': 1  # 课程顺序
    },
    'action': {
        'title': '第 2 节课：动作',
        'desc': '学会用动词描述姿势与状态，让画面更生动。',
        'section': 'action',
        'type': 'trial',
        'order': 2
    },
    'scene': {
        'title': '第 3 节课：场景',
        'desc': '选择环境与地点，给人物一个"发生故事"的舞台。',
        'section': 'scene',
        'type': 'trial',
        'order': 3
    },
    'practice': {
        'title': '综合练习',
        'desc': '把人物 + 动作 + 场景组合成一句完整提示词，挑战更复杂的画面。',
        'section': 'mix',
        'type': 'trial',
        'order': 4
    },
    
    # 未来扩展：正式课程示例
    # 'advanced_character': {
    #     'title': '进阶课 1：高级人物设计',
    #     'desc': '深入学习人物细节刻画、光影效果和情绪表达。',
    #     'section': 'advanced_character',
    #     'type': 'formal',
    #     'order': 5
    # },
}


def get_all_courses():
    """获取所有课程"""
    return COURSES


def get_course(key):
    """获取单个课程"""
    return COURSES.get(key)


def get_courses_by_type(course_type):
    """
    按类型获取课程
    :param course_type: 'trial' 或 'formal'
    """
    return {
        key: course 
        for key, course in COURSES.items() 
        if course.get('type') == course_type
    }


def get_trial_courses():
    """获取所有体验课程"""
    return get_courses_by_type('trial')


def get_formal_courses():
    """获取所有正式课程"""
    return get_courses_by_type('formal')


def get_courses_for_qr():
    """
    获取用于二维码生成的课程列表
    返回格式: {key: title}
    """
    # 按order排序
    sorted_courses = sorted(
        COURSES.items(), 
        key=lambda x: x[1].get('order', 999)
    )
    return {key: course['title'] for key, course in sorted_courses}


def get_course_display_name(key):
    """获取课程显示名称"""
    course = get_course(key)
    return course['title'] if course else '未知课程'
