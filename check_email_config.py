#!/usr/bin/env python3
"""
邮件配置检查工具
检查邮件服务是否正确配置并测试连接
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def check_email_config():
    """检查邮件配置"""
    print("📧 邮件配置检查工具")
    print("="*50)
    
    # 加载环境变量
    load_dotenv()
    
    # 检查环境变量
    config = {
        'MAIL_SERVER': os.getenv('MAIL_SERVER'),
        'MAIL_PORT': os.getenv('MAIL_PORT'),
        'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS'),
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER')
    }
    
    print("🔍 环境变量检查:")
    for key, value in config.items():
        status = "✅ 已配置" if value else "❌ 未配置"
        display_value = value if key != 'MAIL_PASSWORD' else ('***隐藏***' if value else None)
        print(f"  {key}: {status} - {display_value}")
    
    # 检查是否所有必需配置都存在
    required_configs = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    missing_configs = [k for k in required_configs if not config[k]]
    
    if missing_configs:
        print(f"\n❌ 缺少必需配置: {', '.join(missing_configs)}")
        print("\n📝 配置步骤:")
        print("1. 编辑 .env 文件")
        print("2. 取消注释邮件配置行")
        print("3. 填入你的Gmail邮箱和应用密码")
        print("4. 重启应用程序")
        print("\n📖 详细说明请查看: EMAIL_SETUP_GUIDE.md")
        return False
    
    print("\n✅ 配置检查通过!")
    
    # 测试SMTP连接
    print("\n🔗 测试SMTP连接...")
    try:
        server = smtplib.SMTP(config['MAIL_SERVER'], int(config['MAIL_PORT'] or 587))
        if config['MAIL_USE_TLS'] != 'False':
            server.starttls()
        server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
        server.quit()
        print("✅ SMTP连接测试成功!")
        return True
    except Exception as e:
        print(f"❌ SMTP连接失败: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 检查Gmail应用密码是否正确")
        print("2. 确认已启用两步验证")
        print("3. 检查网络连接")
        return False

def test_send_email(to_email=None):
    """测试发送邮件"""
    if not to_email:
        to_email = input("\n📮 输入测试邮箱地址: ").strip()
    
    if not to_email:
        print("❌ 邮箱地址不能为空")
        return False
    
    load_dotenv()
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = os.getenv('MAIL_USERNAME')  # QQ邮箱要求使用简单格式
        msg['To'] = to_email
        msg['Subject'] = "AI创意工坊 - 邮件配置测试"
        
        body = """
        🎉 恭喜！邮件配置测试成功！
        
        这是一封来自AI创意工坊的测试邮件。
        如果你收到这封邮件，说明邮件服务已正确配置。
        
        现在家长验证邮件可以正常发送了！
        
        ---
        AI创意工坊团队
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP(os.getenv('MAIL_SERVER', 'smtp.gmail.com'), 
                             int(os.getenv('MAIL_PORT', 587)))
        if os.getenv('MAIL_USE_TLS', 'True').lower() == 'true':
            server.starttls()
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        
        text = msg.as_string()
        server.sendmail(os.getenv('MAIL_USERNAME'), to_email, text)
        server.quit()
        
        print(f"✅ 测试邮件已发送到 {to_email}")
        print("📬 请检查收件箱（可能在垃圾邮件中）")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

if __name__ == "__main__":
    print("AI创意工坊 - 邮件配置检查工具")
    print("="*50)
    
    # 检查配置
    config_ok = check_email_config()
    
    if config_ok:
        choice = input("\n🤔 是否发送测试邮件? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            test_send_email()
    
    print("\n🔧 如需帮助，请查看 EMAIL_SETUP_GUIDE.md")