"""
sci_plot_gui.py - 科研绘图工具 桌面版 (增强版)
==============================================
使用Tkinter构建的交互式科研绘图界面

功能:
- 实时预览: 参数变更自动更新图表
- 配色系统: Nature/ColorBrewer/色盲友好
- 图例控制: 位置/样式/字号
- 双Y轴支持
- 子图组合
- 模板保存/加载

启动方法:
    python sci_plot_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
import os
import json

# 导入核心库
from sci_plot import SciPlot, ColorPalettes

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

class SciPlotGUI:
    """科研绘图工具桌面版 (增强版)"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SciPlot - 科研绘图工具")
        self.root.geometry("1400x900")
        
        # 数据
        self.df = None
        self.fig = None
        self.canvas = None
        self.toolbar = None
        
        # 实时预览标志
        self._updating = False
        
        # 创建界面
        self.create_menu()
        self.create_widgets()
        
        # 设置初始样式
        self.apply_style()
    
    def apply_style(self):
        """应用绘图样式"""
        tick_inward = self.tick_inward.get() if hasattr(self, 'tick_inward') else True
        
        plt.rcParams.update({
            'font.size': 10,
            'axes.linewidth': 1.0,
            'axes.spines.top': True,
            'axes.spines.right': True,
            'lines.linewidth': 1.5,
            'lines.markersize': 6,
            'legend.frameon': True,
            'legend.framealpha': 1.0,
            'legend.edgecolor': 'black',
        })
        
        if tick_inward:
            plt.rcParams.update({
                'xtick.direction': 'in', 'ytick.direction': 'in',
                'xtick.top': True, 'ytick.right': True,
            })
        else:
            plt.rcParams.update({
                'xtick.direction': 'out', 'ytick.direction': 'out',
                'xtick.top': False, 'ytick.right': False,
            })
    
    def get_colors(self, n=10):
        """获取当前配色"""
        palette = self.palette_var.get() if hasattr(self, 'palette_var') else 'Nature'
        if self.colorblind_var.get() if hasattr(self, 'colorblind_var') else False:
            palette = 'colorblind'
        return ColorPalettes.get_palette(palette, n)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开CSV", command=self.load_csv)
        file_menu.add_command(label="打开Excel", command=self.load_excel)
        file_menu.add_command(label="打开TSV", command=self.load_tsv)
        file_menu.add_separator()
        file_menu.add_command(label="保存图片", command=self.save_figure)
        file_menu.add_command(label="保存模板", command=self.save_template)
        file_menu.add_command(label="加载模板", command=self.load_template)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 示例菜单
        demo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="示例数据", menu=demo_menu)
        demo_menu.add_command(label="随机散点", command=lambda: self.load_example('scatter'))
        demo_menu.add_command(label="正弦余弦", command=lambda: self.load_example('sincos'))
        demo_menu.add_command(label="分组数据", command=lambda: self.load_example('group'))
        demo_menu.add_command(label="相关性矩阵", command=lambda: self.load_example('corr'))
        demo_menu.add_command(label="时间序列", command=lambda: self.load_example('timeseries'))
        demo_menu.add_command(label="误差线数据", command=lambda: self.load_example('errorbar'))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧控制面板 (使用Canvas+Scrollbar实现滚动)
        left_container = ttk.Frame(main_frame, width=320)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_container.pack_propagate(False)
        
        # 创建滚动Canvas
        canvas_left = tk.Canvas(left_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas_left.yview)
        self.left_frame = ttk.Frame(canvas_left)
        
        self.left_frame.bind(
            "<Configure>",
            lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        )
        
        canvas_left.create_window((0, 0), window=self.left_frame, anchor="nw")
        canvas_left.configure(yscrollcommand=scrollbar.set)
        
        canvas_left.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 右侧图表区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === 左侧控制面板内容 ===
        self.create_data_section()
        self.create_chart_type_section()
        self.create_options_section()
        self.create_config_section()
        self.create_palette_section()
        self.create_legend_section()
        self.create_buttons_section()
        
        # === 右侧图表区域 ===
        self.canvas_frame = ttk.Frame(right_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.toolbar_frame = ttk.Frame(right_frame)
        self.toolbar_frame.pack(fill=tk.X)
    
    def create_data_section(self):
        """数据信息区域"""
        frame = ttk.LabelFrame(self.left_frame, text="📁 数据信息", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))
        
        self.info_label = ttk.Label(frame, text="未加载数据")
        self.info_label.pack(anchor=tk.W)
        
        ttk.Button(frame, text="预览数据", command=self.preview_data).pack(fill=tk.X, pady=2)
    
    def create_chart_type_section(self):
        """图表类型区域"""
        frame = ttk.LabelFrame(self.left_frame, text="📊 图表类型", padding=5)
        frame.pack(fill=tk.X, pady=5)
        
        self.chart_type = tk.StringVar(value="散点图")
        chart_types = ["散点图", "折线图", "柱状图", "直方图", "饼图",
                       "热力图", "箱线图", "小提琴图", "误差线图", "堆叠面积图", "双Y轴图"]
        
        # 使用Combobox更节省空间
        self.chart_combo = ttk.Combobox(frame, textvariable=self.chart_type,
                                        values=chart_types, state='readonly')
        self.chart_combo.pack(fill=tk.X)
        self.chart_combo.bind('<<ComboboxSelected>>', lambda e: self.update_options())
    
    def create_options_section(self):
        """图表选项区域"""
        self.options_frame = ttk.LabelFrame(self.left_frame, text="⚙️ 图表选项", padding=5)
        self.options_frame.pack(fill=tk.X, pady=5)
    
    def create_config_section(self):
        """配置区域"""
        frame = ttk.LabelFrame(self.left_frame, text="📐 配置", padding=5)
        frame.pack(fill=tk.X, pady=5)
        
        # 标题
        ttk.Label(frame, text="标题:").pack(anchor=tk.W)
        self.title_entry = ttk.Entry(frame)
        self.title_entry.insert(0, "图表标题")
        self.title_entry.pack(fill=tk.X, pady=2)
        self.title_entry.bind('<KeyRelease>', lambda e: self.schedule_update())
        
        # X轴标签
        ttk.Label(frame, text="X轴标签:").pack(anchor=tk.W)
        self.xlabel_entry = ttk.Entry(frame)
        self.xlabel_entry.pack(fill=tk.X, pady=2)
        self.xlabel_entry.bind('<KeyRelease>', lambda e: self.schedule_update())
        
        # Y轴标签
        ttk.Label(frame, text="Y轴标签:").pack(anchor=tk.W)
        self.ylabel_entry = ttk.Entry(frame)
        self.ylabel_entry.pack(fill=tk.X, pady=2)
        self.ylabel_entry.bind('<KeyRelease>', lambda e: self.schedule_update())
        
        # 内向刻度
        self.tick_inward = tk.BooleanVar(value=True)
        cb = ttk.Checkbutton(frame, text="内向刻度", variable=self.tick_inward,
                            command=self.schedule_update)
        cb.pack(anchor=tk.W)
        
        # 图片尺寸
        size_frame = ttk.Frame(frame)
        size_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(size_frame, text="宽度:").pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=8)
        spin_w = ttk.Spinbox(size_frame, from_=4, to=16, textvariable=self.width_var, width=4)
        spin_w.pack(side=tk.LEFT, padx=2)
        spin_w.bind('<Return>', lambda e: self.schedule_update())
        
        ttk.Label(size_frame, text="高度:").pack(side=tk.LEFT, padx=(10,0))
        self.height_var = tk.IntVar(value=6)
        spin_h = ttk.Spinbox(size_frame, from_=3, to=12, textvariable=self.height_var, width=4)
        spin_h.pack(side=tk.LEFT, padx=2)
        spin_h.bind('<Return>', lambda e: self.schedule_update())
    
    def create_palette_section(self):
        """配色方案区域"""
        frame = ttk.LabelFrame(self.left_frame, text="🎨 配色方案", padding=5)
        frame.pack(fill=tk.X, pady=5)
        
        # 配色选择
        palettes = []
        for category, names in ColorPalettes.list_palettes().items():
            palettes.extend(names)
        
        self.palette_var = tk.StringVar(value='Nature')
        self.palette_combo = ttk.Combobox(frame, textvariable=self.palette_var,
                                          values=palettes, state='readonly')
        self.palette_combo.pack(fill=tk.X, pady=2)
        self.palette_combo.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
        
        # 色盲友好
        self.colorblind_var = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(frame, text="色盲友好模式", variable=self.colorblind_var,
                            command=self.schedule_update)
        cb.pack(anchor=tk.W)
        
        # 热力图配色
        ttk.Label(frame, text="热力图/连续配色:").pack(anchor=tk.W)
        cmaps = ['RdBu_r', 'coolwarm', 'viridis', 'Blues', 'YlOrRd', 'Spectral']
        self.cmap_var = tk.StringVar(value='RdBu_r')
        self.cmap_combo = ttk.Combobox(frame, textvariable=self.cmap_var,
                                       values=cmaps, state='readonly')
        self.cmap_combo.pack(fill=tk.X, pady=2)
        self.cmap_combo.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
    
    def create_legend_section(self):
        """图例设置区域"""
        frame = ttk.LabelFrame(self.left_frame, text="📋 图例设置", padding=5)
        frame.pack(fill=tk.X, pady=5)
        
        # 图例位置
        ttk.Label(frame, text="位置:").pack(anchor=tk.W)
        positions = ['best', 'upper right', 'upper left', 'lower left',
                    'lower right', 'right', 'center left', 'center right',
                    'lower center', 'upper center', 'center']
        self.legend_loc_var = tk.StringVar(value='best')
        self.legend_loc_combo = ttk.Combobox(frame, textvariable=self.legend_loc_var,
                                             values=positions, state='readonly')
        self.legend_loc_combo.pack(fill=tk.X, pady=2)
        self.legend_loc_combo.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
        
        # 图例边框
        self.legend_frame_var = tk.BooleanVar(value=True)
        cb = ttk.Checkbutton(frame, text="显示图例边框", variable=self.legend_frame_var,
                            command=self.schedule_update)
        cb.pack(anchor=tk.W)
        
        # 图例字号
        size_frame = ttk.Frame(frame)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, text="字号:").pack(side=tk.LEFT)
        self.legend_fontsize_var = tk.IntVar(value=9)
        spin = ttk.Spinbox(size_frame, from_=6, to=14, textvariable=self.legend_fontsize_var, width=4)
        spin.pack(side=tk.LEFT, padx=2)
        spin.bind('<Return>', lambda e: self.schedule_update())
    
    def create_buttons_section(self):
        """按钮区域"""
        frame = ttk.Frame(self.left_frame)
        frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(frame, text="🎨 绘制图表", command=self.plot).pack(fill=tk.X, pady=2)
        ttk.Button(frame, text="🔄 刷新图表", command=self.update_plot).pack(fill=tk.X, pady=2)
        ttk.Button(frame, text="🗑️ 清除图表", command=self.clear_plot).pack(fill=tk.X, pady=2)
    
    def schedule_update(self):
        """安排延迟更新（防抖）"""
        if self._updating:
            return
        self._updating = True
        self.root.after(300, self._do_update)
    
    def _do_update(self):
        """执行更新"""
        self._updating = False
        if self.fig is not None:
            self.update_plot()
    
    def update_options(self):
        """更新图表选项"""
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        chart_type = self.chart_type.get()
        
        if self.df is None:
            ttk.Label(self.options_frame, text="请先加载数据").pack()
            return
        
        numeric_cols = list(self.df.select_dtypes(include=[np.number]).columns)
        all_cols = list(self.df.columns)
        
        if chart_type == "散点图":
            ttk.Label(self.options_frame, text="X轴:").pack(anchor=tk.W)
            self.scatter_x = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if numeric_cols: self.scatter_x.current(0)
            self.scatter_x.pack(fill=tk.X, pady=2)
            self.scatter_x.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="Y轴:").pack(anchor=tk.W)
            self.scatter_y = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if len(numeric_cols) > 1: self.scatter_y.current(1)
            self.scatter_y.pack(fill=tk.X, pady=2)
            self.scatter_y.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="颜色分组:").pack(anchor=tk.W)
            self.scatter_color = ttk.Combobox(self.options_frame, values=['无'] + all_cols, state='readonly')
            self.scatter_color.current(0)
            self.scatter_color.pack(fill=tk.X, pady=2)
            self.scatter_color.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
        
        elif chart_type == "折线图":
            ttk.Label(self.options_frame, text="X轴:").pack(anchor=tk.W)
            self.line_x = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if numeric_cols: self.line_x.current(0)
            self.line_x.pack(fill=tk.X, pady=2)
            self.line_x.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="Y轴 (Ctrl多选):").pack(anchor=tk.W)
            self.line_y = tk.Listbox(self.options_frame, selectmode=tk.MULTIPLE, height=4)
            for col in numeric_cols[1:]:
                self.line_y.insert(tk.END, col)
            self.line_y.pack(fill=tk.X, pady=2)
            self.line_y.bind('<<ListboxSelect>>', lambda e: self.schedule_update())
        
        elif chart_type == "柱状图":
            ttk.Label(self.options_frame, text="类别列:").pack(anchor=tk.W)
            self.bar_cat = ttk.Combobox(self.options_frame, values=all_cols, state='readonly')
            self.bar_cat.current(0)
            self.bar_cat.pack(fill=tk.X, pady=2)
            self.bar_cat.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="数值列 (Ctrl多选):").pack(anchor=tk.W)
            self.bar_val = tk.Listbox(self.options_frame, selectmode=tk.MULTIPLE, height=4)
            for col in numeric_cols:
                self.bar_val.insert(tk.END, col)
            self.bar_val.pack(fill=tk.X, pady=2)
            self.bar_val.bind('<<ListboxSelect>>', lambda e: self.schedule_update())
            
            self.bar_error = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.options_frame, text="显示误差线", variable=self.bar_error,
                           command=self.schedule_update).pack(anchor=tk.W)
        
        elif chart_type == "直方图":
            ttk.Label(self.options_frame, text="数据列 (Ctrl多选):").pack(anchor=tk.W)
            self.hist_cols = tk.Listbox(self.options_frame, selectmode=tk.MULTIPLE, height=4)
            for col in numeric_cols:
                self.hist_cols.insert(tk.END, col)
            self.hist_cols.pack(fill=tk.X, pady=2)
            self.hist_cols.bind('<<ListboxSelect>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="分箱数:").pack(anchor=tk.W)
            self.hist_bins = tk.IntVar(value=30)
            spin = ttk.Spinbox(self.options_frame, from_=5, to=100, textvariable=self.hist_bins)
            spin.pack(fill=tk.X, pady=2)
            spin.bind('<Return>', lambda e: self.schedule_update())
        
        elif chart_type == "饼图":
            ttk.Label(self.options_frame, text="标签列:").pack(anchor=tk.W)
            self.pie_label = ttk.Combobox(self.options_frame, values=all_cols, state='readonly')
            self.pie_label.current(0)
            self.pie_label.pack(fill=tk.X, pady=2)
            self.pie_label.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="数值列:").pack(anchor=tk.W)
            self.pie_value = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if numeric_cols: self.pie_value.current(0)
            self.pie_value.pack(fill=tk.X, pady=2)
            self.pie_value.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
        
        elif chart_type == "热力图":
            self.heatmap_corr = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.options_frame, text="相关性矩阵", variable=self.heatmap_corr,
                           command=self.schedule_update).pack(anchor=tk.W)
        
        elif chart_type in ["箱线图", "小提琴图"]:
            ttk.Label(self.options_frame, text="数值列:").pack(anchor=tk.W)
            self.box_value = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if numeric_cols: self.box_value.current(0)
            self.box_value.pack(fill=tk.X, pady=2)
            self.box_value.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="分组列:").pack(anchor=tk.W)
            self.box_group = ttk.Combobox(self.options_frame, values=['无'] + all_cols, state='readonly')
            self.box_group.current(0)
            self.box_group.pack(fill=tk.X, pady=2)
            self.box_group.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            if chart_type == "箱线图":
                self.show_points = tk.BooleanVar(value=False)
                ttk.Checkbutton(self.options_frame, text="显示数据点", variable=self.show_points,
                               command=self.schedule_update).pack(anchor=tk.W)
        
        elif chart_type == "误差线图":
            ttk.Label(self.options_frame, text="X轴:").pack(anchor=tk.W)
            self.err_x = ttk.Combobox(self.options_frame, values=all_cols, state='readonly')
            self.err_x.current(0)
            self.err_x.pack(fill=tk.X, pady=2)
            self.err_x.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="Y轴:").pack(anchor=tk.W)
            self.err_y = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if numeric_cols: self.err_y.current(0)
            self.err_y.pack(fill=tk.X, pady=2)
            self.err_y.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="误差列:").pack(anchor=tk.W)
            self.err_err = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if len(numeric_cols) > 1: self.err_err.current(1)
            self.err_err.pack(fill=tk.X, pady=2)
            self.err_err.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
        
        elif chart_type == "堆叠面积图":
            ttk.Label(self.options_frame, text="X轴:").pack(anchor=tk.W)
            self.stack_x = ttk.Combobox(self.options_frame, values=all_cols, state='readonly')
            self.stack_x.current(0)
            self.stack_x.pack(fill=tk.X, pady=2)
            self.stack_x.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="Y轴 (Ctrl多选):").pack(anchor=tk.W)
            self.stack_y = tk.Listbox(self.options_frame, selectmode=tk.MULTIPLE, height=4)
            for col in numeric_cols:
                self.stack_y.insert(tk.END, col)
            self.stack_y.pack(fill=tk.X, pady=2)
            self.stack_y.bind('<<ListboxSelect>>', lambda e: self.schedule_update())
        
        elif chart_type == "双Y轴图":
            ttk.Label(self.options_frame, text="X轴:").pack(anchor=tk.W)
            self.dual_x = ttk.Combobox(self.options_frame, values=all_cols, state='readonly')
            self.dual_x.current(0)
            self.dual_x.pack(fill=tk.X, pady=2)
            self.dual_x.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="左Y轴:").pack(anchor=tk.W)
            self.dual_y1 = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if numeric_cols: self.dual_y1.current(0)
            self.dual_y1.pack(fill=tk.X, pady=2)
            self.dual_y1.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
            
            ttk.Label(self.options_frame, text="右Y轴:").pack(anchor=tk.W)
            self.dual_y2 = ttk.Combobox(self.options_frame, values=numeric_cols, state='readonly')
            if len(numeric_cols) > 1: self.dual_y2.current(1)
            self.dual_y2.pack(fill=tk.X, pady=2)
            self.dual_y2.bind('<<ComboboxSelected>>', lambda e: self.schedule_update())
    
    def load_csv(self):
        """加载CSV文件"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")])
        if filepath:
            try:
                self.df = pd.read_csv(filepath)
                self.info_label.config(text=f"已加载: {os.path.basename(filepath)}\n{self.df.shape[0]}行 × {self.df.shape[1]}列")
                self.update_options()
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {e}")
    
    def load_excel(self):
        """加载Excel文件"""
        filepath = filedialog.askopenfilename(filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")])
        if filepath:
            try:
                self.df = pd.read_excel(filepath)
                self.info_label.config(text=f"已加载: {os.path.basename(filepath)}\n{self.df.shape[0]}行 × {self.df.shape[1]}列")
                self.update_options()
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {e}")
    
    def load_tsv(self):
        """加载TSV文件"""
        filepath = filedialog.askopenfilename(filetypes=[("TSV文件", "*.tsv"), ("所有文件", "*.*")])
        if filepath:
            try:
                self.df = pd.read_csv(filepath, sep='\t')
                self.info_label.config(text=f"已加载: {os.path.basename(filepath)}\n{self.df.shape[0]}行 × {self.df.shape[1]}列")
                self.update_options()
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {e}")
    
    def load_example(self, example_type):
        """加载示例数据"""
        np.random.seed(42)
        
        if example_type == 'scatter':
            self.df = pd.DataFrame({
                'X': np.random.randn(100),
                'Y': np.random.randn(100) * 2 + 1,
                'Group': np.random.choice(['A', 'B', 'C'], 100)
            })
        elif example_type == 'sincos':
            x = np.linspace(0, 10, 50)
            self.df = pd.DataFrame({'X': x, 'sin_X': np.sin(x), 'cos_X': np.cos(x)})
        elif example_type == 'group':
            self.df = pd.DataFrame({
                'Group': np.repeat(['A', 'B', 'C', 'D'], 30),
                'Value': np.concatenate([
                    np.random.normal(10, 2, 30), np.random.normal(12, 2.5, 30),
                    np.random.normal(8, 1.5, 30), np.random.normal(15, 3, 30)
                ])
            })
        elif example_type == 'corr':
            data = np.random.rand(5, 5)
            data = (data + data.T) / 2
            np.fill_diagonal(data, 1)
            self.df = pd.DataFrame(data, columns=['V1', 'V2', 'V3', 'V4', 'V5'],
                                  index=['V1', 'V2', 'V3', 'V4', 'V5'])
        elif example_type == 'timeseries':
            dates = pd.date_range('2024-01-01', periods=100)
            self.df = pd.DataFrame({
                'Date': dates,
                'Value_A': np.cumsum(np.random.randn(100)) + 100,
                'Value_B': np.cumsum(np.random.randn(100)) + 50
            })
        elif example_type == 'errorbar':
            self.df = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D', 'E'],
                'Mean': [23, 45, 56, 78, 32],
                'Std': [3, 5, 4, 6, 3]
            })
        else:
            messagebox.showwarning("提示", f"未知的示例数据类型: {example_type}")
            return
        
        if self.df is not None:
            self.info_label.config(text=f"已加载示例数据\n{self.df.shape[0]}行 × {self.df.shape[1]}列")
            self.update_options()
    
    def preview_data(self):
        """预览数据"""
        if self.df is None:
            messagebox.showwarning("提示", "请先加载数据")
            return
        
        preview_window = tk.Toplevel(self.root)
        preview_window.title("数据预览")
        preview_window.geometry("800x500")
        
        text = scrolledtext.ScrolledText(preview_window, wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True)
        
        text.insert(tk.END, f"数据形状: {self.df.shape[0]} 行 × {self.df.shape[1]} 列\n")
        text.insert(tk.END, "=" * 50 + "\n\n")
        text.insert(tk.END, self.df.head(20).to_string())
        text.insert(tk.END, "\n\n" + "=" * 50 + "\n")
        text.insert(tk.END, "\n描述性统计:\n")
        text.insert(tk.END, self.df.describe().to_string())
    
    def plot(self):
        """绘制图表"""
        if self.df is None:
            messagebox.showwarning("提示", "请先加载数据")
            return
        
        self.apply_style()
        self._create_figure()
    
    def update_plot(self):
        """更新图表"""
        if self.df is None or self.fig is None:
            return
        
        self.apply_style()
        self._create_figure()
    
    def _create_figure(self):
        """创建图表"""
        if self.df is None:
            return
        
        # 清除旧图表
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        for widget in self.toolbar_frame.winfo_children():
            widget.destroy()
        
        figsize = (self.width_var.get(), self.height_var.get())
        self.fig = Figure(figsize=figsize, dpi=100)
        ax = self.fig.add_subplot(111)
        
        chart_type = self.chart_type.get()
        
        try:
            if chart_type == "散点图":
                self._plot_scatter(ax)
            elif chart_type == "折线图":
                self._plot_line(ax)
            elif chart_type == "柱状图":
                self._plot_bar(ax)
            elif chart_type == "直方图":
                self._plot_histogram(ax)
            elif chart_type == "饼图":
                self._plot_pie(ax)
            elif chart_type == "热力图":
                self._plot_heatmap(ax)
            elif chart_type == "箱线图":
                self._plot_box(ax)
            elif chart_type == "小提琴图":
                self._plot_violin(ax)
            elif chart_type == "误差线图":
                self._plot_errorbar(ax)
            elif chart_type == "堆叠面积图":
                self._plot_stack(ax)
            elif chart_type == "双Y轴图":
                self._plot_dual_axis(ax)
            
            ax.set_title(self.title_entry.get())
            self.fig.tight_layout()
            
            # 显示图表
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # 工具栏
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
            self.toolbar.update()
            
        except Exception as e:
            messagebox.showerror("错误", f"绘图失败: {e}")
    
    def _get_legend_kwargs(self):
        """获取图例参数"""
        return {
            'loc': self.legend_loc_var.get(),
            'frameon': self.legend_frame_var.get(),
            'fontsize': self.legend_fontsize_var.get()
        }
    
    def _plot_scatter(self, ax):
        x_col = self.scatter_x.get()
        y_col = self.scatter_y.get()
        color_col = self.scatter_color.get()
        colors = self.get_colors()
        
        xlabel = self.xlabel_entry.get() or x_col
        ylabel = self.ylabel_entry.get() or y_col
        
        if color_col == '无':
            ax.scatter(self.df[x_col], self.df[y_col], s=50, alpha=0.7,
                      edgecolors='white', linewidth=0.5, color=colors[0])
        else:
            groups = self.df[color_col].unique()
            for i, group in enumerate(groups):
                mask = self.df[color_col] == group
                ax.scatter(self.df.loc[mask, x_col], self.df.loc[mask, y_col],
                          label=str(group), s=50, alpha=0.7,
                          edgecolors='white', color=colors[i % len(colors)])
            ax.legend(**self._get_legend_kwargs())
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    def _plot_line(self, ax):
        x_col = self.line_x.get()
        selected = self.line_y.curselection()
        y_cols = [self.line_y.get(i) for i in selected]
        colors = self.get_colors()
        markers = ['o', 's', '^', 'D', 'v', '<', '>']
        
        xlabel = self.xlabel_entry.get() or x_col
        ylabel = self.ylabel_entry.get() or 'Value'
        
        for i, y_col in enumerate(y_cols):
            ax.plot(self.df[x_col], self.df[y_col], label=y_col,
                   color=colors[i % len(colors)],
                   marker=markers[i % len(markers)], markersize=5)
        
        if y_cols:
            ax.legend(**self._get_legend_kwargs())
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    def _plot_bar(self, ax):
        cat_col = self.bar_cat.get()
        selected = self.bar_val.curselection()
        val_cols = [self.bar_val.get(i) for i in selected]
        colors = self.get_colors()
        show_error = self.bar_error.get()
        
        xlabel = self.xlabel_entry.get() or cat_col
        ylabel = self.ylabel_entry.get() or 'Value'
        
        if val_cols:
            if show_error:
                bar_data = self.df.groupby(cat_col)[val_cols].agg(['mean', 'std']).reset_index()
                bar_data.columns = [cat_col] + [f'{c}_{s}' for c in val_cols for s in ['mean', 'std']]
            else:
                bar_data = self.df.groupby(cat_col)[val_cols].mean().reset_index()
            
            x = np.arange(len(bar_data))
            width = 0.8 / len(val_cols)
            
            for i, col in enumerate(val_cols):
                offset = (i - len(val_cols)/2 + 0.5) * width
                if show_error:
                    y = bar_data[f'{col}_mean']
                    yerr = bar_data[f'{col}_std']
                else:
                    y = bar_data[col]
                    yerr = None
                
                ax.bar(x + offset, y, width, label=col,
                      color=colors[i % len(colors)], yerr=yerr, capsize=3)
            
            ax.set_xticks(x)
            ax.set_xticklabels(bar_data[cat_col])
            ax.legend(**self._get_legend_kwargs())
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    def _plot_histogram(self, ax):
        selected = self.hist_cols.curselection()
        cols = [self.hist_cols.get(i) for i in selected]
        bins = self.hist_bins.get()
        colors = self.get_colors()
        
        xlabel = self.xlabel_entry.get() or 'Value'
        ylabel = self.ylabel_entry.get() or 'Frequency'
        
        for i, col in enumerate(cols):
            ax.hist(self.df[col], bins=bins, alpha=0.7, label=col,
                   color=colors[i % len(colors)], edgecolor='white')
        
        if cols:
            ax.legend(**self._get_legend_kwargs())
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    def _plot_pie(self, ax):
        label_col = self.pie_label.get()
        value_col = self.pie_value.get()
        colors = self.get_colors(len(self.df))
        
        ax.pie(self.df[value_col], labels=self.df[label_col], autopct='%1.1f%%',
               colors=colors, startangle=90,
               wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
    
    def _plot_heatmap(self, ax):
        numeric_df = self.df.select_dtypes(include=[np.number])
        cmap = self.cmap_var.get()
        
        if self.heatmap_corr.get():
            plot_data = numeric_df.corr()
            center = 0
        else:
            plot_data = numeric_df
            center = None
        
        sns.heatmap(plot_data, ax=ax, cmap=cmap, annot=True, fmt='.2f',
                    linewidths=0.5, center=center)
    
    def _plot_box(self, ax):
        value_col = self.box_value.get()
        group_col = self.box_group.get()
        colors = self.get_colors()
        show_points = self.show_points.get() if hasattr(self, 'show_points') else False
        
        if group_col != '无':
            groups = self.df[group_col].unique()
            data_list = [self.df[self.df[group_col] == g][value_col].values for g in groups]
            bp = ax.boxplot(data_list, labels=groups, patch_artist=True)
            for patch, color in zip(bp['boxes'], colors[:len(groups)]):
                patch.set_facecolor(color)
            if show_points:
                for i, g in enumerate(groups):
                    y = self.df[self.df[group_col] == g][value_col].values
                    x = np.random.normal(i+1, 0.04, len(y))
                    ax.scatter(x, y, alpha=0.4, s=10, color='black')
        else:
            bp = ax.boxplot([self.df[value_col]], labels=[value_col], patch_artist=True)
            bp['boxes'][0].set_facecolor(colors[0])
        
        ylabel = self.ylabel_entry.get() or value_col
        ax.set_ylabel(ylabel)
    
    def _plot_violin(self, ax):
        value_col = self.box_value.get()
        group_col = self.box_group.get()
        colors = self.get_colors()
        
        groups = self.df[group_col].unique()
        data_list = [self.df[self.df[group_col] == g][value_col].values for g in groups]
        
        parts = ax.violinplot(data_list, showmeans=True, showmedians=True)
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i % len(colors)])
            pc.set_alpha(0.7)
        
        ax.set_xticks(range(1, len(groups) + 1))
        ax.set_xticklabels(groups)
        
        xlabel = self.xlabel_entry.get() or group_col
        ylabel = self.ylabel_entry.get() or value_col
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    def _plot_errorbar(self, ax):
        x_col = self.err_x.get()
        y_col = self.err_y.get()
        err_col = self.err_err.get()
        colors = self.get_colors()
        
        xlabel = self.xlabel_entry.get() or x_col
        ylabel = self.ylabel_entry.get() or y_col
        
        ax.errorbar(self.df[x_col], self.df[y_col], yerr=self.df[err_col],
                   fmt='o-', capsize=5, color=colors[0], linewidth=1.5)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    def _plot_stack(self, ax):
        x_col = self.stack_x.get()
        selected = self.stack_y.curselection()
        y_cols = [self.stack_y.get(i) for i in selected]
        colors = self.get_colors()
        
        xlabel = self.xlabel_entry.get() or x_col
        ylabel = self.ylabel_entry.get() or 'Value'
        
        if y_cols:
            ax.stackplot(self.df[x_col], *[self.df[c] for c in y_cols],
                        labels=y_cols, colors=colors[:len(y_cols)], alpha=0.8)
            ax.legend(**self._get_legend_kwargs())
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    def _plot_dual_axis(self, ax):
        x_col = self.dual_x.get()
        y1_col = self.dual_y1.get()
        y2_col = self.dual_y2.get()
        colors = self.get_colors()
        
        xlabel = self.xlabel_entry.get() or x_col
        
        ax.plot(self.df[x_col], self.df[y1_col], color=colors[0], marker='o', label=y1_col)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(y1_col, color=colors[0])
        ax.tick_params(axis='y', labelcolor=colors[0])
        
        ax2 = ax.twinx()
        ax2.plot(self.df[x_col], self.df[y2_col], color=colors[1], marker='s', label=y2_col)
        ax2.set_ylabel(y2_col, color=colors[1])
        ax2.tick_params(axis='y', labelcolor=colors[1])
        
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, **self._get_legend_kwargs())
    
    def clear_plot(self):
        """清除图表"""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        for widget in self.toolbar_frame.winfo_children():
            widget.destroy()
        self.fig = None
        self.canvas = None
    
    def save_figure(self):
        """保存图表"""
        if self.fig is None:
            messagebox.showwarning("提示", "请先绘制图表")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"),
                      ("SVG", "*.svg"), ("EPS", "*.eps"), ("所有文件", "*.*")]
        )
        
        if filepath:
            try:
                self.fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("成功", f"图表已保存到:\n{filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def save_template(self):
        """保存模板"""
        config = {
            'title': self.title_entry.get(),
            'xlabel': self.xlabel_entry.get(),
            'ylabel': self.ylabel_entry.get(),
            'tick_inward': self.tick_inward.get(),
            'width': self.width_var.get(),
            'height': self.height_var.get(),
            'palette': self.palette_var.get(),
            'colorblind': self.colorblind_var.get(),
            'cmap': self.cmap_var.get(),
            'legend_loc': self.legend_loc_var.get(),
            'legend_frame': self.legend_frame_var.get(),
            'legend_fontsize': self.legend_fontsize_var.get(),
            'chart_type': self.chart_type.get(),
        }
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("所有文件", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", f"模板已保存到:\n{filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def load_template(self):
        """加载模板"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("所有文件", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, config.get('title', ''))
                
                self.xlabel_entry.delete(0, tk.END)
                self.xlabel_entry.insert(0, config.get('xlabel', ''))
                
                self.ylabel_entry.delete(0, tk.END)
                self.ylabel_entry.insert(0, config.get('ylabel', ''))
                
                self.tick_inward.set(config.get('tick_inward', True))
                self.width_var.set(config.get('width', 8))
                self.height_var.set(config.get('height', 6))
                self.palette_var.set(config.get('palette', 'Nature'))
                self.colorblind_var.set(config.get('colorblind', False))
                self.cmap_var.set(config.get('cmap', 'RdBu_r'))
                self.legend_loc_var.set(config.get('legend_loc', 'best'))
                self.legend_frame_var.set(config.get('legend_frame', True))
                self.legend_fontsize_var.set(config.get('legend_fontsize', 9))
                self.chart_type.set(config.get('chart_type', '散点图'))
                
                self.update_options()
                messagebox.showinfo("成功", "模板已加载")
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {e}")
    
    def show_help(self):
        """显示帮助"""
        messagebox.showinfo("使用说明",
            "SciPlot - 科研绘图工具\n\n"
            "1. 数据导入: 文件菜单或示例数据\n"
            "2. 选择图表类型\n"
            "3. 设置图表选项\n"
            "4. 调整配色和图例\n"
            "5. 点击绘制或等待自动更新\n"
            "6. 保存图片或模板\n\n"
            "快捷操作:\n"
            "- 参数变更自动更新图表\n"
            "- 支持保存/加载配置模板\n"
            "- 鼠标滚轮缩放图表")
    
    def show_about(self):
        """显示关于"""
        messagebox.showinfo("关于",
            "SciPlot - 科研绘图工具\n\n"
            "版本: 2.0 (增强版)\n\n"
            "功能:\n"
            "- 11种图表类型\n"
            "- 50+配色方案\n"
            "- 实时预览\n"
            "- 中文字体支持\n"
            "- 模板系统\n"
            "- 双Y轴支持")


def main():
    root = tk.Tk()
    app = SciPlotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()