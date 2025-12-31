import streamlit as st
import pygame
import random
import math
import sys
import io
from PIL import Image
import numpy as np
from pygame.locals import *

# 初始化pygame（用于渲染）
pygame.init()

# 设置颜色
COLORS = {
    'background': (12, 0, 50),
    'gold': (255, 209, 102),
    'red': (255, 51, 102),
    'blue': (52, 152, 219),
    'green': (46, 204, 113),
    'purple': (155, 89, 182),
    'orange': (230, 126, 34),
    'pink': (255, 105, 180),
    'cyan': (0, 255, 255),
    'white': (255, 255, 255)
}

# Streamlit页面配置
st.set_page_config(
    page_title="2026马年跨年烟花",
    page_icon="🎆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS适应移动端
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        .main-header {
            font-size: 1.5rem !important;
            padding: 0.5rem !important;
        }
        .blessing-text {
            font-size: 1.2rem !important;
            padding: 0.3rem !important;
        }
        .control-button {
            padding: 0.3rem 0.6rem !important;
            font-size: 0.8rem !important;
            margin: 0.2rem !important;
        }
    }
    
    .main-header {
        text-align: center;
        color: #FFD166;
        padding: 1rem;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 0 0 10px #FF3366;
        background: linear-gradient(135deg, #0c0032, #3500d3);
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .blessing-text {
        background: rgba(255, 209, 102, 0.1);
        padding: 0.8rem;
        border-radius: 15px;
        border-left: 4px solid #FFD166;
        margin: 0.5rem 0;
        font-size: 1.5rem;
        color: #FFD166;
        text-align: center;
    }
    
    .control-button {
        background: linear-gradient(135deg, #FF3366, #FFD166);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        margin: 0.3rem;
        width: 100%;
    }
    
    .control-button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255, 209, 102, 0.5);
    }
    
    .firework-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 500px;
        background: linear-gradient(135deg, #0c0032 0%, #190061 30%, #240090 70%, #3500d3 100%);
        border-radius: 15px;
        overflow: hidden;
        position: relative;
    }
    
    .status-indicator {
        padding: 0.5rem;
        background: rgba(255, 51, 102, 0.2);
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
        color: #FFD166;
    }
</style>
""", unsafe_allow_html=True)

# 烟花模拟类
class FireworkSimulation:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.particles = []
        self.fireworks = []
        self.stars = []
        self.blessing_texts = []
        self.last_firework_time = 0
        self.firework_interval = 1000
        self.blessing_index = 0
        
        # 祝福语列表
        self.blessings = [
            "元旦快乐", "马年大吉", "万事如意", "心想事成",
            "恭喜发财", "身体健康", "龙马精神", "一马当先"
        ]
        
        # 初始化星星
        self.init_stars()
    
    def init_stars(self):
        """初始化背景星星"""
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.uniform(0.5, 2),
                'brightness': random.uniform(0.3, 1.0),
                'speed': random.uniform(0.01, 0.05),
                'phase': random.uniform(0, math.pi * 2)
            })
    
    def update_stars(self):
        """更新星星"""
        for star in self.stars:
            star['phase'] += star['speed']
            star['brightness'] = 0.5 + 0.5 * math.sin(star['phase'])
    
    def create_firework(self, x=None, y=None, is_blessing=False, text=""):
        """创建一个烟花"""
        if x is None:
            x = random.randint(100, self.width - 100)
        if y is None:
            y = self.height + 50
            
        color = random.choice(list(COLORS.values())[1:])
        
        firework = {
            'x': x,
            'y': y,
            'color': color,
            'velocity_y': random.uniform(-12, -8),
            'velocity_x': random.uniform(-1, 1),
            'exploded': False,
            'particles': [],
            'trail': [],
            'is_blessing': is_blessing,
            'text': text,
            'text_alpha': 0,
            'show_text': False
        }
        
        self.fireworks.append(firework)
    
    def create_blessing_firework(self):
        """创建祝福语烟花"""
        if self.blessing_index < len(self.blessings):
            text = self.blessings[self.blessing_index]
            self.blessing_index = (self.blessing_index + 1) % len(self.blessings)
            
            # 在随机位置创建祝福语烟花
            x = random.randint(200, self.width - 200)
            y = random.randint(100, self.height - 100)
            
            self.create_firework(x, self.height + 50, True, text)
            return text
        return None
    
    def update(self, current_time):
        """更新所有元素"""
        # 更新星星
        self.update_stars()
        
        # 自动创建随机烟花
        if current_time - self.last_firework_time > self.firework_interval:
            self.create_firework()
            self.last_firework_time = current_time
        
        # 更新烟花
        for firework in self.fireworks[:]:
            if not firework['exploded']:
                # 上升阶段
                firework['y'] += firework['velocity_y']
                firework['x'] += firework['velocity_x']
                firework['velocity_y'] += 0.2
                
                # 添加轨迹
                firework['trail'].append((firework['x'], firework['y']))
                if len(firework['trail']) > 15:
                    firework['trail'].pop(0)
                
                # 检查是否需要爆炸
                if firework['velocity_y'] >= 0:
                    self.explode_firework(firework)
            else:
                # 更新爆炸粒子
                for particle in firework['particles'][:]:
                    particle['x'] += particle['velocity_x']
                    particle['y'] += particle['velocity_y']
                    particle['velocity_y'] += particle['gravity']
                    particle['velocity_x'] *= 0.99
                    particle['life'] -= particle['decay']
                    
                    if particle['life'] <= 0:
                        firework['particles'].remove(particle)
                
                # 显示文字
                if firework['is_blessing'] and not firework['show_text']:
                    if len(firework['particles']) < 50:
                        firework['show_text'] = True
                
                if firework['show_text'] and firework['text_alpha'] < 255:
                    firework['text_alpha'] += 5
        
        # 移除已经完成的烟花
        self.fireworks = [f for f in self.fireworks 
                         if not (f['exploded'] and f['show_text'] and f['text_alpha'] >= 255 and len(f['particles']) == 0)]
    
    def explode_firework(self, firework):
        """烟花爆炸"""
        firework['exploded'] = True
        
        # 创建爆炸粒子
        particles_count = 200 if not firework['is_blessing'] else 300
        
        for _ in range(particles_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 8)
            
            particle = {
                'x': firework['x'],
                'y': firework['y'],
                'color': firework['color'],
                'velocity_x': math.cos(angle) * speed,
                'velocity_y': math.sin(angle) * speed,
                'size': random.uniform(1.5, 3),
                'gravity': 0.1,
                'life': 255,
                'decay': random.uniform(1, 3)
            }
            
            firework['particles'].append(particle)
    
    def render(self):
        """渲染场景到Surface"""
        # 创建Surface
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 绘制背景
        surface.fill((0, 0, 0, 0))
        bg = pygame.Surface((self.width, self.height))
        bg.fill(COLORS['background'])
        surface.blit(bg, (0, 0))
        
        # 绘制星星
        for star in self.stars:
            brightness = int(255 * star['brightness'])
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, 
                             (int(star['x']), int(star['y'])), 
                             star['size'])
        
        # 绘制烟花
        for firework in self.fireworks:
            if not firework['exploded']:
                # 绘制轨迹
                for i, (trail_x, trail_y) in enumerate(firework['trail']):
                    alpha = int(255 * (i / len(firework['trail'])))
                    radius = max(1, int(2 * (i / len(firework['trail']))))
                    color = firework['color']
                    pygame.draw.circle(surface, color, 
                                     (int(trail_x), int(trail_y)), 
                                     radius)
                
                # 绘制上升的火花
                pygame.draw.circle(surface, firework['color'], 
                                 (int(firework['x']), int(firework['y'])), 4)
                pygame.draw.circle(surface, COLORS['white'], 
                                 (int(firework['x']), int(firework['y'])), 2)
            else:
                # 绘制爆炸粒子
                for particle in firework['particles']:
                    if particle['life'] > 0:
                        alpha = min(255, int(particle['life']))
                        radius = max(1, int(particle['size'] * (particle['life'] / 255)))
                        
                        # 绘制粒子
                        pygame.draw.circle(surface, particle['color'], 
                                         (int(particle['x']), int(particle['y'])), 
                                         radius)
                
                # 绘制祝福语文字
                if firework['is_blessing'] and firework['show_text']:
                    try:
                        # 尝试创建字体
                        font = pygame.font.SysFont(None, 48)
                        text_surface = font.render(firework['text'], True, COLORS['gold'])
                        text_surface.set_alpha(firework['text_alpha'])
                        
                        # 绘制文字
                        text_rect = text_surface.get_rect(center=(firework['x'], firework['y']))
                        surface.blit(text_surface, text_rect)
                        
                        # 绘制发光效果
                        if firework['text_alpha'] > 100:
                            for i in range(3, 0, -1):
                                glow_alpha = firework['text_alpha'] // (i * 2)
                                glow_surface = font.render(firework['text'], True, 
                                                          (255, 200, 100, glow_alpha))
                                glow_rect = glow_surface.get_rect(center=(firework['x'], firework['y']))
                                surface.blit(glow_surface, glow_rect)
                    except:
                        pass
        
        return surface

# 主应用
def main():
    # 标题
    st.markdown('<div class="main-header">🎆 2026马年跨年烟花祝福 🐴</div>', unsafe_allow_html=True)
    
    # 初始化状态
    if 'simulation' not in st.session_state:
        st.session_state.simulation = FireworkSimulation(width=800, height=500)
        st.session_state.last_update = 0
        st.session_state.auto_mode = True
        st.session_state.next_blessing_time = 0
    
    # 获取当前时间
    import time
    current_time = int(time.time() * 1000)
    
    # 更新模拟
    if current_time - st.session_state.last_update > 16:  # 约60fps
        st.session_state.simulation.update(current_time)
        st.session_state.last_update = current_time
        
        # 自动模式发射祝福语烟花
        if st.session_state.auto_mode:
            if current_time - st.session_state.next_blessing_time > 3000:  # 3秒一个
                text = st.session_state.simulation.create_blessing_firework()
                if text:
                    st.session_state.last_blessing = text
                st.session_state.next_blessing_time = current_time
    
    # 布局
    col1, col2, col3 = st.columns([2, 5, 2])
    
    with col1:
        st.markdown("### 🎯 祝福语控制")
        
        # 祝福语列表
        for i, blessing in enumerate(st.session_state.simulation.blessings):
            if st.button(f"🎇 {blessing}", key=f"blessing_{i}", use_container_width=True):
                st.session_state.simulation.create_blessing_firework()
                st.session_state.last_blessing = blessing
        
        # 随机烟花按钮
        if st.button("🎆 发射随机烟花", use_container_width=True):
            st.session_state.simulation.create_firework()
        
        # 自动模式开关
        auto_mode = st.checkbox("自动模式", value=st.session_state.auto_mode)
        if auto_mode != st.session_state.auto_mode:
            st.session_state.auto_mode = auto_mode
            st.rerun()
        
        # 清空按钮
        if st.button("🧹 清空烟花", use_container_width=True):
            st.session_state.simulation.fireworks = []
            st.rerun()
        
        # 状态显示
        st.markdown("---")
        active_count = len(st.session_state.simulation.fireworks)
        st.markdown(f"**活跃烟花:** {active_count}个")
        if 'last_blessing' in st.session_state:
            st.markdown(f"**上次祝福:** {st.session_state.last_blessing}")
    
    with col2:
        st.markdown("### 🎇 烟花展示区")
        
        # 渲染烟花
        surface = st.session_state.simulation.render()
        
        # 转换为PIL Image
        img_str = pygame.image.tostring(surface, 'RGBA')
        img = Image.frombytes('RGBA', (800, 500), img_str)
        
        # 显示图像
        st.image(img, use_column_width=True)
        
        # 触摸控制提示（移动端）
        st.markdown("""
        <div style="text-align: center; color: #FFD166; margin-top: 1rem;">
        📱 移动端提示：点击祝福语按钮发射对应烟花
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 📜 祝福语录")
        
        # 显示所有祝福语
        for blessing in st.session_state.simulation.blessings:
            st.markdown(f'<div class="blessing-text">{blessing}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 烟花效果说明
        st.markdown("### 💫 效果说明")
        st.markdown("""
        - 🎆 **金色烟花**：祝福语烟花
        - 🌈 **彩色烟花**：随机装饰烟花
        - ✨ **文字特效**：烟花爆炸后显示祝福语
        - ⭐ **星空背景**：动态闪烁星星
        """)
        
        # 马年特别祝福
        st.markdown("### 🐴 马年特辑")
        horse_blessings = [
            "马到成功",
            "龙马精神", 
            "一马当先",
            "万马奔腾",
            "马上有福"
        ]
        for hb in horse_blessings:
            st.markdown(f"🎠 {hb}")
    
    # 底部信息
    st.markdown("---")
    
    # 响应式布局适应移动端
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        if st.button("🎇 快速发射", use_container_width=True):
            for _ in range(3):
                st.session_state.simulation.create_firework()
    
    with col_b2:
        if st.button("🎉 连发祝福", use_container_width=True):
            for _ in range(3):
                text = st.session_state.simulation.create_blessing_firework()
                if text:
                    st.session_state.last_blessing = text
    
    with col_b3:
        if st.button("✨ 特效模式", use_container_width=True):
            # 创建多个烟花形成特效
            for i in range(5):
                x = st.session_state.simulation.width * (i + 1) // 6
                st.session_state.simulation.create_firework(x=x)
    
    # 版权信息
    st.markdown("""
    <div style="text-align: center; color: #888; margin-top: 2rem; font-size: 0.9rem;">
    🎆 2026 马年跨年烟花祝福系统 | 祝您新年快乐，万事如意！ 🐴
    </div>
    """, unsafe_allow_html=True)
    
    # 自动重新运行以更新动画
    st.rerun()

if __name__ == "__main__":
    main()