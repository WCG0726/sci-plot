"""
charts/statistical.py - 统计图表
================================
包含箱线图、热力图、山脊图等统计图表
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from utils import get_colors, apply_origin_style


def plot_box(df, config, style):
    """箱线图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        value_col = st.selectbox("数值列", numeric_cols, key='box_val')
    with col2:
        group_col = st.selectbox("分组列", ['无'] + all_cols, key='box_group')
    
    show_points = st.checkbox("显示数据点", value=True)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = get_colors(config, style)
    
    if group_col != '无':
        groups = df[group_col].unique()
        data_list = [df[df[group_col] == g][value_col].values for g in groups]
        bp = ax.boxplot(data_list, labels=groups, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors[:len(groups)]):
            patch.set_facecolor(color)
            patch.set_alpha(1-style['fill_alpha'])
        
        if show_points:
            for i, g in enumerate(groups):
                y = df[df[group_col] == g][value_col].values
                x = np.random.normal(i+1, 0.04, len(y))
                ax.scatter(x, y, alpha=0.6, s=20, color='black')
    else:
        bp = ax.boxplot([df[value_col]], labels=[value_col], patch_artist=True)
        bp['boxes'][0].set_facecolor(colors[0])
        bp['boxes'][0].set_alpha(1-style['fill_alpha'])
    
    apply_origin_style(ax, config, style)
    return fig


def plot_heatmap(df, config, style):
    """热力图"""
    numeric_df = df.select_dtypes(include=[np.number])
    use_corr = st.checkbox("计算相关性矩阵", value=True)
    
    cmap = st.selectbox("配色", ['RdBu_r', 'coolwarm', 'viridis', 'Blues', 'YlOrRd'], index=0)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if use_corr:
        plot_data = numeric_df.corr()
        center = 0
    else:
        plot_data = numeric_df
        center = None
    
    sns.heatmap(plot_data, ax=ax, cmap=cmap, annot=True, fmt='.2f',
                linewidths=0.5, center=center)
    
    apply_origin_style(ax, config, style)
    return fig


def plot_ridge(df, config, style):
    """
    山脊图(Ridge/Joy Plot) - 参考Show2Know
    https://github.com/Winn1y/Show2Know/tree/main/11%20Joy%20Plot
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    selected_cols = st.multiselect("选择数据列", numeric_cols, default=numeric_cols[:3])
    
    if not selected_cols:
        st.warning("请选择至少一列数据")
        fig, ax = plt.subplots()
        return fig
    
    plot_data = df[selected_cols]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = get_colors(config, style, len(selected_cols))
    
    # 使用seaborn的kdeplot绘制山脊图
    for i, col in enumerate(selected_cols):
        sns.kdeplot(data=df[col], fill=True, color=colors[i], alpha=0.6, ax=ax, label=col)
    
    ax.set_xlabel(config['xlabel'] or 'Value', fontsize=config['label_fontsize'])
    ax.set_ylabel('Density', fontsize=config['label_fontsize'])
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    
    if config['show_legend']:
        ax.legend(loc=config['legend_loc'], fontsize=config['legend_fontsize'])
    
    return fig