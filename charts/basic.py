"""
charts/basic.py - 基础图表
==========================
包含折线图、散点图、柱状图等基础图表
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils import get_colors, apply_origin_style


def plot_line(df, config, style):
    """折线图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        x_col = st.selectbox("X轴", df.columns.tolist(), key='line_x')
    with col2:
        y_cols = st.multiselect("Y轴 (可多选)", 
                                [c for c in numeric_cols if c != x_col],
                                default=[c for c in numeric_cols[:2] if c != x_col],
                                key='line_y')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = get_colors(config, style)
    markers = ['o', 's', '^', 'D', 'v', 'p', 'h', '*']
    
    for i, y_col in enumerate(y_cols):
        ax.plot(df[x_col], df[y_col], label=y_col,
               color=colors[i % len(colors)],
               linestyle=style['line_style_code'],
               marker=style['marker_code'] if style['marker_code'] else markers[i % len(markers)],
               markersize=style['marker_size'],
               linewidth=style['line_width'],
               markeredgecolor=colors[i % len(colors)],
               markeredgewidth=style['marker_edge_width'])
    
    apply_origin_style(ax, config, style)
    return fig


def plot_scatter(df, config, style):
    """散点图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("X轴", numeric_cols, key='scatter_x')
    with col2:
        y_col = st.selectbox("Y轴", [c for c in numeric_cols if c != x_col], key='scatter_y')
    with col3:
        color_col = st.selectbox("颜色分组", ['无'] + all_cols, key='scatter_color')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = get_colors(config, style)
    
    if color_col == '无':
        ax.scatter(df[x_col], df[y_col], 
                   s=style['marker_size']**2,
                   alpha=1-style['fill_alpha'],
                   edgecolors=colors[0],
                   linewidth=style['marker_edge_width'],
                   color=colors[0],
                   marker=style['marker_code'] if style['marker_code'] else 'o')
    else:
        groups = df[color_col].unique()
        for i, group in enumerate(groups):
            mask = df[color_col] == group
            ax.scatter(df.loc[mask, x_col], df.loc[mask, y_col],
                      label=str(group),
                      s=style['marker_size']**2,
                      alpha=1-style['fill_alpha'],
                      edgecolors=colors[i % len(colors)],
                      linewidth=style['marker_edge_width'],
                      color=colors[i % len(colors)],
                      marker=style['marker_code'] if style['marker_code'] else 'o')
    
    apply_origin_style(ax, config, style)
    return fig


def plot_bar(df, config, style):
    """柱状图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        cat_col = st.selectbox("类别列", all_cols, key='bar_cat')
    with col2:
        val_cols = st.multiselect("数值列", numeric_cols, key='bar_val')
    
    compute_error = st.checkbox("自动计算误差线 (标准差)", value=False)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = get_colors(config, style)
    
    if val_cols:
        if compute_error:
            bar_data = df.groupby(cat_col)[val_cols].agg(['mean', 'std']).reset_index()
            bar_data.columns = [cat_col] + [f'{c}_{s}' for c in val_cols for s in ['mean', 'std']]
        else:
            bar_data = df.groupby(cat_col)[val_cols].mean().reset_index()
        
        x = np.arange(len(bar_data))
        width = 0.8 / len(val_cols)
        
        for i, col in enumerate(val_cols):
            offset = (i - len(val_cols)/2 + 0.5) * width
            if compute_error:
                y = bar_data[f'{col}_mean']
                yerr = bar_data[f'{col}_std']
            else:
                y = bar_data[col]
                yerr = None
            
            ax.bar(x + offset, y, width, label=col,
                  color=colors[i % len(colors)],
                  edgecolor='black',
                  linewidth=style['line_width'],
                  yerr=yerr, capsize=3)
        
        ax.set_xticks(x)
        ax.set_xticklabels(bar_data[cat_col])
    
    apply_origin_style(ax, config, style)
    return fig


def plot_errorbar(df, config, style):
    """误差线图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("X轴", df.columns, key='err_x')
    with col2:
        y_col = st.selectbox("Y轴", numeric_cols, key='err_y')
    with col3:
        err_col = st.selectbox("误差列", numeric_cols, key='err_err')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = get_colors(config, style)
    
    ax.errorbar(df[x_col], df[y_col], yerr=df[err_col],
                fmt=style['marker_code'] if style['marker_code'] else 'o',
                color=colors[0],
                linestyle=style['line_style_code'],
                linewidth=style['line_width'],
                markersize=style['marker_size'],
                capsize=5, capthick=1)
    
    apply_origin_style(ax, config, style)
    return fig