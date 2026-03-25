"""
sci_plot_web.py - 科研绘图工具 Web版 (增强版)
=============================================
使用Streamlit构建的交互式科研绘图界面

功能:
- 配色系统: Nature/ColorBrewer/色盲友好
- 图例控制: 位置/样式/字号
- 模板系统: 保存/加载配置
- 批量出图: 多文件处理
- 数据预处理: 缺失值/类型转换

启动方法:
    streamlit run sci_plot_web.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from io import BytesIO
import json

# 导入核心库
from sci_plot import SciPlot, ColorPalettes

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
# 中文字体自动检测
# ============================================================
def setup_chinese_font():
    chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Noto Sans CJK SC',
                     'WenQuanYi Micro Hei', 'PingFang SC', 'Heiti SC']
    available = {f.name for f in fm.fontManager.ttflist}
    for font in chinese_fonts:
        if font in available:
            plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            return font
    return None

CN_FONT = setup_chinese_font()

# ============================================================
# 自定义样式
# ============================================================
st.markdown("""
<style>
    .stButton button {background-color: #00A087; color: white; border-radius: 5px;}
    .stButton button:hover {background-color: #008066;}
    .color-box {display: inline-block; width: 30px; height: 20px; margin: 2px; border-radius: 3px;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 辅助函数
# ============================================================

def setup_plot_style(config):
    """根据配置设置绘图样式"""
    plt.rcParams.update({
        'font.size': config.get('fontsize', 10),
        'figure.figsize': config.get('figsize', (8, 6)),
        'figure.dpi': 150,
        'axes.linewidth': 1.0,
        'lines.linewidth': 1.5,
        'lines.markersize': 6,
    })
    
    if config.get('tick_inward', True):
        plt.rcParams.update({
            'xtick.direction': 'in', 'ytick.direction': 'in',
            'xtick.top': True, 'ytick.right': True,
        })
    else:
        plt.rcParams.update({
            'xtick.direction': 'out', 'ytick.direction': 'out',
            'xtick.top': False, 'ytick.right': False,
        })

def get_colors(palette_name, n=10):
    """获取配色方案"""
    return ColorPalettes.get_palette(palette_name, n)

def display_color_preview(palette_name):
    """显示配色预览"""
    colors = get_colors(palette_name, 8)
    html = '<div style="display: flex; gap: 2px; margin: 5px 0;">'
    for c in colors:
        html += f'<div class="color-box" style="background-color: {c};"></div>'
    html += '</div>'
    st.sidebar.markdown(html, unsafe_allow_html=True)

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
            type=['csv', 'xlsx', 'xls', 'tsv', 'json'],
            help="支持 CSV, Excel, TSV, JSON 格式"
        )
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.tsv'):
                    df = pd.read_csv(uploaded_file, sep='\t')
                elif uploaded_file.name.endswith('.json'):
                    df = pd.read_json(uploaded_file)
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
                    # 尝试转换为数字
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
            ["随机散点", "正弦余弦", "分组数据", "相关性矩阵", "时间序列", "误差线数据"]
        )
        
        np.random.seed(42)
        if example_type == "随机散点":
            df = pd.DataFrame({
                'X': np.random.randn(100),
                'Y': np.random.randn(100) * 2 + 1,
                'Group': np.random.choice(['A', 'B', 'C'], 100)
            })
        elif example_type == "正弦余弦":
            x = np.linspace(0, 10, 50)
            df = pd.DataFrame({'X': x, 'sin_X': np.sin(x), 'cos_X': np.cos(x)})
        elif example_type == "分组数据":
            df = pd.DataFrame({
                'Group': np.repeat(['A', 'B', 'C', 'D'], 30),
                'Value': np.concatenate([
                    np.random.normal(10, 2, 30), np.random.normal(12, 2.5, 30),
                    np.random.normal(8, 1.5, 30), np.random.normal(15, 3, 30)
                ])
            })
        elif example_type == "相关性矩阵":
            data = np.random.rand(5, 5)
            data = (data + data.T) / 2
            np.fill_diagonal(data, 1)
            df = pd.DataFrame(data, columns=['V1', 'V2', 'V3', 'V4', 'V5'],
                            index=['V1', 'V2', 'V3', 'V4', 'V5'])
        elif example_type == "时间序列":
            dates = pd.date_range('2024-01-01', periods=100)
            df = pd.DataFrame({
                'Date': dates,
                'Value_A': np.cumsum(np.random.randn(100)) + 100,
                'Value_B': np.cumsum(np.random.randn(100)) + 50
            })
        else:  # 误差线数据
            df = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D', 'E'],
                'Mean': [23, 45, 56, 78, 32],
                'Std': [3, 5, 4, 6, 3]
            })
        
        st.sidebar.success(f"✅ {example_type}")
    
    return df

# ============================================================
# 数据预处理
# ============================================================

def data_preprocessing(df):
    """数据预处理"""
    st.sidebar.markdown("---")
    st.sidebar.header("🔧 数据预处理")
    
    # 缺失值处理
    missing_action = st.sidebar.selectbox(
        "缺失值处理",
        ["保持不变", "删除含缺失行", "填充0", "填充均值"]
    )
    
    if missing_action == "删除含缺失行":
        df = df.dropna()
    elif missing_action == "填充0":
        df = df.fillna(0)
    elif missing_action == "填充均值":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    return df

# ============================================================
# 图表配置模块
# ============================================================

def chart_config_section():
    """图表配置区域"""
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ 图表配置")
    
    config = {}
    
    # 基本配置
    config['title'] = st.sidebar.text_input("图表标题", value="My Chart")
    config['xlabel'] = st.sidebar.text_input("X轴标签", value="")
    config['ylabel'] = st.sidebar.text_input("Y轴标签", value="")
    
    # 图片尺寸
    st.sidebar.subheader("📐 图片尺寸")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config['figsize_w'] = st.slider("宽度", 4, 16, 8)
    with col2:
        config['figsize_h'] = st.slider("高度", 3, 12, 6)
    config['figsize'] = (config['figsize_w'], config['figsize_h'])
    
    # 配色方案
    st.sidebar.subheader("🎨 配色方案")
    
    palettes = ColorPalettes.list_palettes()
    all_palettes = []
    for category, names in palettes.items():
        all_palettes.extend(names)
    
    config['palette'] = st.sidebar.selectbox("选择配色", all_palettes, index=0)
    display_color_preview(config['palette'])
    
    # 顺序/发散配色
    config['cmap'] = st.sidebar.selectbox(
        "热力图/连续配色",
        ['RdBu_r', 'coolwarm', 'viridis', 'Blues', 'YlOrRd', 'Spectral']
    )
    
    # 色盲友好模式
    config['colorblind'] = st.sidebar.checkbox("色盲友好模式", value=False)
    if config['colorblind']:
        config['palette'] = 'colorblind'
    
    # 刻度设置
    config['tick_inward'] = st.sidebar.checkbox("内向刻度", value=True)
    config['fontsize'] = st.sidebar.slider("字号", 8, 16, 10)
    
    # 图例设置
    st.sidebar.subheader("📋 图例设置")
    legend_positions = ['best', 'upper right', 'upper left', 'lower left', 
                        'lower right', 'right', 'center left', 'center right',
                        'lower center', 'upper center', 'center']
    config['legend_loc'] = st.sidebar.selectbox("图例位置", legend_positions, index=0)
    config['legend_frame'] = st.sidebar.checkbox("图例边框", value=True)
    config['legend_fontsize'] = st.sidebar.slider("图例字号", 6, 14, 9)
    
    return config

# ============================================================
# 图表绘制函数
# ============================================================

def get_colors_for_plot(config, n=10):
    """根据配置获取颜色"""
    if config.get('colorblind'):
        return ColorPalettes.get_palette('colorblind', n)
    return ColorPalettes.get_palette(config.get('palette', 'Nature'), n)

def plot_scatter(df, config):
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
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    colors = get_colors_for_plot(config)
    
    if color_col == '无':
        ax.scatter(df[x_col], df[y_col], s=50, alpha=0.7,
                   edgecolors='white', linewidth=0.5, color=colors[0])
    else:
        groups = df[color_col].unique()
        for i, group in enumerate(groups):
            mask = df[color_col] == group
            ax.scatter(df.loc[mask, x_col], df.loc[mask, y_col],
                      label=str(group), s=50, alpha=0.7,
                      edgecolors='white', color=colors[i % len(colors)])
        ax.legend(loc=config['legend_loc'], frameon=config['legend_frame'],
                 fontsize=config['legend_fontsize'])
    
    ax.set_xlabel(config.get('xlabel') or x_col)
    ax.set_ylabel(config.get('ylabel') or y_col)
    ax.set_title(config['title'])
    return fig

def plot_line(df, config):
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
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    colors = get_colors_for_plot(config)
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p']
    
    for i, y_col in enumerate(y_cols):
        ax.plot(df[x_col], df[y_col], label=y_col,
               color=colors[i % len(colors)],
               marker=markers[i % len(markers)], markersize=5)
    
    ax.set_xlabel(config.get('xlabel') or x_col)
    ax.set_ylabel(config.get('ylabel') or 'Value')
    if y_cols:
        ax.legend(loc=config['legend_loc'], frameon=config['legend_frame'],
                 fontsize=config['legend_fontsize'])
    ax.set_title(config['title'])
    return fig

def plot_bar(df, config):
    """柱状图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        cat_col = st.selectbox("类别列", all_cols, key='bar_cat')
    with col2:
        val_cols = st.multiselect("数值列", numeric_cols, key='bar_val')
    
    # 自动计算误差线
    compute_error = st.checkbox("自动计算误差线 (标准差)", value=False)
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    
    if val_cols:
        if compute_error:
            bar_data = df.groupby(cat_col)[val_cols].agg(['mean', 'std']).reset_index()
            bar_data.columns = [cat_col] + [f'{c}_{s}' for c in val_cols for s in ['mean', 'std']]
        else:
            bar_data = df.groupby(cat_col)[val_cols].mean().reset_index()
        
        x = np.arange(len(bar_data))
        width = 0.8 / len(val_cols)
        colors = get_colors_for_plot(config)
        
        for i, col in enumerate(val_cols):
            offset = (i - len(val_cols)/2 + 0.5) * width
            if compute_error:
                y = bar_data[f'{col}_mean']
                yerr = bar_data[f'{col}_std']
            else:
                y = bar_data[col]
                yerr = None
            
            ax.bar(x + offset, y, width, label=col,
                  color=colors[i % len(colors)], yerr=yerr, capsize=3)
        
        ax.set_xticks(x)
        ax.set_xticklabels(bar_data[cat_col])
        ax.legend(loc=config['legend_loc'], frameon=config['legend_frame'],
                 fontsize=config['legend_fontsize'])
    
    ax.set_xlabel(config.get('xlabel') or cat_col)
    ax.set_ylabel(config.get('ylabel') or 'Value')
    ax.set_title(config['title'])
    return fig

def plot_histogram(df, config):
    """直方图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    selected_cols = st.multiselect("选择数据列", numeric_cols, default=numeric_cols[:1])
    bins = st.slider("分箱数", 5, 100, 30)
    density = st.checkbox("显示密度", value=False)
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    colors = get_colors_for_plot(config)
    
    for i, col in enumerate(selected_cols):
        ax.hist(df[col], bins=bins, alpha=0.7, label=col, density=density,
               color=colors[i % len(colors)], edgecolor='white')
    
    if selected_cols:
        ax.legend(loc=config['legend_loc'], frameon=config['legend_frame'],
                 fontsize=config['legend_fontsize'])
    ax.set_xlabel(config.get('xlabel') or 'Value')
    ax.set_ylabel(config.get('ylabel') or ('Density' if density else 'Frequency'))
    ax.set_title(config['title'])
    return fig

def plot_pie(df, config):
    """饼图"""
    col1, col2 = st.columns(2)
    with col1:
        label_col = st.selectbox("标签列", df.columns, key='pie_label')
    with col2:
        value_col = st.selectbox("数值列", df.select_dtypes(include=[np.number]).columns, key='pie_value')
    
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = get_colors_for_plot(config, len(df))
    ax.pie(df[value_col], labels=df[label_col], autopct='%1.1f%%',
           colors=colors, startangle=90,
           wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
    ax.set_title(config['title'])
    return fig

def plot_heatmap(df, config):
    """热力图"""
    numeric_df = df.select_dtypes(include=[np.number])
    use_corr = st.checkbox("计算相关性矩阵", value=True)
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    
    if use_corr:
        plot_data = numeric_df.corr()
        center = 0
    else:
        plot_data = numeric_df
        center = None
    
    sns.heatmap(plot_data, ax=ax, cmap=config.get('cmap', 'RdBu_r'),
                annot=True, fmt='.2f', linewidths=0.5, center=center)
    ax.set_title(config['title'])
    return fig

def plot_box(df, config):
    """箱线图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        value_col = st.selectbox("数值列", numeric_cols, key='box_val')
    with col2:
        group_col = st.selectbox("分组列", ['无'] + all_cols, key='box_group')
    
    show_points = st.checkbox("显示数据点", value=False)
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    colors = get_colors_for_plot(config)
    
    if group_col != '无':
        groups = df[group_col].unique()
        data_list = [df[df[group_col] == g][value_col].values for g in groups]
        bp = ax.boxplot(data_list, labels=groups, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors[:len(groups)]):
            patch.set_facecolor(color)
        if show_points:
            for i, g in enumerate(groups):
                y = df[df[group_col] == g][value_col].values
                x = np.random.normal(i+1, 0.04, len(y))
                ax.scatter(x, y, alpha=0.4, s=10, color='black')
    else:
        bp = ax.boxplot([df[value_col]], labels=[value_col], patch_artist=True)
        bp['boxes'][0].set_facecolor(colors[0])
    
    ax.set_ylabel(config.get('ylabel') or value_col)
    ax.set_title(config['title'])
    return fig

def plot_violin(df, config):
    """小提琴图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        value_col = st.selectbox("数值列", numeric_cols, key='violin_val')
    with col2:
        group_col = st.selectbox("分组列", all_cols, key='violin_group')
    
    inner = st.selectbox("内部样式", ['box', 'quartile', 'point', 'stick'], index=0)
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    colors = get_colors_for_plot(config)
    
    groups = df[group_col].unique()
    data_list = [df[df[group_col] == g][value_col].values for g in groups]
    
    parts = ax.violinplot(data_list, showmeans=True, showmedians=(inner=='box'))
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i % len(colors)])
        pc.set_alpha(0.7)
    
    ax.set_xticks(range(1, len(groups) + 1))
    ax.set_xticklabels(groups)
    ax.set_xlabel(config.get('xlabel') or group_col)
    ax.set_ylabel(config.get('ylabel') or value_col)
    ax.set_title(config['title'])
    return fig

def plot_errorbar(df, config):
    """误差线图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("X轴", df.columns, key='err_x')
    with col2:
        y_col = st.selectbox("Y轴", numeric_cols, key='err_y')
    with col3:
        err_col = st.selectbox("误差列", numeric_cols, key='err_err')
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    colors = get_colors_for_plot(config)
    ax.errorbar(df[x_col], df[y_col], yerr=df[err_col],
                fmt='o-', capsize=5, color=colors[0], linewidth=1.5)
    ax.set_xlabel(config.get('xlabel') or x_col)
    ax.set_ylabel(config.get('ylabel') or y_col)
    ax.set_title(config['title'])
    return fig

def plot_stack(df, config):
    """堆叠面积图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        x_col = st.selectbox("X轴", df.columns, key='stack_x')
    with col2:
        y_cols = st.multiselect("Y轴数据", numeric_cols, key='stack_y')
    
    fig, ax = plt.subplots(figsize=config['figsize'])
    colors = get_colors_for_plot(config)
    
    if y_cols:
        ax.stackplot(df[x_col], *[df[c] for c in y_cols], labels=y_cols,
                     colors=colors[:len(y_cols)], alpha=0.8)
        ax.legend(loc=config['legend_loc'], frameon=config['legend_frame'],
                 fontsize=config['legend_fontsize'])
    
    ax.set_xlabel(config.get('xlabel') or x_col)
    ax.set_ylabel(config.get('ylabel') or 'Value')
    ax.set_title(config['title'])
    return fig

def plot_dual_axis(df, config):
    """双Y轴图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("X轴", df.columns, key='dual_x')
    with col2:
        y1_col = st.selectbox("左Y轴", numeric_cols, key='dual_y1')
    with col3:
        y2_col = st.selectbox("右Y轴", [c for c in numeric_cols if c != y1_col], key='dual_y2')
    
    colors = get_colors_for_plot(config)
    
    fig, ax1 = plt.subplots(figsize=config['figsize'])
    ax1.plot(df[x_col], df[y1_col], color=colors[0], marker='o', label=y1_col)
    ax1.set_xlabel(config.get('xlabel') or x_col)
    ax1.set_ylabel(y1_col, color=colors[0])
    ax1.tick_params(axis='y', labelcolor=colors[0])
    
    ax2 = ax1.twinx()
    ax2.plot(df[x_col], df[y2_col], color=colors[1], marker='s', label=y2_col)
    ax2.set_ylabel(y2_col, color=colors[1])
    ax2.tick_params(axis='y', labelcolor=colors[1])
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc=config['legend_loc'],
              frameon=config['legend_frame'], fontsize=config['legend_fontsize'])
    
    ax1.set_title(config['title'])
    return fig

# ============================================================
# 模板管理
# ============================================================

def template_section():
    """模板管理区域"""
    st.sidebar.markdown("---")
    st.sidebar.header("💾 模板管理")
    
    # 保存模板
    if st.sidebar.button("保存当前配置为模板"):
        if 'current_config' in st.session_state:
            config_json = json.dumps(st.session_state.current_config, indent=2)
            st.sidebar.download_button(
                label="下载模板",
                data=config_json,
                file_name="sci_plot_template.json",
                mime="application/json"
            )
    
    # 加载模板
    uploaded_template = st.sidebar.file_uploader("加载模板", type=['json'])
    if uploaded_template:
        try:
            template_config = json.load(uploaded_template)
            st.session_state.template_config = template_config
            st.sidebar.success("模板已加载")
        except Exception as e:
            st.sidebar.error(f"加载失败: {e}")

# ============================================================
# 导出模块
# ============================================================

def export_section(fig):
    """导出图表"""
    st.markdown("---")
    st.subheader("📥 导出图表")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        dpi = st.selectbox("分辨率", [150, 300, 600], index=1)
    with col2:
        fmt = st.selectbox("格式", ['png', 'pdf', 'svg', 'eps'])
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

# ============================================================
# 主界面
# ============================================================

def main():
    st.title("📊 SciPlot - 科研绘图工具")
    st.markdown("---")
    
    # 数据输入
    df = data_input_section()
    
    if df is not None:
        # 数据预处理
        df = data_preprocessing(df)
        
        # 数据预览
        with st.expander("📋 数据预览", expanded=False):
            st.dataframe(df.head(20))
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**行数:** {df.shape[0]}")
                st.write(f"**列数:** {df.shape[1]}")
            with col2:
                st.write(f"**数值列:** {len(df.select_dtypes(include=[np.number]).columns)}")
                st.write(f"**类别列:** {len(df.select_dtypes(exclude=[np.number]).columns)}")
            
            # 列统计
            if st.checkbox("显示列统计"):
                st.dataframe(df.describe())
        
        # 图表配置
        config = chart_config_section()
        
        # 保存配置到session
        st.session_state.current_config = config
        
        # 模板管理
        template_section()
        
        # 设置样式
        setup_plot_style(config)
        
        # 选择图表类型
        st.markdown("---")
        chart_type = st.selectbox(
            "📊 选择图表类型",
            ["散点图", "折线图", "柱状图", "直方图", "饼图",
             "热力图", "箱线图", "小提琴图", "误差线图", "堆叠面积图", "双Y轴图"]
        )
        
        # 绘制图表
        chart_functions = {
            "散点图": plot_scatter,
            "折线图": plot_line,
            "柱状图": plot_bar,
            "直方图": plot_histogram,
            "饼图": plot_pie,
            "热力图": plot_heatmap,
            "箱线图": plot_box,
            "小提琴图": plot_violin,
            "误差线图": plot_errorbar,
            "堆叠面积图": plot_stack,
            "双Y轴图": plot_dual_axis,
        }
        
        fig = chart_functions[chart_type](df, config)
        
        # 显示图表
        st.pyplot(fig)
        
        # 导出
        export_section(fig)
    
    else:
        st.info("👈 请在左侧选择数据来源开始绘图")
        
        # 显示示例
        st.markdown("---")
        st.subheader("🎨 示例图表")
        
        col1, col2 = st.columns(2)
        with col1:
            np.random.seed(42)
            fig, ax = plt.subplots(figsize=(6, 4))
            x, y = np.random.randn(50), np.random.randn(50)
            ax.scatter(x, y, c='#E64B35', s=50, alpha=0.7, edgecolors='white')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title('Scatter Plot')
            st.pyplot(fig)
        
        with col2:
            x = np.linspace(0, 10, 30)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(x, np.sin(x), color='#E64B35', label='sin(x)', marker='o', markersize=4)
            ax.plot(x, np.cos(x), color='#4DBBD5', label='cos(x)', marker='s', markersize=4)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.legend()
            ax.set_title('Line Plot')
            st.pyplot(fig)

if __name__ == "__main__":
    main()