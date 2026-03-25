"""
charts/__init__.py - 图表模块
============================
包含所有图表函数
"""

# 基础图表
from .basic import plot_line, plot_scatter, plot_bar, plot_errorbar

# 统计图表
from .statistical import plot_box, plot_heatmap, plot_ridge

# 高级图表
from .advanced import plot_dual_axis, plot_subplots, plot_sankey

# 特殊图表
from .special import plot_ring, plot_stack_area, plot_parallel

__all__ = [
    # 基础图表
    'plot_line',
    'plot_scatter',
    'plot_bar',
    'plot_errorbar',
    # 统计图表
    'plot_box',
    'plot_heatmap',
    'plot_ridge',
    # 高级图表
    'plot_dual_axis',
    'plot_subplots',
    'plot_sankey',
    # 特殊图表
    'plot_ring',
    'plot_stack_area',
    'plot_parallel',
]

# 图表类型字典，方便主程序使用
CHART_TYPES = {
    "折线图": plot_line,
    "散点图": plot_scatter,
    "柱状图": plot_bar,
    "误差线图": plot_errorbar,
    "箱线图": plot_box,
    "热力图": plot_heatmap,
    "山脊图": plot_ridge,
    "双Y轴图": plot_dual_axis,
    "子图组合": plot_subplots,
    "桑基图": plot_sankey,
    "环形图": plot_ring,
    "堆叠面积图": plot_stack_area,
    "平行坐标图": plot_parallel,
}