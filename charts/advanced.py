"""
charts/advanced.py - 高级图表
=============================
包含双Y轴图、子图组合、桑基图等高级图表
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils import get_colors, apply_origin_style


def plot_dual_axis(df, config, style):
    """双Y轴图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("X轴", df.columns, key='dual_x')
    with col2:
        y1_col = st.selectbox("左Y轴", numeric_cols, key='dual_y1')
    with col3:
        y2_col = st.selectbox("右Y轴", [c for c in numeric_cols if c != y1_col], key='dual_y2')
    
    colors = get_colors(config, style)
    
    fig, ax1 = plt.subplots(figsize=(8, 6))
    
    ax1.plot(df[x_col], df[y1_col], 
             color=colors[0], 
             marker=style['marker_code'] if style['marker_code'] else 'o',
             linestyle=style['line_style_code'],
             linewidth=style['line_width'],
             markersize=style['marker_size'],
             label=y1_col)
    ax1.set_ylabel(y1_col, color=colors[0], fontsize=config['label_fontsize'])
    ax1.tick_params(axis='y', labelcolor=colors[0])
    
    ax2 = ax1.twinx()
    ax2.plot(df[x_col], df[y2_col],
             color=colors[1],
             marker=style['marker_code'] if style['marker_code'] else 's',
             linestyle=style['line_style_code'],
             linewidth=style['line_width'],
             markersize=style['marker_size'],
             label=y2_col)
    ax2.set_ylabel(y2_col, color=colors[1], fontsize=config['label_fontsize'])
    ax2.tick_params(axis='y', labelcolor=colors[1])
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, 
               loc=config['legend_loc'],
               fontsize=config['legend_fontsize'],
               frameon=config['legend_frame'])
    
    ax1.set_xlabel(config['xlabel'], fontsize=config['label_fontsize'])
    ax1.set_title(config['title'], fontsize=config['title_fontsize'],
                  fontweight='bold' if config['title_bold'] else 'normal')
    
    return fig


def plot_subplots(df, config, style):
    """
    子图组合
    参考: https://matplotlib.net.cn/stable/users/explain/axes/
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    st.markdown("**子图布局设置:**")
    col1, col2 = st.columns(2)
    with col1:
        layout = st.selectbox("布局", ['1×2', '2×1', '2×2', '2×3', '3×2', '3×3'], index=2)
        rows, cols = map(int, layout.split('×'))
    with col2:
        fig_width = st.slider("总宽度", 6, 16, 10)
        fig_height = st.slider("总高度", 4, 12, 8)
    
    st.markdown("**为每个子图选择数据:**")
    subplot_configs = []
    for i in range(rows * cols):
        st.markdown(f"**子图 {i+1}:**")
        scol1, scol2, scol3 = st.columns(3)
        with scol1:
            x_col = st.selectbox(f"X轴", df.columns, key=f'subplot_{i}_x')
        with scol2:
            y_cols = st.multiselect(f"Y轴", numeric_cols, 
                                   default=[numeric_cols[i % len(numeric_cols)]] if numeric_cols else [], 
                                   key=f'subplot_{i}_y')
        with scol3:
            chart_type = st.selectbox(f"图表类型", ['折线图', '散点图', '柱状图'], key=f'subplot_{i}_type')
        subplot_configs.append({'x': x_col, 'y': y_cols, 'type': chart_type})
    
    fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), layout='constrained')
    
    if rows * cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    colors = get_colors(config, style)
    markers = ['o', 's', '^', 'D', 'v', 'p', 'h', '*']
    
    for i, (ax, subplot_cfg) in enumerate(zip(axes, subplot_configs)):
        if subplot_cfg['y']:
            x_data = df[subplot_cfg['x']]
            for j, y_col in enumerate(subplot_cfg['y']):
                y_data = df[y_col]
                color = colors[j % len(colors)]
                marker = markers[j % len(markers)]
                
                if subplot_cfg['type'] == '折线图':
                    ax.plot(x_data, y_data, label=y_col, color=color, 
                           marker=marker, markersize=4, linewidth=1.5)
                elif subplot_cfg['type'] == '散点图':
                    ax.scatter(x_data, y_data, label=y_col, color=color,
                              s=30, alpha=0.7, edgecolors='white')
                elif subplot_cfg['type'] == '柱状图':
                    width = 0.8 / len(subplot_cfg['y'])
                    x_pos = np.arange(len(x_data))
                    offset = (j - len(subplot_cfg['y'])/2 + 0.5) * width
                    ax.bar(x_pos + offset, y_data, width, label=y_col, color=color)
                    if j == len(subplot_cfg['y']) - 1:
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(x_data)
            
            ax.set_xlabel(subplot_cfg['x'], fontsize=10)
            ax.set_ylabel('Value', fontsize=10)
            ax.legend(fontsize=8, loc='best')
            ax.set_title(f'子图 {i+1}', fontsize=11, fontweight='bold')
            
            ax.tick_params(direction='in', width=0.8, length=3)
            for spine in ax.spines.values():
                spine.set_linewidth(0.8)
    
    for i in range(len(subplot_configs), len(axes)):
        axes[i].set_visible(False)
    
    fig.suptitle(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    
    return fig


def plot_sankey(df, config, style):
    """
    桑基图 - 参考Show2Know
    https://github.com/Winn1y/Show2Know/tree/main/7%20Sankey%20Plot
    """
    from matplotlib.sankey import Sankey
    
    st.markdown("**桑基图设置:**")
    st.info("桑基图需要手动输入数据：source, target, value")
    
    col1, col2 = st.columns(2)
    with col1:
        labels = st.text_input("节点标签 (逗号分隔)", value="A,B,C,D,E")
        label_list = [l.strip() for l in labels.split(',')]
    with col2:
        flows = st.text_input("流量值 (逗号分隔)", value="10,-3,-4,-3")
        flow_list = [float(f.strip()) for f in flows.split(',')]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sankey = Sankey(ax=ax, scale=0.01, offset=0.2, head_angle=180, format='%.0f', unit='%')
    sankey.add(flows=flow_list, labels=label_list,
               orientations=[0] * len(flow_list),
               pathlengths=[0.25] * len(flow_list))
    sankey.finish()
    
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    
    return fig