"""
config.py - 配置类
================
包含OriginStyleConfig和各种配置常量
"""

import matplotlib.colors as mcolors
import matplotlib.font_manager as fm


# ============================================================
# 字体配置
# ============================================================

def get_available_fonts():
    """获取系统可用的字体列表"""
    available = {f.name for f in fm.fontManager.ttflist}
    preferred = [
        'Times New Roman', 'Arial', 'Calibri', 'Cambria',
        'Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 
        'FangSong', 'Noto Sans CJK SC', 'Noto Sans CJK JP'
    ]
    return [f for f in preferred if f in available]


AVAILABLE_FONTS = get_available_fonts()
CSS4_COLORS = list(mcolors.CSS4_COLORS.keys())[:50]


# ============================================================
# Origin风格配置类
# ============================================================

class OriginStyleConfig:
    """Origin风格配置"""
    
    # 线型选项
    LINE_STYLES = {
        '实线': '-',
        '虚线': '--',
        '点线': ':',
        '点划线': '-.',
        '无线': ''
    }
    
    # 标记样式
    MARKERS = {
        '无': '',
        '圆圈': 'o',
        '方块': 's',
        '三角形': '^',
        '菱形': 'D',
        '倒三角': 'v',
        '五边形': 'p',
        '六边形': 'h',
        '星形': '*',
        '十字': '+',
        '叉号': 'x',
    }
    
    # 颜色预设
    COLOR_PRESETS = {
        'Nature科研': ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F'],
        '暖色调': ['#FF6B6B', '#FFA07A', '#FFD700', '#FF8C00', '#FF4500'],
        '冷色调': ['#4169E1', '#00CED1', '#20B2AA', '#5F9EA0', '#4682B4'],
        '灰度': ['#2C2C2C', '#4A4A4A', '#6B6B6B', '#8C8C8C', '#ADADAD'],
        '彩虹': ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF'],
        'Pastel': ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFD1DC'],
        'Set1': ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00'],
        'Set2': ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854'],
    }
    
    # 刻度方向选项
    TICK_DIRECTIONS = ['内向(in)', '外向(out)', '内外交叉(inout)']
    
    # 图例位置选项
    LEGEND_LOCATIONS = [
        'best', 'upper right', 'upper left', 'lower left', 'lower right',
        'center left', 'center right', 'lower center', 'upper center', 'center'
    ]
    
    # 分辨率选项
    DPI_OPTIONS = [150, 300, 600]
    
    # 导出格式选项
    EXPORT_FORMATS = ['png', 'pdf', 'svg', 'eps', 'tiff']
    
    # 子图布局选项
    SUBPLOT_LAYOUTS = ['1×2', '2×1', '2×2', '2×3', '3×2', '3×3']


# ============================================================
# 页面配置
# ============================================================

PAGE_CONFIG = {
    'page_title': "SciPlot - 科研绘图工具",
    'page_icon': "📊",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# 自定义CSS样式
CUSTOM_CSS = """
<style>
    .stButton button {background-color: #00A087; color: white; border-radius: 5px;}
    .stButton button:hover {background-color: #008066;}
    .color-box {display: inline-block; width: 25px; height: 15px; margin: 1px; border-radius: 2px; border: 1px solid #ddd;}
</style>
"""