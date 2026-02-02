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
    
    # 正式课程 - 一、人像模块（4课时）
    'formal_hairstyle': {
        'title': '第 1 课：发型',
        'desc': '学习不同发型的特征与表现技巧',
        'section': 'portrait',
        'type': 'formal',
        'order': 5,
        'module': '人像'
    },
    'formal_face': {
        'title': '第 2 课：脸型',
        'desc': '掌握各种脸型的绘画要领',
        'section': 'portrait',
        'type': 'formal',
        'order': 6,
        'module': '人像'
    },
    'formal_facial_features': {
        'title': '第 3 课：五官',
        'desc': '细致描绘眼睛、鼻子、嘴巴等五官特征',
        'section': 'portrait',
        'type': 'formal',
        'order': 7,
        'module': '人像'
    },
    'formal_skin_color': {
        'title': '第 4 课：肤色',
        'desc': '学习不同肤色的表现与光影处理',
        'section': 'portrait',
        'type': 'formal',
        'order': 8,
        'module': '人像'
    },
    
    # 正式课程 - 二、体态模块（3课时）
    'formal_body_type': {
        'title': '第 5 课：体型',
        'desc': '掌握不同体型的绘画技巧',
        'section': 'posture',
        'type': 'formal',
        'order': 9,
        'module': '体态'
    },
    'formal_clothing': {
        'title': '第 6 课：服饰',
        'desc': '学习服装的搭配与细节刻画',
        'section': 'posture',
        'type': 'formal',
        'order': 10,
        'module': '体态'
    },
    'formal_accessories': {
        'title': '第 7 课：饰品',
        'desc': '学习各类饰品的表现方法',
        'section': 'posture',
        'type': 'formal',
        'order': 11,
        'module': '体态'
    },
    
    # 正式课程 - 三、场景模块（3课时）
    'formal_perspective': {
        'title': '第 8 课：远近/透视',
        'desc': '理解空间透视与景深关系',
        'section': 'scene',
        'type': 'formal',
        'order': 12,
        'module': '场景'
    },
    'formal_weather': {
        'title': '第 9 课：天气',
        'desc': '表现晴天、雨天等不同天气效果',
        'section': 'scene',
        'type': 'formal',
        'order': 13,
        'module': '场景'
    },
    'formal_location': {
        'title': '第 10 课：地点',
        'desc': '绘制各种场景环境与背景',
        'section': 'scene',
        'type': 'formal',
        'order': 14,
        'module': '场景'
    },
    
    # 正式课程 - 四、综合创作模块（5课时）
    'formal_composition1': {
        'title': '第 11 课：综合练习一',
        'desc': '人像与体态的综合应用',
        'section': 'comprehensive',
        'type': 'formal',
        'order': 15,
        'module': '综合创作'
    },
    'formal_composition2': {
        'title': '第 12 课：综合练习二',
        'desc': '人像与场景的结合创作',
        'section': 'comprehensive',
        'type': 'formal',
        'order': 16,
        'module': '综合创作'
    },
    'formal_composition3': {
        'title': '第 13 课：综合练习三',
        'desc': '多元素的整体画面构建',
        'section': 'comprehensive',
        'type': 'formal',
        'order': 17,
        'module': '综合创作'
    },
    'formal_ai_animation': {
        'title': '第 14 课：AI动画',
        'desc': '让静态作品动起来',
        'section': 'comprehensive',
        'type': 'formal',
        'order': 18,
        'module': '综合创作'
    },
    'formal_final_work': {
        'title': '第 15 课：结业作品',
        'desc': '创作并展示个人结业作品',
        'section': 'comprehensive',
        'type': 'formal',
        'order': 19,
        'module': '综合创作'
    },
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
    返回格式: [{'key': key, 'title': title}, ...]
    """
    # 按order排序
    sorted_courses = sorted(
        COURSES.items(), 
        key=lambda x: x[1].get('order', 999)
    )
    return [{'key': key, 'title': course['title']} for key, course in sorted_courses]


def get_course_display_name(key):
    """获取课程显示名称"""
    course = get_course(key)
    return course['title'] if course else '未知课程'
