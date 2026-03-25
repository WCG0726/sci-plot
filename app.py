"""
app.py - 主入口文件 (优化版)
==========================
SciPlot - 科研绘图工具 Web版

启动方法:
    streamlit run app.py
"""

import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

# 导入配置
from config import PAGE_CONFIG, CUSTOM_CSS, OriginStyleConfig

# ============================================================
# 图表数据格式说明
# ============================================================

CHART_FORMATS = {
    "折线图": {
        "desc": "显示数据随时间或类别的变化趋势",
        "format": "| X轴 | Y1 | Y2 | Y3 |\n|-----|----|----|----|\n| 1   | 10 | 15 | 8  |\n| 2   | 12 | 18 | 10 |",
        "tips": "- X轴: 通常是时间、类别或数值\n- Y轴: 可选择多列，每列画一条线\n- 支持多组数据对比"
    },
    "散点图": {
        "desc": "显示两个变量之间的关系",
        "format": "| X   | Y   | Group |\n|-----|-----|-------|\n| 1.2 | 3.4 | A     |\n| 2.1 | 4.5 | B     |",
        "tips": "- X/Y: 两列数值数据\n- Group: (可选)分组列，不同组用不同颜色"
    },
    "柱状图": {
        "desc": "比较不同类别的数据大小",
        "format": "| Category | Score1 | Score2 |\n|----------|--------|--------|\n| A        | 85     | 78     |\n| B        | 90     | 82     |",
        "tips": "- Category: 类别名称\n- Score: 可选择多列，生成分组柱状图\n- 支持多组数据对比"
    },
    "误差线图": {
        "desc": "显示数据的均值和误差范围",
        "format": "| X   | Mean | Std |\n|-----|------|-----|\n| 1   | 10   | 1.5 |\n| 2   | 15   | 2.0 |",
        "tips": "- X: 类别或数值\n- Mean: 均值\n- Std: 标准差(误差范围)"
    },
    "箱线图": {
        "desc": "显示数据分布特征",
        "format": "| Group | Value |\n|-------|-------|\n| A     | 10    |\n| A     | 12    |\n| B     | 15    |",
        "tips": "- Group: 分组列\n- Value: 数值列\n- 自动计算统计特征"
    },
    "热力图": {
        "desc": "显示数据矩阵或相关性",
        "format": "| V1  | V2  | V3  |\n|-----|-----|-----|\n| 1.0 | 0.8 | 0.3 |\n| 0.8 | 1.0 | 0.5 |",
        "tips": "- 多列数值数据\n- 自动计算相关性矩阵\n- 颜色深浅表示相关性强弱"
    },
    "山脊图": {
        "desc": "多组数据密度分布对比",
        "format": "| Group1 | Group2 | Group3 |\n|--------|--------|--------|\n| 10     | 15     | 8      |\n| 12     | 18     | 10     |",
        "tips": "- 每列代表一组数据\n- 显示各组的概率密度分布"
    },
    "双Y轴图": {
        "desc": "共享X轴，两个Y轴显示不同量纲数据",
        "format": "| Time | Temp | Pressure |\n|------|------|----------|\n| 1    | 25   | 101      |\n| 2    | 28   | 102      |",
        "tips": "- Time: X轴(共享)\n- Temp: 左Y轴\n- Pressure: 右Y轴"
    },
    "子图组合": {
        "desc": "多个图表组合展示",
        "format": "任意格式的数据都可以\n选择多列数据分别绘制",
        "tips": "- 可选择1x2, 2x2等布局\n- 每个子图可选择不同数据"
    },
    "桑基图": {
        "desc": "显示流量或转移关系",
        "format": "手动输入节点和流量:\n- 节点: A, B, C, D\n- 流量: 10, -3, -4, -3",
        "tips": "- 正值表示流入\n- 负值表示流出"
    },
    "环形图": {
        "desc": "显示各部分占比",
        "format": "| Label | Value |\n|-------|-------|\n| A     | 35    |\n| B     | 25    |",
        "tips": "- Label: 类别名称\n- Value: 数值(自动计算百分比)"
    },
    "堆叠面积图": {
        "desc": "多系列数据堆叠展示",
        "format": "| Time | Series1 | Series2 |\n|------|---------|---------|\n| 1    | 10      | 5       |\n| 2    | 12      | 8       |",
        "tips": "- Time: X轴\n- Series: 多列数据堆叠显示"
    },
    "平行坐标图": {
        "desc": "多维数据对比",
        "format": "| Feature1 | Feature2 | Group |\n|----------|----------|-------|\n| 10       | 20       | A     |\n| 15       | 25       | B     |",
        "tips": "- 多列特征数据\n- Group: (可选)分类列"
    },
}

# 导入组件
from components import (
    data_input_section,
    data_editor_section,
    show_data_preview,
    axis_settings_section,
    style_settings_section
)

# 导入图表
from charts import CHART_TYPES

# 导入工具函数
from utils import setup_plot_style

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# 主界面
# ============================================================

def main():
    # 顶部标题栏
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 SciPlot")
        st.caption("基于matplotlib的专业科研绘图工具 | 集成Show2Know图表类型")
    with col2:
        st.markdown("""
        <div style="text-align: right; padding-top: 20px;">
            <a href="https://github.com/WCG0726/sci-plot" target="_blank">
                <img src="img.shields.io/badge/GitHub-⭐ Star-blue" alt="GitHub">
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 数据输入区域（只在侧边栏调用一次）
    df = data_input_section()
    
    # 使用session state共享数据
    if df is not None:
        st.session_state.current_data = df
    
    # 使用Tab页组织功能
    tab1, tab2, tab3 = st.tabs(["📊 绘图", "📝 数据", "❓ 帮助"])
    
    with tab1:
        plot_tab()
    
    with tab2:
        data_tab()
    
    with tab3:
        help_tab()


def plot_tab():
    """绘图主界面"""
    # 从session state获取数据
    df = st.session_state.get('current_data', None)
    
    if df is None:
        st.info("👈 请在左侧选择数据来源开始绘图")
        show_quick_start()
        return
    
    # 主区域布局：左中右三栏
    col_left, col_center = st.columns([1, 3])
    
    with col_left:
        # 图表类型选择
        st.markdown("### 📊 图表类型")
        chart_type = st.radio(
            "选择图表",
            list(CHART_TYPES.keys()),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 快速样式设置
        st.markdown("### 🎨 快速样式")
        quick_style = quick_style_section()
        
        # 显示数据格式说明
        st.markdown("---")
        show_data_format(chart_type)
        
        st.markdown("---")
        
        # 坐标轴设置（可折叠）
        with st.expander("📐 坐标轴设置"):
            config = axis_settings_section()
        
        # 使用默认配置补充
        default_config = get_default_config()
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        style = quick_style
    
    with col_center:
        # 图表预览区域
        st.markdown("### 📈 图表预览")
        
        # 绘制图表
        fig = CHART_TYPES[chart_type](df, config, style)
        
        # 显示图表
        st.pyplot(fig, use_container_width=True)
        
        # 导出按钮（放在图表下方）
        export_section(fig)


def data_tab():
    """数据管理界面"""
    st.markdown("### 📝 数据管理")
    
    # 从session state获取数据
    df = st.session_state.get('current_data', None)
    
    if df is not None:
        # 数据预览
        show_data_preview(df)
        
        # 数据编辑
        df = data_editor_section(df)
        
        # 更新session state中的数据
        st.session_state.current_data = df
    else:
        st.info("👈 请在左侧选择数据来源")


def help_tab():
    """帮助界面"""
    st.markdown("### ❓ 使用帮助")
    
    show_help()


def quick_style_section():
    """快速样式设置"""
    style = {}
    
    # 配色方案
    from config import OriginStyleConfig
    preset_name = st.selectbox(
        "配色方案",
        list(OriginStyleConfig.COLOR_PRESETS.keys()),
        index=0
    )
    style['custom_colors'] = OriginStyleConfig.COLOR_PRESETS[preset_name]
    style['use_custom_colors'] = False
    
    # 颜色预览
    colors = OriginStyleConfig.COLOR_PRESETS[preset_name]
    preview_html = '<div style="display: flex; gap: 2px; margin: 5px 0;">'
    for c in colors:
        preview_html += f'<div style="width: 25px; height: 15px; background: {c}; border-radius: 2px;"></div>'
    preview_html += '</div>'
    st.markdown(preview_html, unsafe_allow_html=True)
    
    # 线型
    style['line_style'] = st.selectbox("线型", ['实线', '虚线', '点线', '点划线'], index=0)
    style['line_style_code'] = {'实线': '-', '虚线': '--', '点线': ':', '点划线': '-.'}[style['line_style']]
    
    # 标记
    style['marker'] = st.selectbox("标记", ['圆圈', '方块', '三角形', '菱形', '无'], index=0)
    style['marker_code'] = {'圆圈': 'o', '方块': 's', '三角形': '^', '菱形': 'D', '无': ''}[style['marker']]
    
    # 线宽和标记大小
    col1, col2 = st.columns(2)
    with col1:
        style['line_width'] = st.slider("线宽", 0.5, 5.0, 1.5, step=0.5)
    with col2:
        style['marker_size'] = st.slider("标记大小", 2, 15, 6)
    
    # 填充透明度
    style['fill_alpha'] = st.slider("填充透明度", 0.0, 1.0, 0.0, step=0.1)
    
    return style


def get_default_config():
    """获取默认配置"""
    return {
        'title': '',
        'xlabel': '',
        'ylabel': '',
        'en_font': 'Times New Roman',
        'cn_font': 'SimHei',
        'title_fontsize': 16,
        'title_bold': True,
        'label_fontsize': 14,
        'labelpad': 5,
        'show_border': True,
        'border_width': 1.0,
        'show_grid': False,
        'grid_color': '#CCCCCC',
        'grid_linewidth': 0.5,
        'grid_alpha': 0.8,
        'tick_dir': 'in',
        'tick_width': 1.0,
        'tick_length': 5,
        'tick_labelsize': 12,
        'tick_rotation': 0,
        'x_min': 0.0,
        'x_max': 10.0,
        'y_min': 0.0,
        'y_max': 10.0,
        'x_interval': 1.0,
        'y_interval': 1.0,
        'auto_range': True,
        'show_legend': True,
        'legend_loc': 'best',
        'legend_fontsize': 10,
        'legend_frame': True,
    }


def export_section(fig):
    """导出图表"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col1:
        filename = st.text_input("文件名", value="sci_plot_output", label_visibility="collapsed", placeholder="文件名")
    
    with col2:
        fmt = st.selectbox("格式", ['png', 'pdf', 'svg', 'eps'], label_visibility="collapsed")
    
    with col3:
        dpi = st.selectbox("DPI", [150, 300, 600], index=1, label_visibility="collapsed")
    
    with col4:
        buf = BytesIO()
        fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        
        st.download_button(
            label=f"⬇️ 下载 {fmt.upper()}",
            data=buf,
            file_name=f"{filename}.{fmt}",
            mime=f"image/{fmt}",
            use_container_width=True
        )


def show_quick_start():
    """显示快速开始指南"""
    st.markdown("---")
    st.markdown("### 🚀 快速开始")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **第一步：上传数据**
        - 支持CSV、Excel、TSV
        - 或使用示例数据
        """)
    
    with col2:
        st.markdown("""
        **第二步：选择图表**
        - 13种图表类型
        - 一键切换配色
        """)
    
    with col3:
        st.markdown("""
        **第三步：导出图片**
        - PNG/PDF/SVG格式
        - 300DPI高清输出
        """)
    
    # 示例图表
    st.markdown("---")
    st.markdown("### 📊 示例图表")
    
    col1, col2 = st.columns(2)
    
    with col1:
        import numpy as np
        np.random.seed(42)
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 50)
        ax.plot(x, np.sin(x), color='#E64B35', label='sin(x)', marker='o', markersize=4)
        ax.plot(x, np.cos(x), color='#4DBBD5', label='cos(x)', marker='s', markersize=4)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        ax.set_title('折线图示例')
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        x, y = np.random.randn(50), np.random.randn(50)
        ax.scatter(x, y, c='#00A087', s=50, alpha=0.7, edgecolors='white')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('散点图示例')
        st.pyplot(fig)


def show_data_format(chart_type):
    """显示数据格式说明"""
    st.markdown("### 📋 数据格式")
    
    if chart_type in CHART_FORMATS:
        info = CHART_FORMATS[chart_type]
        
        st.markdown(f"**{info['desc']}**")
        
        with st.expander("查看数据格式示例", expanded=True):
            st.code(info['format'], language="text")
        
        st.markdown(info['tips'])


def show_help():
    """显示帮助信息"""
    st.markdown("""
    ### 支持的图表类型
    
    | 类别 | 图表 | 说明 |
    |------|------|------|
    | 基础 | 折线图、散点图、柱状图、误差线图 | 显示趋势和分布 |
    | 统计 | 箱线图、热力图、山脊图 | 数据统计分析 |
    | 高级 | 双Y轴图、子图组合、桑基图 | 复杂数据可视化 |
    | 特殊 | 环形图、堆叠面积图、平行坐标图 | 特定场景应用 |
    
    ### 字体设置
    - **英文字体**: Times New Roman, Arial等
    - **中文字体**: 黑体(SimHei), 楷体(KaiTi), 宋体(SimSun)等
    
    ### 坐标轴设置
    - **边框**: 显示/隐藏，宽度可调
    - **网格线**: 颜色、线宽、透明度
    - **刻度**: 方向(in/out)、大小、粗细
    - **刻度范围**: 手动设置X/Y轴范围和间隔
    
    ### 致谢
    部分图表代码参考自 [Show2Know](https://github.com/Winn1y/Show2Know)
    
    ### 参考文档
    - [Matplotlib中文文档](https://matplotlib.net.cn/stable/)
    - [用户指南](https://matplotlib.net.cn/stable/users/index.html)
    """)


if __name__ == "__main__":
    main()