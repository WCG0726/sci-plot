"""
utils/helpers.py - 辅助函数
==========================
包含颜色获取、样式设置等辅助函数
"""

import matplotlib.pyplot as plt
from config import OriginStyleConfig


def get_colors(config, style, n=10):
    """获取颜色列表"""
    if style.get('use_custom_colors', False):
        colors = style.get('custom_colors', [])
        while len(colors) < n:
            colors = colors + colors
        return colors[:n]
    else:
        # 使用预设配色
        palette = style.get('palette', 'Nature科研')
        preset_colors = OriginStyleConfig.COLOR_PRESETS.get(palette, 
                         OriginStyleConfig.COLOR_PRESETS['Nature科研'])
        while len(preset_colors) < n:
            preset_colors = preset_colors + preset_colors
        return preset_colors[:n]


def setup_plot_style(config):
    """根据配置设置绘图样式"""
    font = config.get('font', 'Times New Roman')
    cn_font = config.get('cn_font', 'SimHei')
    fontweight = 'bold' if config.get('font_bold', False) else 'normal'
    
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': [font, cn_font, 'DejaVu Sans'],
        'font.size': config.get('fontsize', 10),
        'font.weight': fontweight,
        'axes.unicode_minus': False,
        'axes.labelweight': fontweight,
        'axes.titleweight': fontweight,
        'figure.figsize': config.get('figsize', (8, 6)),
        'figure.dpi': 150,
        'axes.linewidth': 1.0,
        'lines.linewidth': 1.5,
        'lines.markersize': 6,
    })
    
    tick_dir = config.get('tick_dir', 'in')
    if tick_dir == 'in':
        plt.rcParams.update({
            'xtick.direction': 'in', 'ytick.direction': 'in',
            'xtick.top': True, 'ytick.right': True,
        })
    else:
        plt.rcParams.update({
            'xtick.direction': 'out', 'ytick.direction': 'out',
            'xtick.top': False, 'ytick.right': False,
        })


def apply_origin_style(ax, config, style):
    """
    应用Origin风格设置到图表
    参考: https://matplotlib.net.cn/stable/users/explain/text/fonts.html
    """
    # 1. 设置字体
    plt.rcParams['font.sans-serif'] = [config['en_font'], config['cn_font'], 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 2. 设置标题
    title_weight = 'bold' if config['title_bold'] else 'normal'
    ax.set_title(config['title'], 
                 fontsize=config['title_fontsize'], 
                 fontweight=title_weight, 
                 pad=config['labelpad'])
    
    # 3. 设置轴标签
    ax.set_xlabel(config['xlabel'], 
                  fontsize=config['label_fontsize'],
                  fontfamily=config['en_font'], 
                  labelpad=config['labelpad'])
    ax.set_ylabel(config['ylabel'], 
                  fontsize=config['label_fontsize'],
                  fontfamily=config['en_font'], 
                  labelpad=config['labelpad'])
    
    # 4. 设置边框
    if config['show_border']:
        for spine in ax.spines.values():
            spine.set_linewidth(config['border_width'])
    else:
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    # 5. 设置网格线
    if config['show_grid']:
        ax.grid(True, color=config['grid_color'], 
                linewidth=config['grid_linewidth'],
                alpha=config['grid_alpha'])
    
    # 6. 设置刻度
    ax.tick_params(axis='both', 
                   direction=config['tick_dir'],
                   width=config['tick_width'],
                   length=config['tick_length'],
                   labelsize=config['tick_labelsize'])
    
    # 设置刻度标签旋转
    for label in ax.get_xticklabels():
        label.set_rotation(config['tick_rotation'])
    
    # 7. 设置刻度范围和间隔
    if not config['auto_range']:
        from matplotlib.ticker import MultipleLocator
        ax.set_xlim(config['x_min'], config['x_max'])
        ax.set_ylim(config['y_min'], config['y_max'])
        
        if config['x_interval'] > 0:
            ax.xaxis.set_major_locator(MultipleLocator(config['x_interval']))
        if config['y_interval'] > 0:
            ax.yaxis.set_major_locator(MultipleLocator(config['y_interval']))
    
    # 8. 设置图例
    if config['show_legend']:
        ax.legend(loc=config['legend_loc'],
                  fontsize=config['legend_fontsize'],
                  frameon=config['legend_frame'])