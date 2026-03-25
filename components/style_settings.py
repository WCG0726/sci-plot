"""
components/style_settings.py - 样式设置组件
==========================================
包含线型、标记、颜色等样式设置
"""

import streamlit as st
from config import OriginStyleConfig


def style_settings_section():
    """图表样式设置"""
    st.sidebar.markdown("---")
    st.sidebar.header("🎨 样式设置")
    
    style = {}
    
    # 线型设置
    style['line_style'] = st.sidebar.selectbox(
        "线型",
        list(OriginStyleConfig.LINE_STYLES.keys()),
        index=0
    )
    style['line_style_code'] = OriginStyleConfig.LINE_STYLES[style['line_style']]
    
    # 标记设置
    style['marker'] = st.sidebar.selectbox(
        "标记样式",
        list(OriginStyleConfig.MARKERS.keys()),
        index=1
    )
    style['marker_code'] = OriginStyleConfig.MARKERS[style['marker']]
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        style['marker_size'] = st.slider("标记大小", 2, 15, 6)
        style['line_width'] = st.slider("线条宽度", 0.5, 5.0, 1.5)
    with col2:
        style['marker_edge_width'] = st.slider("标记边框", 0.0, 2.0, 0.5)
    
    # 颜色设置 - 简化版
    st.sidebar.markdown("**🎨 颜色方案:**")
    
    color_mode = st.sidebar.radio("颜色模式", ["预设方案", "自定义颜色"], horizontal=True)
    
    if color_mode == "预设方案":
        preset_name = st.sidebar.selectbox("选择配色", list(OriginStyleConfig.COLOR_PRESETS.keys()), index=0)
        style['custom_colors'] = OriginStyleConfig.COLOR_PRESETS[preset_name]
        style['use_custom_colors'] = False
        
        # 显示颜色预览
        preview_html = '<div style="display: flex; gap: 3px; margin: 5px 0;">'
        for c in OriginStyleConfig.COLOR_PRESETS[preset_name]:
            preview_html += f'<div style="width: 30px; height: 20px; background: {c}; border-radius: 3px; border: 1px solid #ddd;"></div>'
        preview_html += '</div>'
        st.sidebar.markdown(preview_html, unsafe_allow_html=True)
    else:
        # 简化的自定义颜色 - 只设置前5个
        st.sidebar.markdown("**选择5个颜色:**")
        default_colors = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F']
        style['custom_colors'] = []
        
        cols = st.sidebar.columns(5)
        for i in range(5):
            with cols[i]:
                color = st.color_picker(f"C{i+1}", default_colors[i], key=f"color_{i}", label_visibility="collapsed")
                style['custom_colors'].append(color)
        
        style['use_custom_colors'] = True
    
    # 填充设置
    style['fill_alpha'] = st.sidebar.slider("填充透明度", 0.0, 1.0, 0.0)
    
    return style