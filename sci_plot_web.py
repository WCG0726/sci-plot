"""
sci_plot_web.py - 科研绘图工具 Web版 (v3.1 - 基于matplotlib官方文档)
====================================================================
参考: https://matplotlib.net.cn/stable/users/index.html

启动方法:
    streamlit run sci_plot_web.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import seaborn as sns
from io import BytesIO
import json

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="SciPlot - 科研绘图工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 字体配置 - 基于matplotlib官方文档
# ============================================================
# 参考: https://matplotlib.net.cn/stable/users/explain/text/fonts.html
# Matplotlib 3.6+ 支持字体回退，可以在font.sans-serif中设置多个字体

# 检测系统可用字体
def get_available_fonts():
    """获取系统可用的字体列表"""
    available = {f.name for f in fm.fontManager.ttflist}
    # 常用中英文字体
    preferred = [
        'Times New Roman', 'Arial', 'Calibri', 'Cambria',
        'Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 
        'FangSong', 'Noto Sans CJK SC', 'Noto Sans CJK JP'
    ]
    return [f for f in preferred if f in available]

AVAILABLE_FONTS = get_available_fonts()

# 设置默认字体（字体回退机制）
# 按顺序尝试：Times New Roman -> Arial -> 系统中文字体
plt.rcParams['font.sans-serif'] = ['Times New Roman', 'Arial', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# CSS4颜色名称（matplotlib内置）
CSS4_COLORS = list(mcolors.CSS4_COLORS.keys())[:50]  # 取前50个常用颜色

# ============================================================
# 自定义样式
# ============================================================
st.markdown("""
<style>
    .stButton button {background-color: #00A087; color: white; border-radius: 5px;}
    .stButton button:hover {background-color: #008066;}
    .color-box {display: inline-block; width: 25px; height: 15px; margin: 1px; border-radius: 2px; border: 1px solid #ddd;}
</style>
""", unsafe_allow_html=True)

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
        '正三角': '^',
        '五边形': 'p',
        '六边形': 'h',
        '星形': '*',
        '十字': '+',
        '叉号': 'x',
    }
    
    # 颜色选项
    COLORS = {
        '红色': '#E64B35',
        '蓝色': '#4DBBD5',
        '绿色': '#00A087',
        '紫色': '#3C5488',
        '橙色': '#F39B7F',
        '灰色': '#8491B4',
        '青色': '#91D1C2',
        '深红': '#DC0000',
        '棕色': '#7E6148',
        '浅棕': '#B09C85',
        '黑色': '#000000',
        '白色': '#FFFFFF',
    }

# ============================================================
# 坐标轴设置模块
# ============================================================

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
    
    # 2. 字体设置 - 基于matplotlib官方字体回退机制
    st.sidebar.subheader("🔤 字体设置")
    
    # 构建可用字体列表
    en_fonts = [f for f in AVAILABLE_FONTS if f in ['Times New Roman', 'Arial', 'Calibri', 'Cambria', 'Georgia']]
    if not en_fonts:
        en_fonts = ['Times New Roman', 'Arial']
    
    cn_fonts = [f for f in AVAILABLE_FONTS if f in ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong']]
    if not cn_fonts:
        cn_fonts = ['SimHei', 'Microsoft YaHei']
    
    # 英文字体
    config['en_font'] = st.sidebar.selectbox(
        "英文字体",
        en_fonts,
        index=0
    )
    
    # 中文字体
    config['cn_font'] = st.sidebar.selectbox(
        "中文字体",
        cn_fonts,
        index=0
    )
    
    # 标题字体大小
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config['title_fontsize'] = st.slider("标题字号", 8, 30, 16)
    with col2:
        config['title_bold'] = st.checkbox("标题加粗", value=True)
    
    # 轴标签字体大小
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
    
    # 刻度方向
    config['tick_direction'] = st.sidebar.selectbox(
        "刻度方向",
        ['内向(in)', '外向(out)', '内外交叉(inout)'],
        index=0
    )
    # 提取方向代码
    config['tick_dir'] = config['tick_direction'].split('(')[1].rstrip(')')
    
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
    config['legend_loc'] = st.sidebar.selectbox(
        "图例位置",
        ['best', 'upper right', 'upper left', 'lower left', 'lower right',
         'center left', 'center right', 'lower center', 'upper center', 'center'],
        index=0
    )
    config['legend_fontsize'] = st.slider("图例字号", 6, 16, 10)
    config['legend_frame'] = st.checkbox("图例边框", value=True)
    
    return config

# ============================================================
# 图表样式设置
# ============================================================

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
        index=1  # 默认圆圈
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
    
    # 预设配色方案
    color_presets = {
        'Nature科研': ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F'],
        '暖色调': ['#FF6B6B', '#FFA07A', '#FFD700', '#FF8C00', '#FF4500'],
        '冷色调': ['#4169E1', '#00CED1', '#20B2AA', '#5F9EA0', '#4682B4'],
        '灰度': ['#2C2C2C', '#4A4A4A', '#6B6B6B', '#8C8C8C', '#ADADAD'],
        '彩虹': ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF'],
        'Pastel': ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFD1DC'],
        'Set1': ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00'],
        'Set2': ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854'],
    }
    
    color_mode = st.sidebar.radio("颜色模式", ["预设方案", "自定义颜色"], horizontal=True)
    
    if color_mode == "预设方案":
        preset_name = st.sidebar.selectbox("选择配色", list(color_presets.keys()), index=0)
        style['custom_colors'] = color_presets[preset_name]
        style['use_custom_colors'] = False
        
        # 显示颜色预览
        preview_html = '<div style="display: flex; gap: 3px; margin: 5px 0;">'
        for c in color_presets[preset_name]:
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

# ============================================================
# 应用Origin风格设置
# ============================================================

def apply_origin_style(ax, config, style):
    """
    应用Origin风格设置到图表
    参考: https://matplotlib.net.cn/stable/users/explain/text/fonts.html
    """
    
    # 1. 设置字体 - 使用font.sans-serif支持字体回退
    # 按顺序尝试：英文字体 -> 中文字体 -> 默认字体
    plt.rcParams['font.sans-serif'] = [config['en_font'], config['cn_font'], 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 2. 设置标题
    title_weight = 'bold' if config['title_bold'] else 'normal'
    ax.set_title(config['title'], 
                 fontsize=config['title_fontsize'], 
                 fontweight=title_weight, 
                 pad=config['labelpad'])
    
    # 3. 设置轴标签 - 使用fontfamily参数
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
    
    # 设置刻度标签字体和旋转
    for label in ax.get_xticklabels():
        label.set_fontfamily(config['en_font'])
        label.set_rotation(config['tick_rotation'])
    for label in ax.get_yticklabels():
        label.set_fontfamily(config['en_font'])
    
    # 7. 设置刻度范围和间隔
    if not config['auto_range']:
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
    else:
        ax.legend().remove() if ax.get_legend() else None

# ============================================================
# 数据输入模块
# ============================================================

def data_input_section():
    """数据输入区域"""
    st.sidebar.header("📁 数据输入")
    
    data_source = st.sidebar.radio("选择数据来源", 
                                    ["上传文件", "手动输入", "示例数据"])
    
    df = None
    
    if data_source == "上传文件":
        uploaded_file = st.sidebar.file_uploader(
            "上传数据文件",
            type=['csv', 'xlsx', 'xls', 'tsv'],
            help="支持 CSV, Excel, TSV 格式"
        )
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.tsv'):
                    df = pd.read_csv(uploaded_file, sep='\t')
                st.sidebar.success(f"✅ {df.shape[0]}行 × {df.shape[1]}列")
            except Exception as e:
                st.sidebar.error(f"读取失败: {e}")
    
    elif data_source == "手动输入":
        st.sidebar.subheader("手动输入数据")
        col_names = st.sidebar.text_input("列名 (逗号分隔)", value="X,Y,Group").split(',')
        data_text = st.sidebar.text_area(
            "数据 (每行一组，逗号分隔)",
            value="1, 2, A\n3, 4, B\n5, 6, A\n7, 8, B",
            height=150
        )
        if data_text:
            try:
                rows = []
                for line in data_text.strip().split('\n'):
                    row = [x.strip() for x in line.split(',')]
                    processed_row = []
                    for v in row:
                        try:
                            processed_row.append(float(v))
                        except:
                            processed_row.append(v)
                    rows.append(processed_row)
                df = pd.DataFrame(rows, columns=[c.strip() for c in col_names])
            except Exception as e:
                st.sidebar.error(f"格式错误: {e}")
    
    else:  # 示例数据
        example_type = st.sidebar.selectbox(
            "选择示例数据",
            ["正弦余弦", "随机散点", "分组数据", "误差线数据", "时间序列"]
        )
        
        np.random.seed(42)
        if example_type == "正弦余弦":
            x = np.linspace(0, 10, 50)
            df = pd.DataFrame({'X': x, 'sin(X)': np.sin(x), 'cos(X)': np.cos(x)})
        elif example_type == "随机散点":
            df = pd.DataFrame({
                'X': np.random.randn(100),
                'Y': np.random.randn(100) * 2 + 1,
                'Group': np.random.choice(['A', 'B', 'C'], 100)
            })
        elif example_type == "分组数据":
            df = pd.DataFrame({
                'Group': np.repeat(['A', 'B', 'C', 'D'], 30),
                'Value': np.concatenate([
                    np.random.normal(10, 2, 30), np.random.normal(12, 2.5, 30),
                    np.random.normal(8, 1.5, 30), np.random.normal(15, 3, 30)
                ])
            })
        elif example_type == "误差线数据":
            df = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D', 'E'],
                'Mean': [23, 45, 56, 78, 32],
                'Std': [3, 5, 4, 6, 3]
            })
        else:  # 时间序列
            dates = pd.date_range('2024-01-01', periods=100)
            df = pd.DataFrame({
                'Date': dates,
                'Value_A': np.cumsum(np.random.randn(100)) + 100,
                'Value_B': np.cumsum(np.random.randn(100)) + 50
            })
        
        st.sidebar.success(f"✅ {example_type}")
    
    return df

# ============================================================
# 数据编辑模块
# ============================================================

def data_editor_section(df):
    """数据编辑区域 - 稳定版"""
    st.markdown("---")
    st.subheader("📝 数据编辑")
    
    # 使用session state保存数据
    if 'edited_df' not in st.session_state:
        st.session_state.edited_df = df.copy()
    
    # 操作按钮
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        add_rows = st.number_input("添加行数", 1, 10, 1, key="add_rows_input")
        if st.button("➕ 添加空行", key="add_rows_btn"):
            new_rows = pd.DataFrame([[np.nan] * len(st.session_state.edited_df.columns)] * add_rows,
                                    columns=st.session_state.edited_df.columns)
            st.session_state.edited_df = pd.concat([st.session_state.edited_df, new_rows], 
                                                    ignore_index=True)
            st.rerun()
    
    with col2:
        new_col = st.text_input("新列名", "New_Column", key="new_col_input")
        if st.button("➕ 添加列", key="add_col_btn"):
            st.session_state.edited_df[new_col] = np.nan
            st.rerun()
    
    with col3:
        if st.button("🗑️ 删除最后行", key="del_row_btn"):
            if len(st.session_state.edited_df) > 1:
                st.session_state.edited_df = st.session_state.edited_df.iloc[:-1]
                st.rerun()
    
    with col4:
        if st.button("🗑️ 删除最后列", key="del_col_btn"):
            if len(st.session_state.edited_df.columns) > 1:
                st.session_state.edited_df = st.session_state.edited_df.iloc[:, :-1]
                st.rerun()
    
    # 显示数据表（使用较稳定的配置）
    st.markdown("**数据表格:**")
    
    # 提供两种编辑模式
    edit_mode = st.radio("编辑模式", ["查看模式", "编辑模式"], horizontal=True, key="edit_mode")
    
    if edit_mode == "编辑模式":
        try:
            # 使用更稳定的data_editor配置
            edited = st.data_editor(
                st.session_state.edited_df,
                use_container_width=True,
                num_rows="fixed",  # 固定行数更稳定
                key="stable_editor"
            )
            st.session_state.edited_df = edited
        except Exception as e:
            st.warning(f"编辑器异常，已切换到查看模式")
            st.dataframe(st.session_state.edited_df, use_container_width=True)
    else:
        st.dataframe(st.session_state.edited_df, use_container_width=True)
    
    # 显示数据形状
    st.caption(f"当前数据: {st.session_state.edited_df.shape[0]}行 × {st.session_state.edited_df.shape[1]}列")
    
    return st.session_state.edited_df

# ============================================================
# 图表绘制函数
# ============================================================

def get_colors(config, style, n=10):
    """获取颜色列表"""
    if style.get('use_custom_colors', False):
        colors = style.get('custom_colors', [])
        while len(colors) < n:
            colors = colors + colors
        return colors[:n]
    else:
        # 使用预设配色
        from matplotlib import cm
        palette = style.get('palette', 'Nature')
        if palette in ['Nature']:
            return ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F',
                    '#8491B4', '#91D1C2', '#DC0000', '#7E6148', '#B09C85'][:n]
        else:
            cmap = cm.get_cmap(palette, n)
            return [cmap(i) for i in range(n)]

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
        ax.plot(df[x_col], df[y_col], 
                label=y_col,
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
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if use_corr:
        plot_data = numeric_df.corr()
        center = 0
    else:
        plot_data = numeric_df
        center = None
    
    cmap = st.selectbox("配色", ['RdBu_r', 'coolwarm', 'viridis', 'Blues', 'YlOrRd'], index=0)
    
    sns.heatmap(plot_data, ax=ax, cmap=cmap, annot=True, fmt='.2f',
                linewidths=0.5, center=center)
    
    apply_origin_style(ax, config, style)
    return fig

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
    
    # 左Y轴
    ax1.plot(df[x_col], df[y1_col], 
             color=colors[0], 
             marker=style['marker_code'] if style['marker_code'] else 'o',
             linestyle=style['line_style_code'],
             linewidth=style['line_width'],
             markersize=style['marker_size'],
             label=y1_col)
    ax1.set_ylabel(y1_col, color=colors[0], fontsize=config['label_fontsize'])
    ax1.tick_params(axis='y', labelcolor=colors[0])
    
    # 右Y轴
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
    
    # 合并图例
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
    
    # 子图布局选择
    st.markdown("**子图布局设置:**")
    col1, col2 = st.columns(2)
    with col1:
        layout = st.selectbox("布局", ['1×2', '2×1', '2×2', '2×3', '3×2', '3×3'], index=2)
        rows, cols = map(int, layout.split('×'))
    with col2:
        fig_width = st.slider("总宽度", 6, 16, 10)
        fig_height = st.slider("总高度", 4, 12, 8)
    
    # 为每个子图选择数据
    st.markdown("**为每个子图选择数据:**")
    subplot_configs = []
    for i in range(rows * cols):
        st.markdown(f"**子图 {i+1}:**")
        scol1, scol2, scol3 = st.columns(3)
        with scol1:
            x_col = st.selectbox(f"X轴", df.columns, key=f'subplot_{i}_x')
        with scol2:
            y_cols = st.multiselect(f"Y轴", numeric_cols, default=[numeric_cols[i % len(numeric_cols)]] if numeric_cols else [], 
                                   key=f'subplot_{i}_y')
        with scol3:
            chart_type = st.selectbox(f"图表类型", ['折线图', '散点图', '柱状图'], key=f'subplot_{i}_type')
        subplot_configs.append({'x': x_col, 'y': y_cols, 'type': chart_type})
    
    # 创建子图
    # 参考matplotlib官方文档: plt.subplots()
    fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), 
                            layout='constrained')
    
    # 处理单个子图的情况
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
            
            # 应用基本样式
            ax.tick_params(direction='in', width=0.8, length=3)
            for spine in ax.spines.values():
                spine.set_linewidth(0.8)
    
    # 隐藏多余的子图
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
    
    # 手动输入桑基图数据
    col1, col2 = st.columns(2)
    with col1:
        labels = st.text_input("节点标签 (逗号分隔)", value="A,B,C,D,E")
        label_list = [l.strip() for l in labels.split(',')]
    with col2:
        flows = st.text_input("流量值 (逗号分隔)", value="10,-3,-4,-3")
        flow_list = [float(f.strip()) for f in flows.split(',')]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 使用matplotlib内置的Sankey
    sankey = Sankey(ax=ax, scale=0.01, offset=0.2, head_angle=180, format='%.0f', unit='%')
    sankey.add(flows=flow_list, labels=label_list,
               orientations=[0] * len(flow_list),
               pathlengths=[0.25] * len(flow_list))
    sankey.finish()
    
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    
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
    
    # 创建数据框
    plot_data = df[selected_cols]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 使用seaborn的kdeplot绘制山脊图
    sns.kdeplot(data=plot_data, fill=True, palette="husl", ax=ax, alpha=0.6)
    
    ax.set_xlabel(config['xlabel'] or 'Value', fontsize=config['label_fontsize'])
    ax.set_ylabel('Density', fontsize=config['label_fontsize'])
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    
    return fig

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
    
    # 绘制饼图
    wedges, texts, autotexts = ax.pie(df[value_col], labels=df[label_col],
                                       colors=colors, autopct='%1.1f%%',
                                       startangle=90, pctdistance=0.85)
    
    # 添加中心圆形成环形图
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
    
    # 绘制堆叠面积图
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
        # 使用pandas的parallel_coordinates
        pd.plotting.parallel_coordinates(df, class_col, 
                                         cols=selected_cols,
                                         colormap='viridis', ax=ax)
    else:
        # 绘制无分类的平行坐标图
        for i, col in enumerate(selected_cols):
            ax.plot(range(len(selected_cols)), [df[col].mean()] * len(selected_cols),
                   marker='o', markersize=4, alpha=0.6)
        ax.set_xticks(range(len(selected_cols)))
        ax.set_xticklabels(selected_cols)
    
    ax.set_title(config['title'], fontsize=config['title_fontsize'],
                fontweight='bold' if config['title_bold'] else 'normal')
    ax.grid(True, alpha=0.3)
    
    return fig

# ============================================================
# 主界面
# ============================================================

def main():
    st.title("📊 SciPlot - Origin风格科研绘图工具")
    st.markdown("模仿Origin的作图逻辑，支持中英文混合字体、坐标轴设置、网格线等")
    st.markdown("---")
    
    # 数据输入
    df = data_input_section()
    
    if df is not None:
        # 数据预览
        with st.expander("📋 数据预览 & 编辑", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**行数:** {df.shape[0]}")
                st.write(f"**列数:** {df.shape[1]}")
            with col2:
                st.write(f"**数值列:** {len(df.select_dtypes(include=[np.number]).columns)}")
                st.write(f"**类别列:** {len(df.select_dtypes(exclude=[np.number]).columns)}")
            
            # 数据编辑
            df = data_editor_section(df)
        
        # 坐标轴设置
        config = axis_settings_section()
        
        # 样式设置
        style = style_settings_section()
        
        # 选择图表类型
        st.markdown("---")
        chart_type = st.selectbox(
            "📊 选择图表类型",
            ["折线图", "散点图", "柱状图", "误差线图", "箱线图", "热力图", "双Y轴图", 
             "子图组合", "桑基图", "山脊图", "环形图", "堆叠面积图", "平行坐标图"]
        )
        
        # 绘制图表
        chart_functions = {
            "折线图": plot_line,
            "散点图": plot_scatter,
            "柱状图": plot_bar,
            "误差线图": plot_errorbar,
            "箱线图": plot_box,
            "热力图": plot_heatmap,
            "双Y轴图": plot_dual_axis,
            "子图组合": plot_subplots,
            "桑基图": plot_sankey,
            "山脊图": plot_ridge,
            "环形图": plot_ring,
            "堆叠面积图": plot_stack_area,
            "平行坐标图": plot_parallel,
        }
        
        fig = chart_functions[chart_type](df, config, style)
        
        # 显示图表
        st.pyplot(fig)
        
        # 导出
        st.markdown("---")
        st.subheader("📥 导出图表")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            dpi = st.selectbox("分辨率", [150, 300, 600], index=1)
        with col2:
            fmt = st.selectbox("格式", ['png', 'pdf', 'svg', 'eps', 'tiff'])
        with col3:
            filename = st.text_input("文件名", value="sci_plot_output")
        
        buf = BytesIO()
        fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        
        st.download_button(
            label=f"⬇️ 下载 {fmt.upper()}",
            data=buf,
            file_name=f"{filename}.{fmt}",
            mime=f"image/{fmt}"
        )
    
    else:
        st.info("👈 请在左侧选择数据来源开始绘图")
        
        # 显示帮助
        st.markdown("---")
        st.subheader("📖 功能说明")
        
        st.markdown("""
        ### 支持的图表类型 (集成自Show2Know)
        
        **基础图表:**
        - **折线图**: 显示数据趋势
        - **散点图**: 显示数据分布
        - **柱状图**: 比较数据大小
        - **误差线图**: 显示数据误差
        
        **统计图表:**
        - **箱线图**: 显示数据分布
        - **热力图**: 显示相关性矩阵
        - **山脊图**: 多组数据密度分布对比
        
        **高级图表:**
        - **双Y轴图**: 共享X轴的双Y轴
        - **子图组合**: 多图组合展示
        - **桑基图**: 流量/转移可视化
        - **环形图**: 占比展示
        - **堆叠面积图**: 多系列堆叠
        - **平行坐标图**: 多维数据对比
        
        ### 致谢
        部分图表代码参考自 [Show2Know](https://github.com/Winn1y/Show2Know)
        
        ### 字体设置
        - **英文字体**: Times New Roman, Arial等
        - **中文字体**: 黑体(SimHei), 楷体(KaiTi), 宋体(SimSun)等
        - **混合使用**: 自动识别中英文，分别应用不同字体
        
        ### 坐标轴设置
        - **边框**: 显示/隐藏，宽度可调
        - **网格线**: 颜色、线宽、透明度
        - **刻度**: 方向(in/out)、大小、粗细
        - **刻度范围**: 手动设置X/Y轴范围和间隔
        
        ### 样式设置
        - **线型**: 实线、虚线、点线、点划线
        - **标记**: 圆圈、方块、三角形、菱形等
        - **颜色**: 自定义颜色或预设配色
        
        ### 数学表达式
        支持LaTeX格式的数学表达式，例如：
        - `$\sigma_i=15$` 显示为 σᵢ=15
        - `$\mu=115, \sigma=15$` 显示为 μ=115, σ=15
        
        ### 字体代码对照
        | 代码 | 字体 |
        |------|------|
        | SimHei | 黑体 |
        | KaiTi | 楷体 |
        | SimSun | 宋体 |
        | FangSong | 仿宋 |
        | Microsoft YaHei | 微软雅黑 |
        
        ### 参考文档
        - [Matplotlib中文文档](https://matplotlib.net.cn/stable/)
        - [用户指南](https://matplotlib.net.cn/stable/users/index.html)
        - [字体设置](https://matplotlib.net.cn/stable/users/explain/text/fonts.html)
        - [颜色指定](https://matplotlib.net.cn/stable/users/explain/colors/colors.html)
        """)

if __name__ == "__main__":
    main()