"""
邮件服务模块
处理家长验证邮件发送
"""

from flask import current_app
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

mail = Mail()

def init_mail(app):
    """初始化邮件服务"""
    # 配置邮件设置
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # QQ邮箱使用简单格式
    
    mail.init_app(app)


def send_verification_email(to_email, child_name, verification_code, verification_url):
    """
    发送家长验证邮件
    
    Args:
        to_email: 家长邮箱
        child_name: 孩子昵称
        verification_code: 6位验证码
        verification_url: 验证链接
    """
    subject = f"【AI创意工坊】请验证{child_name}的账户注册"
    
    # HTML邮件模板
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            .email-container {{
                max-width: 650px;
                margin: 0 auto;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 20px;
                border-radius: 15px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
                border-radius: 15px 15px 0 0;
                position: relative;
                overflow: hidden;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="30" cy="20" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="15" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="70" cy="25" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="10" r="1" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                animation: float 20s infinite linear;
            }}
            @keyframes float {{
                0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
                100% {{ transform: translate(-50%, -50%) rotate(360deg); }}
            }}
            .header-content {{
                position: relative;
                z-index: 2;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 10px;
                display: block;
            }}
            .content {{
                background: white;
                padding: 40px 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                position: relative;
            }}
            .welcome-banner {{
                background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                margin: 20px 0;
                color: #2c3e50;
            }}
            .child-avatar {{
                width: 80px;
                height: 80px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                color: white;
                margin: 0 auto 15px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }}
            .verification-section {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                margin: 30px 0;
                position: relative;
                overflow: hidden;
            }}
            .verification-section::before {{
                content: '🎨✨🎭🖌️🎪';
                position: absolute;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 20px;
                opacity: 0.3;
                letter-spacing: 20px;
            }}
            .code-container {{
                background: rgba(255,255,255,0.2);
                border: 2px dashed rgba(255,255,255,0.5);
                padding: 25px;
                border-radius: 12px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
            }}
            .code {{
                font-size: 42px;
                font-weight: bold;
                letter-spacing: 12px;
                font-family: 'Courier New', monospace;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                margin: 10px 0;
            }}
            .verify-button {{
                display: inline-block;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                color: white;
                padding: 18px 40px;
                text-decoration: none;
                border-radius: 50px;
                margin: 25px 0;
                font-weight: bold;
                font-size: 18px;
                box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .feature-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
                transform: scale(1);
                transition: transform 0.3s ease;
            }}
            .feature-icon {{
                font-size: 48px;
                margin-bottom: 15px;
                display: block;
            }}
            .feature-title {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .feature-desc {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .safety-notice {{
                background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                border-left: 5px solid #ff8a80;
                color: #2c3e50;
                padding: 25px;
                border-radius: 12px;
                margin: 25px 0;
                position: relative;
            }}
            .safety-icon {{
                position: absolute;
                top: -10px;
                right: 20px;
                font-size: 36px;
                background: #ff8a80;
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .steps-container {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 12px;
                margin: 25px 0;
            }}
            .step {{
                display: flex;
                align-items: center;
                margin: 15px 0;
                padding: 15px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .step-number {{
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-right: 15px;
            }}
            .footer {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 0 0 15px 15px;
                font-size: 14px;
            }}
            .social-links {{
                margin: 20px 0;
            }}
            .social-link {{
                display: inline-block;
                margin: 0 10px;
                font-size: 24px;
                text-decoration: none;
                color: rgba(255,255,255,0.8);
            }}
            .countdown {{
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                backdrop-filter: blur(10px);
            }}
            @media (max-width: 600px) {{
                .email-container {{ padding: 10px; }}
                .features-grid {{ grid-template-columns: 1fr; }}
                .code {{ font-size: 32px; letter-spacing: 8px; }}
                .verify-button {{ padding: 15px 30px; font-size: 16px; }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="header-content">
                    <span class="logo">🎨</span>
                    <h1 style="margin: 0; font-size: 36px;">AI创意工坊</h1>
                    <p style="margin: 10px 0 0; font-size: 18px; opacity: 0.9;">✨ 儿童AI艺术创作平台 ✨</p>
                </div>
            </div>
            
            <div class="content">
                <div class="welcome-banner">
                    <div class="child-avatar">👶</div>
                    <h2 style="margin: 0 0 10px; color: #2c3e50;">🎉 新的小艺术家加入啦！</h2>
                    <p style="margin: 0; font-size: 16px;">您的孩子 <strong style="color: #667eea;">{child_name}</strong> 想要开启AI艺术创作之旅</p>
                </div>
                
                <h2 style="color: #2c3e50; margin-top: 30px;">💌 亲爱的家长，您好！</h2>
                
                <p style="font-size: 16px; line-height: 1.8;">
                    感谢您关注AI创意工坊！我们是一个专为 <strong>10-14岁儿童</strong> 设计的安全、有趣的AI艺术创作平台。
                    孩子们可以通过上传简笔画，体验AI智能上色、3D建模和动画制作的神奇过程。
                </p>
                
                <div class="safety-notice">
                    <div class="safety-icon">🛡️</div>
                    <h3 style="margin: 0 0 15px; color: #2c3e50;">🔒 儿童安全第一</h3>
                    <p style="margin: 0; line-height: 1.6;">
                        为了保护您孩子的网络安全和隐私，我们需要获得您的许可才能激活账户。
                        所有创作内容都将受到严格的安全保护，我们承诺不会收集任何个人敏感信息。
                    </p>
                </div>
                
                <div class="verification-section">
                    <h2 style="margin: 30px 0 20px; font-size: 28px;">🎯 账户验证</h2>
                    
                    <div class="code-container">
                        <p style="margin: 0 0 10px; font-size: 18px; opacity: 0.9;">✨ 验证码 ✨</p>
                        <div class="code">{verification_code}</div>
                        <div class="countdown">
                            <p style="margin: 0; font-size: 14px; opacity: 0.8;">
                                ⏰ 验证码24小时内有效
                            </p>
                        </div>
                    </div>
                    
                    <a href="{verification_url}" class="verify-button">
                        🚀 立即验证账户
                    </a>
                </div>
                
                <div class="steps-container">
                    <h3 style="color: #2c3e50; text-align: center; margin-bottom: 25px;">📝 验证步骤</h3>
                    <div class="step">
                        <div class="step-number">1</div>
                        <div>
                            <strong>点击验证按钮</strong><br>
                            <small>点击上方蓝色按钮进入验证页面</small>
                        </div>
                    </div>
                    <div class="step">
                        <div class="step-number">2</div>
                        <div>
                            <strong>输入验证码</strong><br>
                            <small>在验证页面输入6位验证码</small>
                        </div>
                    </div>
                    <div class="step">
                        <div class="step-number">3</div>
                        <div>
                            <strong>完成验证</strong><br>
                            <small>验证成功后孩子即可开始创作</small>
                        </div>
                    </div>
                </div>
                
                <h3 style="color: #2c3e50; text-align: center; margin: 40px 0 25px;">🌟 平台特色功能</h3>
                <div class="features-grid">
                    <div class="feature-card">
                        <span class="feature-icon">🎨</span>
                        <div class="feature-title">智能上色</div>
                        <div class="feature-desc">AI为简笔画自动添加丰富色彩</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🎬</span>
                        <div class="feature-title">动态视频</div>
                        <div class="feature-desc">将静态图片转换为动态视频</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🏛️</span>
                        <div class="feature-title">3D建模</div>
                        <div class="feature-desc">自动生成精美3D模型</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🔒</span>
                        <div class="feature-title">安全保护</div>
                        <div class="feature-desc">严格的儿童隐私安全保护</div>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 30px 0; text-align: center;">
                    <h3 style="color: #2c3e50; margin: 0 0 15px;">� 温馨提示</h3>
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: left;">
                        <p style="margin: 0 0 10px; color: #555;">✅ 验证完成后，您将收到家长监护面板链接</p>
                        <p style="margin: 0 0 10px; color: #555;">✅ 您可以随时查看孩子的创作活动记录</p>
                        <p style="margin: 0 0 10px; color: #555;">✅ 所有作品数据均安全存储，绝不外泄</p>
                        <p style="margin: 0; color: #555;">✅ 支持家长权限管理和时间控制</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0; padding: 25px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 12px;">
                    <h3 style="margin: 0 0 15px;">🎪 加入我们的创作社区</h3>
                    <p style="margin: 0 0 20px; opacity: 0.9;">让孩子在安全、有趣的环境中探索AI艺术的无限可能</p>
                    <div style="margin: 20px 0;">
                        <span style="margin: 0 10px; font-size: 24px;">🎨</span>
                        <span style="margin: 0 10px; font-size: 24px;">🎬</span>
                        <span style="margin: 0 10px; font-size: 24px;">🏛️</span>
                        <span style="margin: 0 10px; font-size: 24px;">✨</span>
                    </div>
                </div>
                
                <p style="color: #666; text-align: center; margin: 30px 0; font-style: italic;">
                    如果您没有申请此账户注册，请忽略此邮件。我们不会向您发送更多邮件。
                </p>
                
                <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0 0 10px; color: #333; font-weight: bold;">📞 需要帮助？</p>
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        如有任何疑问，请联系我们的客服团队<br>
                        我们将竭诚为您和孩子提供最好的服务体验
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #667eea; font-weight: bold; margin: 0;">
                        🌟 祝愿您的孩子在AI创意工坊收获满满的快乐与成长！
                    </p>
                </div>
            </div>
            
            <div class="footer">
                <h3 style="margin: 0 0 15px;">🎨 AI创意工坊</h3>
                <p style="margin: 0 0 10px; font-size: 16px; opacity: 0.9;">让每个孩子都成为小小创作家</p>
                <p style="margin: 0 0 20px; font-size: 14px; opacity: 0.8;">专为10-14岁儿童设计的AI艺术创作平台</p>
                
                <div class="social-links">
                    <span class="social-link">🌐</span>
                    <span class="social-link">📧</span>
                    <span class="social-link">📱</span>
                </div>
                
                <p style="margin: 20px 0 0; font-size: 12px; opacity: 0.7;">
                    此邮件由系统自动发送，请勿回复<br>
                    如果无法点击按钮，请复制以下链接到浏览器：<br>
                    <span style="word-break: break-all; color: rgba(255,255,255,0.9);">{verification_url}</span>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 文本版本（备用）
    text_body = f"""
    亲爱的家长，您好！

    您的孩子 {child_name} 正在申请注册AI创意工坊账户。

    验证码：{verification_code}

    请访问以下链接完成验证：
    {verification_url}

    AI创意工坊是一个专为10-14岁儿童设计的AI艺术创作平台。

    如果您没有申请此账户，请忽略此邮件。

    AI创意工坊团队
    """
    
    try:
        # 使用Flask-Mail发送
        if current_app.config.get('MAIL_USERNAME'):
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body,
                body=text_body
            )
            mail.send(msg)
            return True
        else:
            # 如果没有配置SMTP，记录到日志（开发环境）
            current_app.logger.info(f"邮件发送模拟 - 收件人: {to_email}")
            current_app.logger.info(f"验证码: {verification_code}")
            current_app.logger.info(f"验证链接: {verification_url}")
            print(f"\\n=== 邮件发送模拟 ===")
            print(f"收件人: {to_email}")
            print(f"验证码: {verification_code}")
            print(f"验证链接: {verification_url}")
            print(f"===================\\n")
            return True
            
    except Exception as e:
        current_app.logger.error(f"发送邮件失败: {str(e)}")
        return False


def send_welcome_email(to_email, child_name, parent_dashboard_url):
    """
    发送欢迎邮件（验证成功后）
    
    Args:
        to_email: 家长邮箱
        child_name: 孩子昵称
        parent_dashboard_url: 家长监护面板链接
    """
    subject = f"【AI创意工坊】欢迎{child_name}加入我们的创意大家庭！"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: white;
                padding: 30px;
                border: 1px solid #e0e0e0;
            }}
            .button {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 8px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 10px 10px;
                color: #666;
                font-size: 14px;
            }}
            .features {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>🎉 欢迎加入AI创意工坊！</h1>
                <p>让创意无限绽放</p>
            </div>
            
            <div class="content">
                <h2>恭喜！验证成功</h2>
                
                <p>亲爱的家长，<strong>{child_name}</strong> 的账户已成功验证，现在可以开始AI创作之旅了！</p>
                
                <div class="features">
                    <h3>🎨 孩子可以体验的功能：</h3>
                    <ul>
                        <li><strong>简笔画上色：</strong>上传手绘作品，AI智能添加色彩</li>
                        <li><strong>Expert模式：</strong>通过文字描述直接生成艺术作品</li>
                        <li><strong>视频生成：</strong>将静态图片转换为动态视频</li>
                        <li><strong>3D模型：</strong>从2D图片生成立体3D模型</li>
                        <li><strong>作品展示：</strong>在安全的环境中分享创意成果</li>
                    </ul>
                </div>
                
                <h3>👨‍👩‍👧‍👦 家长监护功能</h3>
                <p>我们为您提供了专门的家长监护面板，您可以：</p>
                <ul>
                    <li>查看孩子的创作活动和作品</li>
                    <li>监控使用时间和频率</li>
                    <li>设置隐私和分享权限</li>
                    <li>接收重要通知和更新</li>
                </ul>
                
                <div style="text-align: center;">
                    <a href="{parent_dashboard_url}" class="button">访问家长监护面板</a>
                </div>
                
                <h3>🔒 安全承诺</h3>
                <ul>
                    <li>严格遵循儿童在线隐私保护法规</li>
                    <li>所有数据加密存储，绝不外泄</li>
                    <li>AI内容安全检测，确保适宜性</li>
                    <li>24/7客服支持，随时解答疑问</li>
                </ul>
                
                <p>感谢您的信任！让我们一起陪伴孩子探索AI艺术的无限可能。</p>
                
                <p>祝愉快，<br>AI创意工坊团队</p>
            </div>
            
            <div class="footer">
                <p>AI创意工坊 - 让每个孩子都成为小小创作家</p>
                <p>如有任何问题，请联系客服或访问帮助中心</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        if current_app.config.get('MAIL_USERNAME'):
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body
            )
            mail.send(msg)
        else:
            current_app.logger.info(f"欢迎邮件发送模拟 - 收件人: {to_email}")
            print(f"\\n=== 欢迎邮件发送模拟 ===")
            print(f"收件人: {to_email}")
            print(f"家长面板: {parent_dashboard_url}")
            print(f"=====================\\n")
        return True
    except Exception as e:
        current_app.logger.error(f"发送欢迎邮件失败: {str(e)}")
        return False