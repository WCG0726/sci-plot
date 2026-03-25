"""
sci_plot_web.py - 科研绘图工具 Web版 (Origin风格 v3.0)
=====================================================
模仿Origin的作图逻辑，支持中英文混合字体、坐标轴设置、网格线、刻度设置等

启动方法:
    streamlit run sci_plot_web.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
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
# 中文字体支持
# ============================================================
# 设置中英文混合字体
plt.rcParams['font.family'] = ['Times New Roman', 'SimHei']  # 英文用Times New Roman，中文用黑体
plt.rcParams['axes.unicode_minus'] = False  # 显示负号

# 字体代码对照表
FONT_MAP = {
    'SimHei': '黑体',
    'KaiTi': '楷体',
    'LiSu': '隶书',
    'FangSong': '仿宋',
    'YouYuan': '幼圆',
    'SimSun': '宋体',
    'Microsoft YaHei': '微软雅黑',
}

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
    
    # 2. 字体设置
    st.sidebar.subheader("🔤 字体设置")
    
    # 英文字体
    config['en_font'] = st.sidebar.selectbox(
        "英文字体",
        ['Times New Roman', 'Arial', 'Calibri', 'Cambria', 'Georgia'],
        index=0
    )
    
    # 中文字体
    config['cn_font'] = st.sidebar.selectbox(
        "中文字体",
        ['SimHei(黑体)', 'KaiTi(楷体)', 'SimSun(宋体)', 'FangSong(仿宋)', 'Microsoft YaHei(微软雅黑)'],
        index=0
    )
    # 提取字体代码
    config['cn_font_code'] = config['cn_font'].split('(')[0]
    
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
    
    # 颜色设置
    style['use_custom_colors'] = st.sidebar.checkbox("自定义颜色", value=False)
    if style['use_custom_colors']:
        st.sidebar.markdown("**选择颜色 (最多10个):**")
        default_colors = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F',
                          '#8491B4', '#91D1C2', '#DC0000', '#7E6148', '#B09C85']
        style['custom_colors'] = []
        for i in range(10):
            color = st.sidebar.color_picker(f"颜色{i+1}", default_colors[i], key=f"style_color_{i}")
            style['custom_colors'].append(color)
    else:
        # 预设配色
        palettes = ['Nature', 'Set1', 'Set2', 'Set3', 'Paired', 'Dark2', 
                    'Blues', 'Greens', 'Reds', 'RdBu_r']
        style['palette'] = st.sidebar.selectbox("预设配色", palettes, index=0)
    
    # 填充设置
    style['fill_alpha'] = st.sidebar.slider("填充透明度", 0.0, 1.0, 0.0)
    
    return style

# ============================================================
# 应用Origin风格设置
# ============================================================

def apply_origin_style(ax, config, style):
    """应用Origin风格设置到图表"""
    
    # 1. 设置字体
    plt.rcParams['font.family'] = [config['en_font'], config['cn_font_code']]
    
    # 2. 设置标题
    title_weight = 'bold' if config['title_bold'] else 'normal'
    ax.set_title(config['title'], fontsize=config['title_fontsize'], 
                 fontweight=title_weight, pad=config['labelpad'])
    
    # 3. 设置轴标签
    ax.set_xlabel(config['xlabel'], fontsize=config['label_fontsize'], 
                  fontfamily=config['en_font'], labelpad=config['labelpad'])
    ax.set_ylabel(config['ylabel'], fontsize=config['label_fontsize'],
                  fontfamily=config['en_font'], labelpad=config['labelpad'])
    
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
    """数据编辑区域"""
    st.markdown("---")
    st.subheader("📝 数据编辑")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**添加行**")
        add_row_count = st.number_input("添加行数", 1, 10, 1, key="add_row_count")
        if st.button("➕ 添加空行"):
            new_rows = pd.DataFrame([[np.nan] * len(df.columns)] * add_row_count, 
                                    columns=df.columns)
            df = pd.concat([df, new_rows], ignore_index=True)
            st.success(f"已添加 {add_row_count} 行")
    
    with col2:
        st.markdown("**添加列**")
        new_col_name = st.text_input("新列名", "New_Column", key="new_col_name")
        if st.button("➕ 添加列"):
            df[new_col_name] = np.nan
            st.success(f"已添加列: {new_col_name}")
    
    with col3:
        st.markdown("**删除操作**")
        if st.button("🗑️ 删除最后一行") and len(df) > 0:
            df = df.iloc[:-1]
            st.success("已删除最后一行")
        if st.button("🗑️ 删除最后一列") and len(df.columns) > 1:
            df = df.iloc[:, :-1]
            st.success("已删除最后一列")
    
    # 可编辑数据表
    st.markdown("**直接编辑数据 (双击单元格编辑):**")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    return edited_df

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
            ["折线图", "散点图", "柱状图", "误差线图", "箱线图", "热力图", "双Y轴图"]
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
        st.subheader("📖 Origin风格设置说明")
        
        st.markdown("""
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
        
        ### 字体代码对照
        | 代码 | 字体 |
        |------|------|
        | SimHei | 黑体 |
        | KaiTi | 楷体 |
        | SimSun | 宋体 |
        | FangSong | 仿宋 |
        | Microsoft YaHei | 微软雅黑 |
        """)

if __name__ == "__main__":
    main()