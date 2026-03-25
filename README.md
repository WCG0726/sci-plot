# SciPlot - 科研绘图工具

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20+-red.svg)](https://streamlit.io/)

**一个开箱即用的科研绘图工具，支持Web版和桌面版**

**🌐 在线体验: [https://sci-plot-wcg-ai.streamlit.app/](https://sci-plot-wcg-ai.streamlit.app/)**

[功能特点](#功能特点) • [快速开始](#快速开始) • [图表类型](#图表类型) • [配色方案](#配色方案) • [使用示例](#使用示例)

</div>

---

## 功能特点

- **11种图表类型**: 散点图、折线图、柱状图、直方图、饼图、热力图、箱线图、小提琴图、误差线图、堆叠面积图、双Y轴图
- **50+配色方案**: Nature默认、ColorBrewer定性/顺序/发散、感知均匀、色盲友好
- **中文字体自动检测**: 支持微软雅黑、黑体、宋体等
- **实时预览**: 参数变更自动更新图表
- **模板系统**: 保存/加载配置模板
- **双版本支持**: Web版(Streamlit) + 桌面版(Tkinter)
- **多格式导出**: PNG、PDF、SVG、EPS

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装:

```bash
pip install matplotlib numpy pandas seaborn streamlit openpyxl
```

### 2. Web版启动 (模块化版本)

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

### 旧版本 (单文件)

```bash
streamlit run sci_plot_web.py
```

### 3. 桌面版启动

```bash
python sci_plot_gui.py
```

---

## 图表类型

| 图表类型 | 方法 | 说明 |
|---------|------|------|
| 散点图 | `sp.scatter()` | 支持颜色分组 |
| 折线图 | `sp.line()` | 支持多系列 |
| 柱状图 | `sp.bar()` | 支持误差线 |
| 直方图 | `sp.histogram()` | 支持多组对比 |
| 饼图 | `sp.pie()` | 百分比显示 |
| 热力图 | `sp.heatmap()` | 相关性矩阵 |
| 箱线图 | `sp.box()` | 支持数据点 |
| 小提琴图 | `sp.violin()` | 分布可视化 |
| 误差线图 | `sp.errorbar()` | 自动计算 |
| 堆叠面积图 | `sp.stack()` | 多系列堆叠 |
| 双Y轴图 | `sp.dual_axis()` | 双坐标轴 |

---

## 配色方案

### Nature默认配色
```
#E64B35 #4DBBD5 #00A087 #3C5488 #F39B7F
#8491B4 #91D1C2 #DC0000 #7E6148 #B09C85
```

### ColorBrewer定性配色
- Set1, Set2, Set3, Paired, Dark2, Accent

### ColorBrewer顺序配色
- Blues, Greens, Reds, YlOrRd, YlGnBu, PuRd

### ColorBrewer发散配色
- RdBu, RdYlGn, Spectral, PiYG

### 感知均匀配色
- viridis, plasma, inferno, magma, cividis

### 色盲友好配色
- 内置8色色盲友好方案

---

## 使用示例

### 核心库使用

```python
from sci_plot import SciPlot as sp
import numpy as np

# 散点图
x = np.random.randn(100)
y = np.random.randn(100)
sp.scatter(x, y, xlabel='X', ylabel='Y', title='Scatter Plot')

# 折线图
x = np.linspace(0, 10, 50)
sp.line(x, [np.sin(x), np.cos(x)], labels=['sin', 'cos'])

# 柱状图
sp.bar(['A', 'B', 'C'], [10, 20, 30], title='Bar Plot')

# 切换配色
sp.config.palette = 'Set1'

# 保存图片
sp.config.save('output', ['png', 'pdf'])
```

### Web版界面

1. 上传CSV/Excel数据
2. 选择图表类型
3. 调整配色和图例
4. 下载图片

### 桌面版界面

1. 文件菜单加载数据
2. 左侧面板选择图表类型
3. 实时调整参数
4. 保存图片或模板

---

## 项目结构

```
sci-plot/
├── sci_plot.py          # 核心绘图库
├── sci_plot_web.py      # Web版界面 (Streamlit)
├── sci_plot_gui.py      # 桌面版界面 (Tkinter)
├── requirements.txt     # 依赖列表
├── .gitignore          # Git忽略文件
└── README.md           # 项目说明
```

---

## 配置选项

```python
sp.config.font = 'Arial'           # 字体
sp.config.fontsize = 10            # 字号
sp.config.dpi = 300                # 分辨率
sp.config.figsize = (8, 6)         # 图片尺寸
sp.config.tick_inward = True       # 内向刻度
sp.config.palette = 'Nature'       # 配色方案
sp.config.legend_loc = 'best'      # 图例位置
sp.config.legend_frame = True      # 图例边框
```

---

## 导出格式

- **PNG**: 高分辨率位图，适合论文插图
- **PDF**: 矢量图，适合论文发表
- **SVG**: 矢量图，适合网页展示
- **EPS**: 矢量图，适合LaTeX

---

## 依赖要求

- Python 3.8+
- matplotlib >= 3.5.0
- numpy >= 1.20.0
- pandas >= 1.3.0
- seaborn >= 0.11.0
- streamlit >= 1.20.0 (Web版)

---

## 许可证

MIT License

---

## 致谢

- 配色方案参考 [ColorBrewer](https://colorbrewer2.org/)
- 灵感来源 [Show2Know](https://github.com/Winn1y/Show2Know)

---

## 更新日志

### v2.0 (增强版)
- 新增中文字体自动检测
- 新增50+配色方案
- 新增色盲友好模式
- 新增图例控制
- 新增实时预览
- 新增模板系统
- 新增双Y轴图表

### v1.0 (基础版)
- 支持10种基础图表
- Nature风格配色
- 支持CSV/Excel数据
- 支持多格式导出
