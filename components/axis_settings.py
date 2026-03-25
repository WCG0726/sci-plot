"""
components/axis_settings.py - 坐标轴设置组件
============================================
包含坐标轴、刻度、图例等设置
"""

import streamlit as st
from config import OriginStyleConfig, AVAILABLE_FONTS


def axis_settings_section():
    """坐标轴设置区域"""
    st.sidebar.markdown("---")
    st.sidebar.header("📐 坐标轴设置")
    
    config = {}
    
    # 1. 基本设置
    st.sidebar.subheader("基本设置")
    config['title'] = st.sidebar.text_input("图表标题", value="My Chart")
    config['xlabel'] = st.sidebar.text_input("X轴标签", value="")
    config['ylabel'] = st.sidebar.text_input("Y轴标签", value="")
    
    # 2. 字体设置
    st.sidebar.subheader("🔤 字体设置")
    
    en_fonts = [f for f in AVAILABLE_FONTS if f in ['Times New Roman', 'Arial', 'Calibri', 'Cambria', 'Georgia']]
    if not en_fonts:
        en_fonts = ['Times New Roman', 'Arial']
    
    cn_fonts = [f for f in AVAILABLE_FONTS if f in ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong']]
    if not cn_fonts:
        cn_fonts = ['SimHei', 'Microsoft YaHei']
    
    config['en_font'] = st.sidebar.selectbox("英文字体", en_fonts, index=0)
    config['cn_font'] = st.sidebar.selectbox("中文字体", cn_fonts, index=0)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config['title_fontsize'] = st.slider("标题字号", 8, 30, 16)
    with col2:
        config['title_bold'] = st.checkbox("标题加粗", value=True)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config['label_fontsize'] = st.slider("标签字号", 8, 24, 14)
    with col2:
        config['labelpad'] = st.slider("标签间距", 0, 20, 5)
    
    # 3. 边框设置
    st.sidebar.subheader("🖼️ 边框设置")
    config['show_border'] = st.sidebar.checkbox("显示边框", value=True)
    config['border_width'] = st.sidebar.slider("边框宽度", 0.5, 3.0, 1.0)
    
    # 4. 网格线设置
    st.sidebar.subheader("📏 网格线设置")
    config['show_grid'] = st.sidebar.checkbox("显示网格线", value=False)
    config['grid_color'] = st.sidebar.color_picker("网格颜色", "#CCCCCC")
    config['grid_linewidth'] = st.sidebar.slider("网格线宽", 0.1, 2.0, 0.5)
    config['grid_alpha'] = st.sidebar.slider("网格透明度", 0.1, 1.0, 0.8)
    
    # 5. 刻度设置
    st.sidebar.subheader("📊 刻度设置")
    
    tick_dir_display = st.sidebar.selectbox("刻度方向", OriginStyleConfig.TICK_DIRECTIONS, index=0)
    config['tick_dir'] = tick_dir_display.split('(')[1].rstrip(')')
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config['tick_width'] = st.slider("刻度线宽度", 0.5, 3.0, 1.0)
        config['tick_length'] = st.slider("刻度线长度", 2, 15, 5)
    with col2:
        config['tick_labelsize'] = st.slider("刻度字号", 8, 24, 12)
        config['tick_rotation'] = st.slider("刻度旋转", 0, 90, 0)
    
    # 6. 刻度范围和间隔
    st.sidebar.subheader("📈 刻度范围")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config['x_min'] = st.number_input("X最小值", value=0.0, step=0.1)
        config['x_max'] = st.number_input("X最大值", value=10.0, step=0.1)
    with col2:
        config['y_min'] = st.number_input("Y最小值", value=0.0, step=0.1)
        config['y_max'] = st.number_input("Y最大值", value=10.0, step=0.1)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config['x_interval'] = st.number_input("X刻度间隔", value=1.0, step=0.1)
    with col2:
        config['y_interval'] = st.number_input("Y刻度间隔", value=1.0, step=0.1)
    
    config['auto_range'] = st.sidebar.checkbox("自动范围", value=True)
    
    # 7. 图例设置
    st.sidebar.subheader("📋 图例设置")
    config['show_legend'] = st.sidebar.checkbox("显示图例", value=True)
    config['legend_loc'] = st.sidebar.selectbox("图例位置", OriginStyleConfig.LEGEND_LOCATIONS, index=0)
    config['legend_fontsize'] = st.slider("图例字号", 6, 16, 10)
    config['legend_frame'] = st.checkbox("图例边框", value=True)
    
    return config