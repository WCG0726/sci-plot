"""
app.py - 主入口文件
==================
SciPlot - 科研绘图工具 Web版 (模块化版本)

启动方法:
    streamlit run app.py
"""

import streamlit as st
from io import BytesIO

# 导入配置
from config import PAGE_CONFIG, CUSTOM_CSS

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
    st.title("📊 SciPlot - 科研绘图工具")
    st.markdown("基于matplotlib的专业科研绘图工具，集成Show2Know图表类型")
    st.markdown("---")
    
    # 数据输入
    df = data_input_section()
    
    if df is not None:
        # 数据预览和编辑
        show_data_preview(df)
        df = data_editor_section(df)
        
        # 坐标轴设置
        config = axis_settings_section()
        
        # 样式设置
        style = style_settings_section()
        
        # 选择图表类型
        st.markdown("---")
        chart_type = st.selectbox(
            "📊 选择图表类型",
            list(CHART_TYPES.keys())
        )
        
        # 绘制图表
        fig = CHART_TYPES[chart_type](df, config, style)
        
        # 显示图表
        st.pyplot(fig)
        
        # 导出
        export_section(fig)
    
    else:
        st.info("👈 请在左侧选择数据来源开始绘图")
        show_help()


def export_section(fig):
    """导出图表"""
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


def show_help():
    """显示帮助信息"""
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