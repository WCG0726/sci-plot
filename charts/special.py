"""
charts/special.py - 特殊图表
============================
包含环形图、堆叠面积图、平行坐标图等特殊图表
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils import get_colors, apply_origin_style


def plot_ring(df, config, style):
    """
    环形图 - 参考Show2Know
    https://github.com/Winn1y/Show2Know/tree/main/6%20Circle%20Plot
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        label_col = st.selectbox("标签列", all_cols, key='ring_label')
    with col2:
        value_col = st.selectbox("数值列", numeric_cols, key='ring_value')
    
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = get_colors(config, style, len(df))
    
    wedges, texts = ax.pie(df[value_col], labels=df[label_col],
                           colors=colors, autopct='%1.1f%%',
                           startangle=90, pctdistance=0.85)
    
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    
    return fig


def plot_stack_area(df, config, style):
    """
    堆叠面积图 - 参考Show2Know
    https://github.com/Winn1y/Show2Know/tree/main/9%20Stack%20Plot
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        x_col = st.selectbox("X轴", df.columns, key='stack_x')
    with col2:
        y_cols = st.multiselect("Y轴数据", numeric_cols, key='stack_y')
    
    if not y_cols:
        st.warning("请选择至少一列Y轴数据")
        fig, ax = plt.subplots()
        return fig
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = get_colors(config, style, len(y_cols))
    
    ax.stackplot(df[x_col], *[df[c] for c in y_cols], labels=y_cols,
                 colors=colors, alpha=0.8)
    
    ax.set_xlabel(config['xlabel'] or x_col, fontsize=config['label_fontsize'])
    ax.set_ylabel(config['ylabel'] or 'Value', fontsize=config['label_fontsize'])
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    
    if config['show_legend']:
        ax.legend(loc=config['legend_loc'], fontsize=config['legend_fontsize'],
                 frameon=config['legend_frame'])
    
    return fig


def plot_parallel(df, config, style):
    """
    平行坐标图 - 参考Show2Know
    https://github.com/Winn1y/Show2Know/tree/main/12%20Parallel%20Plot
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        class_col = st.selectbox("分类列 (可选)", ['无'] + all_cols, key='parallel_class')
    with col2:
        selected_cols = st.multiselect("数值列", numeric_cols, default=numeric_cols[:5])
    
    if not selected_cols:
        st.warning("请选择至少两列数值数据")
        fig, ax = plt.subplots()
        return fig
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if class_col != '无':
        pd.plotting.parallel_coordinates(df, class_col, 
                                         cols=selected_cols,
                                         colormap='viridis', ax=ax)
    else:
        colors = get_colors(config, style)
        for i, col in enumerate(selected_cols):
            ax.plot(range(len(selected_cols)), 
                   [df[col].mean()] * len(selected_cols),
                   marker='o', markersize=4, alpha=0.6, color=colors[i % len(colors)],
                   label=col)
        ax.set_xticks(range(len(selected_cols)))
        ax.set_xticklabels(selected_cols)
        if config['show_legend']:
            ax.legend(loc=config['legend_loc'], fontsize=config['legend_fontsize'])
    
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    ax.grid(True, alpha=0.3)
    
    return fig