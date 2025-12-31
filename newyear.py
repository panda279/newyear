import streamlit as st
import random
import math
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 页面配置
st.set_page_config(
    page_title="2026马年跨年烟花",
    page_icon="🎆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS - 移动端优化
st.markdown("""
<style>
    /* 移动端适配 */
    @media (max-width: 768px) {
        .main-title { 
            font-size: 1.5rem !important; 
            padding: 0.8rem !important;
            margin-bottom: 1rem !important;
        }
        .firework-display {
            height: 300px !important;
            min-height: 300px !important;
        }
        .control-section {
            padding: 0.5rem !important;
        }
        .blessing-button {
            padding: 0.4rem 0.6rem !important;
            font-size: 0.9rem !important;
            margin: 0.2rem !important;
        }
        .mobile-hide {
            display: none !important;
        }
    }
    
    /* 主标题 */
    .main-title {
        background: linear-gradient(135deg, #0c0032, #3500d3);
        color: #FFD166;
        text-align: center;
        padding: 1.2rem;
        border-radius: 15px;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px #FF3366;
        border: 2px solid #FFD166;
    }
    
    /* 烟花显示区域 */
    .firework-display {
        background: linear-gradient(135deg, #0c0032 0%, #190061 30%, #240090 70%, #3500d3 100%);
        border-radius: 10px;
        padding: 10px;
        height: 400px;
        min-height: 400px;
        border: 2px solid #FFD166;
        position: relative;
        overflow: hidden;
    }
    
    /* 控制区域 */
    .control-section {
        background: rgba(12, 0, 50, 0.8);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #FFD166;
    }
    
    /* 祝福语按钮 */
    .blessing-button {
        background: linear-gradient(135deg, rgba(255, 51, 102, 0.8), rgba(255, 209, 102, 0.8));
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.6rem 1rem;
        margin: 0.3rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        display: inline-block;
        width: 100%;
    }
    
    .blessing-button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255, 209, 102, 0.5);
    }
    
    /* 状态标签 */
    .status-tag {
        display: inline-block;
        background: rgba(255, 209, 102, 0.2);
        color: #FFD166;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    
    /* 祝福语卡片 */
    .blessing-card {
        background: rgba(255, 209, 102, 0.1);
        border: 1px solid rgba(255, 209, 102, 0.3);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        text-align: center;
        color: #FFD166;
        font-size: 1.1rem;
    }
    
    /* 移动端底部导航 */
    .mobile-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(12, 0, 50, 0.95);
        padding: 0.5rem;
        display: flex;
        justify-content: space-around;
        z-index: 1000;
        border-top: 2px solid #FFD166;
    }
    
    .nav-button {
        background: none;
        border: none;
        color: #FFD166;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
def init_session_state():
    if 'fireworks' not in st.session_state:
        st.session_state.fireworks = []
    if 'stars' not in st.session_state:
        st.session_state.stars = []
        # 初始化星星
        for _ in range(50):
            st.session_state.stars.append({
                'x': random.random(),
                'y': random.random(),
                'size': random.uniform(0.5, 2),
                'brightness': random.uniform(0.3, 0.8),
                'speed': random.uniform(0.002, 0.005)
            })
    if 'auto_mode' not in st.session_state:
        st.session_state.auto_mode = True
    if 'next_blessing' not in st.session_state:
        st.session_state.next_blessing = 0
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()

# 祝福语列表
BLESSINGS = [
    "🎉 元旦快乐", "🐴 马年大吉", "✨ 万事如意", "🎯 心想事成",
    "💰 恭喜发财", "💪 身体健康", "🚀 龙马精神", "🏆 一马当先",
    "🎁 马上有福", "🌟 马到成功", "🎊 年年有余", "👨‍👩‍👧‍👦 阖家幸福"
]

# 颜色列表
FIREWORK_COLORS = [
    (255, 209, 102),  # 金色
    (255, 51, 102),   # 红色
    (52, 152, 219),   # 蓝色
    (46, 204, 113),   # 绿色
    (155, 89, 182),   # 紫色
    (230, 126, 34),   # 橙色
    (255, 105, 180),  # 粉色
    (0, 255, 255),    # 青色
]

def create_firework(x, y, is_blessing=False, text=""):
    """创建一个烟花"""
    return {
        'x': x,
        'y': y,
        'color': random.choice(FIREWORK_COLORS),
        'velocity': random.uniform(-0.5, -0.3),
        'exploded': False,
        'particles': [],
        'life': 100,
        'is_blessing': is_blessing,
        'text': text,
        'text_alpha': 0,
        'show_text': False,
        'created_at': time.time()
    }

def update_fireworks():
    """更新烟花状态"""
    current_time = time.time()
    
    # 更新星星
    for star in st.session_state.stars:
        star['brightness'] = 0.5 + 0.5 * math.sin(current_time * star['speed'] * math.pi)
    
    # 自动发射祝福语
    if st.session_state.auto_mode:
        if current_time - st.session_state.next_blessing > 4:  # 每4秒一个
            text = random.choice(BLESSINGS)
            # 在随机位置发射
            x = random.uniform(0.2, 0.8)
            st.session_state.fireworks.append(create_firework(x * 600, 400, True, text))
            st.session_state.next_blessing = current_time
    
    # 更新烟花
    for firework in st.session_state.fireworks[:]:
        if not firework['exploded']:
            # 上升阶段
            firework['y'] += firework['velocity'] * 20
            firework['velocity'] += 0.008
            firework['life'] -= 1
            
            # 检查是否爆炸
            if firework['life'] <= 0 or firework['velocity'] >= 0:
                firework['exploded'] = True
                # 创建爆炸粒子
                for _ in range(80):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(0.5, 2.5)
                    firework['particles'].append({
                        'x': firework['x'],
                        'y': firework['y'],
                        'vx': math.cos(angle) * speed,
                        'vy': math.sin(angle) * speed,
                        'life': random.uniform(60, 100),
                        'color': firework['color'],
                        'size': random.uniform(1.5, 3)
                    })
        else:
            # 更新粒子
            for particle in firework['particles'][:]:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.04
                particle['vx'] *= 0.98
                particle['life'] -= 1
                
                if particle['life'] <= 0:
                    firework['particles'].remove(particle)
            
            # 显示文字
            if firework['is_blessing']:
                if len(firework['particles']) < 30:
                    firework['show_text'] = True
                
                if firework['show_text'] and firework['text_alpha'] < 255:
                    firework['text_alpha'] += 4
        
        # 移除旧烟花
        if current_time - firework['created_at'] > 10:  # 10秒后移除
            st.session_state.fireworks.remove(firework)

def create_firework_image(width=600, height=400):
    """创建烟花图像"""
    # 创建背景
    image = Image.new('RGBA', (width, height), (12, 0, 50, 255))
    draw = ImageDraw.Draw(image)
    
    # 绘制星星
    for star in st.session_state.stars:
        brightness = int(255 * star['brightness'])
        x = int(star['x'] * width)
        y = int(star['y'] * height)
        radius = int(star['size'])
        
        # 绘制星星
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                    fill=(brightness, brightness, brightness, 180))
    
    # 绘制烟花
    for firework in st.session_state.fireworks:
        if not firework['exploded']:
            # 上升的烟花
            r, g, b = firework['color']
            for i in range(4, 0, -1):
                alpha = int(200 * (i/4))
                draw.ellipse([
                    firework['x'] - i, firework['y'] - i,
                    firework['x'] + i, firework['y'] + i
                ], fill=(r, g, b, alpha))
        else:
            # 爆炸粒子
            for particle in firework['particles']:
                if particle['life'] > 0:
                    alpha = int(255 * (particle['life'] / 100))
                    r, g, b = particle['color']
                    size = particle['size'] * (particle['life'] / 100)
                    
                    # 绘制粒子
                    draw.ellipse([
                        particle['x'] - size, particle['y'] - size,
                        particle['x'] + size, particle['y'] + size
                    ], fill=(r, g, b, alpha))
            
            # 绘制祝福文字
            if firework['is_blessing'] and firework['show_text']:
                try:
                    # 创建文字图像
                    font_size = 28
                    try:
                        font = ImageFont.truetype("simhei.ttf", font_size)
                    except:
                        try:
                            font = ImageFont.truetype("arial.ttf", font_size)
                        except:
                            font = ImageFont.load_default()
                    
                    # 计算文字位置
                    bbox = draw.textbbox((0, 0), firework['text'], font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    text_x = firework['x'] - text_width // 2
                    text_y = firework['y'] - text_height // 2
                    
                    # 绘制发光效果
                    for i in range(3, 0, -1):
                        glow_alpha = firework['text_alpha'] // (i * 2)
                        glow_color = (255, 200, 100, glow_alpha)
                        
                        # 绘制文字
                        draw.text((text_x, text_y), firework['text'], 
                                fill=glow_color, font=font)
                except:
                    pass
    
    return image

def main():
    # 初始化
    init_session_state()
    
    # 更新烟花状态
    update_fireworks()
    
    # 标题
    st.markdown('<div class="main-title">🎆 2026马年跨年烟花祝福 🐴</div>', unsafe_allow_html=True)
    
    # 响应式布局
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown('<div class="control-section">', unsafe_allow_html=True)
        st.markdown("### 🎯 控制面板")
        
        # 状态显示
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f'<div class="status-tag">🎆 {len(st.session_state.fireworks)}个烟花</div>', 
                       unsafe_allow_html=True)
        with col_b:
            mode_text = "自动" if st.session_state.auto_mode else "手动"
            st.markdown(f'<div class="status-tag">🔄 {mode_text}模式</div>', 
                       unsafe_allow_html=True)
        
        # 模式切换
        auto_mode = st.toggle("自动发射祝福语", value=st.session_state.auto_mode)
        if auto_mode != st.session_state.auto_mode:
            st.session_state.auto_mode = auto_mode
        
        st.markdown("---")
        st.markdown("### 🎇 发射祝福")
        
        # 祝福语按钮网格
        cols = st.columns(2)
        for idx, blessing in enumerate(BLESSINGS[:8]):  # 只显示前8个
            with cols[idx % 2]:
                if st.button(blessing, key=f"btn_{idx}", use_container_width=True):
                    x = random.uniform(0.2, 0.8) * 600
                    st.session_state.fireworks.append(create_firework(x, 400, True, blessing))
        
        st.markdown("---")
        st.markdown("### ⚡ 快速操作")
        
        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("🎆 发射烟花", use_container_width=True):
                for _ in range(3):
                    x = random.uniform(0.1, 0.9) * 600
                    st.session_state.fireworks.append(create_firework(x, 400))
        
        with col_d:
            if st.button("🧹 清空", use_container_width=True):
                st.session_state.fireworks = []
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="firework-display">', unsafe_allow_html=True)
        st.markdown("### 🎇 烟花展示区")
        
        # 生成并显示烟花图像
        firework_img = create_firework_image()
        st.image(firework_img, use_column_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 移动端提示
        st.markdown("""
        <div style="text-align: center; color: #FFD166; padding: 0.5rem; font-size: 0.9rem;">
        📱 点击左侧按钮发射对应祝福烟花
        </div>
        """, unsafe_allow_html=True)
    
    # 祝福语录区域
    st.markdown("---")
    st.markdown("### 📜 祝福语录")
    
    # 显示所有祝福语
    cols = st.columns(4)
    for idx, blessing in enumerate(BLESSINGS):
        with cols[idx % 4]:
            if st.button(blessing, key=f"card_{idx}", use_container_width=True):
                x = random.uniform(0.2, 0.8) * 600
                st.session_state.fireworks.append(create_firework(x, 400, True, blessing))
    
    # 马年特别祝福
    st.markdown("---")
    st.markdown("### 🐴 马年特辑")
    
    horse_blessings = ["马到成功", "龙马精神", "一马当先", "万马奔腾", "马上有福", "马年吉祥"]
    for hb in horse_blessings:
        st.markdown(f'<div class="blessing-card">🎠 {hb}</div>', unsafe_allow_html=True)
    
    # 底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
    🎆 2026马年跨年烟花祝福系统 | 祝您新年快乐，万事如意！ 🐴
    </div>
    """, unsafe_allow_html=True)
    
    # 自动刷新（模拟动画）
    time.sleep(0.05)
    st.rerun()

if __name__ == "__main__":
    main()
