"""
sci_plot.py - 科研绘图工具箱 (增强版)
=====================================
整合20+种科研常用图表类型，支持中文字体、ColorBrewer配色、模板系统

使用方法:
    from sci_plot import SciPlot as sp
    
    # 基础图表
    sp.scatter(x, y, xlabel='X', ylabel='Y')
    sp.line(x, [y1, y2], labels=['A', 'B'])
    sp.bar(categories, values)
    
    # 配置
    sp.config.palette = 'Set1'  # 切换配色
    sp.config.save('output', ['png', 'pdf'])
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Optional, Union


# ============================================================
# ColorBrewer 配色方案
# ============================================================

class ColorPalettes:
    """配色方案集合"""
    
    # Nature默认配色
    NATURE = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F',
              '#8491B4', '#91D1C2', '#DC0000', '#7E6148', '#B09C85']
    
    # ColorBrewer 定性配色
    QUALITATIVE = {
        'Set1': ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
                 '#ffff33', '#a65628', '#f781bf', '#999999'],
        'Set2': ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854',
                 '#ffd92f', '#e5c494', '#b3b3b3'],
        'Set3': ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
                 '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd',
                 '#ccebc5', '#ffed6f'],
        'Paired': ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
                   '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
                   '#ffff99', '#b15928'],
        'Dark2': ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e',
                  '#e6ab02', '#a6761d', '#666666'],
        'Accent': ['#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0',
                   '#f0027f', '#bf5b17', '#666666'],
    }
    
    # ColorBrewer 顺序配色
    SEQUENTIAL = {
        'Blues': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6',
                  '#4292c6', '#2171b5', '#08519c', '#08306b'],
        'Greens': ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476',
                   '#41ab5d', '#238b45', '#006d2c', '#00441b'],
        'Reds': ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a',
                 '#ef3b2c', '#cb181d', '#a50f15', '#67000d'],
        'YlOrRd': ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c',
                   '#fc4e2a', '#e31a1c', '#bd0026', '#800026'],
        'YlGnBu': ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4',
                   '#1d91c0', '#225ea8', '#253494', '#081d58'],
        'PuRd': ['#f7f4f9', '#e7e1ef', '#d4b9da', '#c994c7', '#df65b0',
                 '#e7298a', '#ce1256', '#980043', '#67001f'],
    }
    
    # ColorBrewer 发散配色
    DIVERGING = {
        'RdBu': ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7',
                 '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac', '#053061'],
        'RdYlGn': ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee08b',
                   '#ffffbf', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837'],
        'Spectral': ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b',
                     '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2'],
        'PiYG': ['#8e0152', '#c51b7d', '#de77ae', '#f1b6da', '#fde0ef',
                 '#f7f7f7', '#e6f5d0', '#b8e186', '#7fbc41', '#4d9221', '#276419'],
    }
    
    # 色盲友好配色
    COLORBLIND_SAFE = ['#0072B2', '#E69F00', '#009E73', '#CC79A7',
                       '#56B4E9', '#D55E00', '#F0E442', '#000000']
    
    @classmethod
    def get_palette(cls, name: str, n_colors: int = None) -> List[str]:
        """获取指定配色方案"""
        if name == 'Nature' or name == 'default':
            colors = cls.NATURE
        elif name == 'colorblind':
            colors = cls.COLORBLIND_SAFE
        elif name in cls.QUALITATIVE:
            colors = cls.QUALITATIVE[name]
        elif name in cls.SEQUENTIAL:
            colors = cls.SEQUENTIAL[name]
        elif name in cls.DIVERGING:
            colors = cls.DIVERGING[name]
        elif name in ['viridis', 'plasma', 'inferno', 'magma', 'cividis']:
            cmap = plt.get_cmap(name)
            n = n_colors or 8
            colors = [plt.matplotlib.colors.to_hex(cmap(i/(n-1))) for i in range(n)]
            return colors
        else:
            colors = cls.NATURE
        
        if n_colors:
            while len(colors) < n_colors:
                colors = colors + colors
            colors = colors[:n_colors]
        
        return colors
    
    @classmethod
    def list_palettes(cls) -> Dict[str, List[str]]:
        """列出所有可用的配色方案"""
        return {
            'Nature': ['Nature'],
            '定性配色': list(cls.QUALITATIVE.keys()),
            '顺序配色': list(cls.SEQUENTIAL.keys()),
            '发散配色': list(cls.DIVERGING.keys()),
            '感知均匀': ['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
            '特殊': ['colorblind'],
        }
    
    @classmethod
    def preview_palette(cls, name: str, ax=None):
        """预览配色方案"""
        colors = cls.get_palette(name, 8)
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 0.8))
        
        for i, color in enumerate(colors):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='white'))
        
        ax.set_xlim(0, len(colors))
        ax.set_ylim(0, 1)
        ax.set_title(f'{name}', loc='left', fontsize=10, fontweight='bold')
        ax.axis('off')
        return ax


# ============================================================
# 绘图配置类
# ============================================================

class PlotConfig:
    """绘图配置类"""
    
    # 可用字体列表
    AVAILABLE_FONTS = ['Arial', 'Times New Roman', 'Microsoft YaHei', 
                       'SimHei', 'SimSun', 'Calibri', 'Cambria',
                       'Consolas', 'Courier New', 'Georgia']
    
    def __init__(self):
        self.font = 'Arial'
        self.fontsize = 10
        self.fontweight = 'normal'  # 'normal', 'bold'
        self.dpi = 300
        self.figsize = (8, 6)
        self.tick_inward = True
        self.palette = 'Nature'
        self.cmap_sequential = 'Blues'
        self.cmap_diverging = 'RdBu_r'
        self.legend_loc = 'best'
        self.legend_frame = True
        self.legend_fontsize = 9
        # 自定义颜色列表
        self.custom_colors = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F',
                              '#8491B4', '#91D1C2', '#DC0000', '#7E6148', '#B09C85']
        self._chinese_font = None
        self._setup_chinese_font()
    
    def _setup_chinese_font(self):
        """自动检测并设置中文字体"""
        chinese_fonts = [
            'Microsoft YaHei', 'SimHei', 'SimSun',
            'Noto Sans CJK SC', 'WenQuanYi Micro Hei',
            'PingFang SC', 'Heiti SC', 'Arial Unicode MS',
        ]
        available = {f.name for f in fm.fontManager.ttflist}
        for font in chinese_fonts:
            if font in available:
                self._chinese_font = font
                break
    
    @staticmethod
    def get_available_fonts():
        """获取系统可用字体列表"""
        available = {f.name for f in fm.fontManager.ttflist}
        # 常用字体
        common_fonts = ['Arial', 'Times New Roman', 'Microsoft YaHei', 
                        'SimHei', 'SimSun', 'Calibri', 'Cambria',
                        'Consolas', 'Courier New', 'Georgia', 'Verdana',
                        'Tahoma', 'Trebuchet MS', 'Lucida Console']
        result = []
        for font in common_fonts:
            if font in available:
                result.append(font)
        return result
    
    def apply(self):
        """应用配置到matplotlib"""
        # 构建字体列表
        fonts = [self.font]
        if self.font != self._chinese_font and self._chinese_font:
            fonts.append(self._chinese_font)
        fonts.extend(['Helvetica', 'DejaVu Sans'])
        
        # 去重
        seen = set()
        unique_fonts = []
        for f in fonts:
            if f and f not in seen:
                seen.add(f)
                unique_fonts.append(f)
        
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': unique_fonts,
            'font.size': self.fontsize,
            'font.weight': self.fontweight,
            'axes.unicode_minus': False,
            'figure.figsize': self.figsize,
            'figure.dpi': self.dpi,
            'savefig.dpi': self.dpi,
            'savefig.bbox': 'tight',
            'axes.linewidth': 1.0,
            'axes.spines.top': True,
            'axes.spines.right': True,
            'axes.labelweight': self.fontweight,
            'axes.titleweight': self.fontweight,
            'lines.linewidth': 1.5,
            'lines.markersize': 6,
            'legend.frameon': self.legend_frame,
            'legend.framealpha': 1.0,
            'legend.edgecolor': 'black',
            'legend.fontsize': self.legend_fontsize,
            'legend.title_fontsize': self.legend_fontsize + 1,
        })
        
        if self.tick_inward:
            plt.rcParams.update({
                'xtick.direction': 'in', 'ytick.direction': 'in',
                'xtick.top': True, 'ytick.right': True,
                'xtick.major.size': 4, 'ytick.major.size': 4,
            })
        else:
            plt.rcParams.update({
                'xtick.direction': 'out', 'ytick.direction': 'out',
                'xtick.top': False, 'ytick.right': False,
            })
    
    def get_colors(self, n: int = None) -> List[str]:
        """获取当前配色方案的颜色列表"""
        return ColorPalettes.get_palette(self.palette, n)
    
    def save(self, filename: str, formats: List[str] = None):
        """保存当前图形"""
        if formats is None:
            formats = ['png', 'pdf']
        for fmt in formats:
            plt.savefig(f"{filename}.{fmt}", dpi=self.dpi,
                       bbox_inches='tight', facecolor='white')
            print(f"Saved: {filename}.{fmt}")
    
    def to_dict(self) -> dict:
        """导出配置为字典"""
        return {
            'font': self.font, 'fontsize': self.fontsize,
            'dpi': self.dpi, 'figsize': list(self.figsize),
            'tick_inward': self.tick_inward, 'palette': self.palette,
            'cmap_sequential': self.cmap_sequential,
            'cmap_diverging': self.cmap_diverging,
            'legend_loc': self.legend_loc, 'legend_frame': self.legend_frame,
            'legend_fontsize': self.legend_fontsize,
        }
    
    def from_dict(self, config: dict):
        """从字典加载配置"""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.apply()
    
    def save_template(self, filepath: str):
        """保存配置为模板文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"Template saved: {filepath}")
    
    def load_template(self, filepath: str):
        """从模板文件加载配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.from_dict(config)
        print(f"Template loaded: {filepath}")


# ============================================================
# 统计函数
# ============================================================

class Statistics:
    """统计计算工具"""
    
    @staticmethod
    def compute_errorbar(data: Union[pd.DataFrame, np.ndarray],
                         group_col: str = None, value_col: str = None,
                         method: str = 'se') -> pd.DataFrame:
        """计算误差线数据"""
        if isinstance(data, pd.DataFrame) and group_col and value_col:
            stats = data.groupby(group_col)[value_col].agg(['mean', 'std', 'count'])
            if method == 'se':
                stats['error'] = stats['std'] / np.sqrt(stats['count'])
            elif method == 'std':
                stats['error'] = stats['std']
            elif method == 'ci95':
                stats['error'] = 1.96 * stats['std'] / np.sqrt(stats['count'])
            return stats.reset_index()
        else:
            arr = np.array(data)
            return pd.DataFrame({
                'mean': [np.mean(arr)], 'std': [np.std(arr)],
                'count': [len(arr)],
                'error': [np.std(arr) / np.sqrt(len(arr))] if method == 'se' else [np.std(arr)]
            })
    
    @staticmethod
    def linear_fit(x, y):
        """线性拟合"""
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        r_squared = 1 - np.sum((y - p(x))**2) / np.sum((y - np.mean(y))**2)
        return {
            'slope': z[0], 'intercept': z[1],
            'r_squared': r_squared,
            'equation': f'y = {z[0]:.4f}x + {z[1]:.4f}',
            'predict': p
        }


# ============================================================
# 科研绘图主类
# ============================================================

class SciPlot:
    """科研绘图主类"""
    
    config = PlotConfig()
    config.apply()
    COLORS = ColorPalettes.NATURE
    Palettes = ColorPalettes
    Stats = Statistics
    
    @classmethod
    def _setup_ax(cls, ax, title='', xlabel='', ylabel=''):
        if title: ax.set_title(title)
        if xlabel: ax.set_xlabel(xlabel)
        if ylabel: ax.set_ylabel(ylabel)
    
    @classmethod
    def _get_colors(cls, n: int = None) -> List[str]:
        return cls.config.get_colors(n)
    
    # ==================== 基础图表 ====================
    
    @classmethod
    def scatter(cls, x, y, c=None, s=50, alpha=0.7,
                xlabel='', ylabel='', title='', 
                cmap=None, colorbar=False,
                log_x=False, log_y=False, filename=None):
        """散点图"""
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        colors = cls._get_colors()
        
        if c is None:
            sc = ax.scatter(x, y, s=s, alpha=alpha,
                           edgecolors='white', linewidth=0.5, color=colors[0])
        else:
            sc = ax.scatter(x, y, c=c, s=s, alpha=alpha, 
                           cmap=cmap or cls.config.cmap_sequential,
                           edgecolors='white', linewidth=0.5)
        
        if colorbar or c is not None:
            plt.colorbar(sc, ax=ax)
        if log_x: ax.set_xscale('log')
        if log_y: ax.set_yscale('log')
        
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def line(cls, x, y_list, labels=None, colors=None, markers=None,
             xlabel='', ylabel='', title='', filename=None):
        """折线图"""
        if not isinstance(y_list[0], (list, np.ndarray, pd.Series)):
            y_list = [y_list]
        n = len(y_list)
        if colors is None: colors = cls._get_colors(n)
        if markers is None: markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p']
        
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        for i, y in enumerate(y_list):
            lbl = labels[i] if labels and i < len(labels) else None
            ax.plot(x, y, label=lbl, color=colors[i % len(colors)],
                   marker=markers[i % len(markers)], markersize=6)
        if labels: ax.legend(loc=cls.config.legend_loc)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def bar(cls, categories, values, labels=None, horizontal=False,
            xlabel='', ylabel='', title='', errorbars=None, filename=None):
        """柱状图"""
        if not isinstance(values[0], (list, np.ndarray, pd.Series)):
            values = [values]
        n_groups, n_bars = len(categories), len(values)
        width = 0.8 / n_bars
        idx = np.arange(n_groups)
        colors = cls._get_colors(n_bars)
        
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        for i, v in enumerate(values):
            lbl = labels[i] if labels and i < len(labels) else None
            offset = (i - n_bars/2 + 0.5) * width
            err = errorbars[i] if errorbars and i < len(errorbars) else None
            
            if horizontal:
                ax.barh(idx + offset, v, width, label=lbl,
                       color=colors[i % len(colors)], xerr=err, capsize=3)
            else:
                ax.bar(idx + offset, v, width, label=lbl,
                      color=colors[i % len(colors)], yerr=err, capsize=3)
        
        if horizontal:
            ax.set_yticks(idx); ax.set_yticklabels(categories)
        else:
            ax.set_xticks(idx); ax.set_xticklabels(categories)
        
        if labels: ax.legend(loc=cls.config.legend_loc)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def histogram(cls, data, bins=30, density=False, labels=None,
                  xlabel='Value', ylabel='Frequency', title='', filename=None):
        """直方图"""
        if isinstance(data, np.ndarray) and data.ndim == 1:
            data = [data]
        
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        colors = cls._get_colors(len(data))
        
        for i, d in enumerate(data):
            lbl = labels[i] if labels and i < len(labels) else None
            ax.hist(d, bins=bins, alpha=0.7, label=lbl, density=density,
                   color=colors[i % len(colors)], edgecolor='white')
        if labels: ax.legend(loc=cls.config.legend_loc)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def pie(cls, sizes, labels, explode=None, title='', filename=None):
        """饼图"""
        fig, ax = plt.subplots(figsize=(6, 6))
        if explode is None: explode = [0] * len(sizes)
        colors = cls._get_colors(len(sizes))
        
        ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
               colors=colors, startangle=90,
               wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
        ax.set_title(title)
        ax.axis('equal')
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def ring(cls, sizes, labels, title='', filename=None):
        """环形图"""
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = cls._get_colors(len(sizes))
        
        ax.pie(sizes, labels=labels, colors=colors,
               wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
        circle = plt.Circle((0, 0), 0.7, fc='white')
        ax.add_artist(circle)
        ax.set_title(title)
        ax.axis('equal')
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    # ==================== 高级图表 ====================
    
    @classmethod
    def heatmap(cls, data, cmap=None, annot=True, center=None,
                xlabel='', ylabel='', title='', filename=None):
        """热力图"""
        import seaborn as sns
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        if cmap is None: cmap = cls.config.cmap_diverging
        
        sns.heatmap(data, ax=ax, cmap=cmap, annot=annot, fmt='.2f',
                    linewidths=0.5, center=center)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def box(cls, data, show_points=False, xlabel='Group', ylabel='Value',
            title='', filename=None):
        """箱线图"""
        import seaborn as sns
        df = pd.DataFrame(data).melt(var_name='Group', value_name='Value')
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        colors = cls._get_colors(len(data))
        
        sns.boxplot(data=df, x='Group', y='Value', ax=ax,
                   palette=colors, linewidth=1.0)
        if show_points:
            sns.stripplot(data=df, x='Group', y='Value', ax=ax,
                         color='black', size=3, alpha=0.5)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def violin(cls, data, inner='box', xlabel='Group', ylabel='Value',
               title='', filename=None):
        """小提琴图"""
        import seaborn as sns
        df = pd.DataFrame(data).melt(var_name='Group', value_name='Value')
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        colors = cls._get_colors(len(data))
        
        sns.violinplot(data=df, x='Group', y='Value', ax=ax,
                      palette=colors, inner=inner)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def errorbar(cls, x, y_list, yerr_list, labels=None,
                 xlabel='', ylabel='', title='', filename=None):
        """误差线图"""
        if not isinstance(y_list[0], (list, np.ndarray, pd.Series)):
            y_list, yerr_list = [y_list], [yerr_list]
        markers = ['o', 's', '^', 'D', 'v', '<', '>']
        colors = cls._get_colors(len(y_list))
        
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        for i, (y, err) in enumerate(zip(y_list, yerr_list)):
            lbl = labels[i] if labels and i < len(labels) else None
            ax.errorbar(x, y, yerr=err, label=lbl, capsize=3,
                       color=colors[i % len(colors)],
                       marker=markers[i % len(markers)])
        if labels: ax.legend(loc=cls.config.legend_loc)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def stack(cls, x, y_list, labels=None, xlabel='', ylabel='',
              title='', filename=None):
        """堆叠面积图"""
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        if labels is None: labels = [f'G{i+1}' for i in range(len(y_list))]
        colors = cls._get_colors(len(y_list))
        
        ax.stackplot(x, *y_list, labels=labels, colors=colors, alpha=0.8)
        ax.legend(loc=cls.config.legend_loc)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def multiline_fill(cls, x, means_list, mins_list, maxs_list, labels=None,
                       xlabel='', ylabel='', title='', filename=None):
        """带填充的多线图"""
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        colors = cls._get_colors(len(means_list))
        
        for i, (mean, mn, mx) in enumerate(zip(means_list, mins_list, maxs_list)):
            lbl = labels[i] if labels and i < len(labels) else None
            c = colors[i % len(colors)]
            ax.plot(x, mean, label=lbl, color=c, marker='o', markersize=6)
            ax.fill_between(x, mn, mx, color=c, alpha=0.2)
        if labels: ax.legend(loc=cls.config.legend_loc)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    # ==================== 特殊图表 ====================
    
    @classmethod
    def sankey(cls, flows, labels, orientations=None, title='', filename=None):
        """桑基图"""
        from matplotlib.sankey import Sankey
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        s = Sankey(ax=ax, scale=0.01, offset=0.2)
        s.add(flows=flows, labels=labels,
              orientations=orientations if orientations else [0]*len(flows))
        s.finish()
        ax.set_title(title)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def treemap(cls, sizes, labels, title='', filename=None):
        """树图"""
        try:
            import squarify
            fig, ax = plt.subplots(figsize=cls.config.figsize)
            colors = cls._get_colors(len(sizes))
            squarify.plot(sizes=sizes, label=labels, alpha=0.8,
                         color=colors, ax=ax)
            ax.axis('off')
            ax.set_title(title)
            plt.tight_layout()
            if filename: cls.config.save(filename)
            plt.show()
        except ImportError:
            print("需要安装squarify: pip install squarify")
    
    @classmethod
    def parallel(cls, data, class_col, xlabel='', ylabel='',
                 title='', filename=None):
        """平行坐标图"""
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        pd.plotting.parallel_coordinates(data, class_col,
                                         colormap=cls.config.cmap_sequential, ax=ax)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def ridge(cls, data_dict, xlabel='', title='', filename=None):
        """山脊图"""
        import seaborn as sns
        n = len(data_dict)
        fig, axes = plt.subplots(n, 1, figsize=cls.config.figsize, sharex=True)
        if n == 1: axes = [axes]
        colors = cls._get_colors(n)
        
        for i, (name, data) in enumerate(data_dict.items()):
            sns.kdeplot(data=data, ax=axes[i], fill=True,
                       color=colors[i % len(colors)], alpha=0.7)
            axes[i].set_ylabel('')
            axes[i].set_yticks([])
            for spine in ['left', 'top', 'right']:
                axes[i].spines[spine].set_visible(False)
            if i < n-1:
                axes[i].spines['bottom'].set_visible(False)
            axes[i].text(-3, 0.1, name, fontsize=9, fontweight='bold')
        
        axes[-1].set_xlabel(xlabel)
        fig.suptitle(title, fontsize=12, fontweight='bold')
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def bar3d(cls, x, y, z, xlabel='X', ylabel='Y', zlabel='Z',
              title='', filename=None):
        """3D柱状图"""
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure(figsize=cls.config.figsize)
        ax = fig.add_subplot(111, projection='3d')
        ax.bar3d(x.flatten(), y.flatten(), np.zeros_like(x.flatten()),
                dx=0.5, dy=0.5, dz=z.flatten(),
                color=plt.cm.viridis(z.flatten() / max(z.max(), 0.001)))
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        ax.set_title(title)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def hist2d(cls, x, y, bins=30, cmap=None,
               xlabel='X', ylabel='Y', title='', filename=None):
        """2D直方图"""
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        if cmap is None: cmap = cls.config.cmap_sequential
        h = ax.hist2d(x, y, bins=bins, cmap=cmap)
        plt.colorbar(h[3], ax=ax)
        cls._setup_ax(ax, title, xlabel, ylabel)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def textbox(cls, texts, positions, title='', filename=None):
        """文本框"""
        fig, ax = plt.subplots(figsize=cls.config.figsize)
        for text, (x, y) in zip(texts, positions):
            ax.text(x, y, text, ha='center', va='center',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.set_xlim(0, 10); ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_title(title)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def dual_axis(cls, x, y1, y2, label1='Left', label2='Right',
                  color1=None, color2=None, xlabel='', title='', filename=None):
        """双Y轴图表"""
        fig, ax1 = plt.subplots(figsize=cls.config.figsize)
        colors = cls._get_colors()
        
        if color1 is None: color1 = colors[0]
        if color2 is None: color2 = colors[1]
        
        ax1.plot(x, y1, color=color1, marker='o', label=label1)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(label1, color=color1)
        ax1.tick_params(axis='y', labelcolor=color1)
        
        ax2 = ax1.twinx()
        ax2.plot(x, y2, color=color2, marker='s', label=label2)
        ax2.set_ylabel(label2, color=color2)
        ax2.tick_params(axis='y', labelcolor=color2)
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc=cls.config.legend_loc)
        
        ax1.set_title(title)
        plt.tight_layout()
        if filename: cls.config.save(filename)
        plt.show()
    
    @classmethod
    def preview_colors(cls, palettes=None):
        """预览配色方案"""
        if palettes is None:
            palettes = ['Nature', 'Set1', 'Set2', 'Paired', 'Blues', 'RdBu_r']
        
        fig, axes = plt.subplots(len(palettes), 1, figsize=(10, len(palettes) * 0.8))
        if len(palettes) == 1: axes = [axes]
        
        for ax, name in zip(axes, palettes):
            cls.Palettes.preview_palette(name, ax)
        
        plt.tight_layout()
        plt.show()
    
    @classmethod
    def batch_plot(cls, data_dir, plot_func, output_dir='output',
                   formats=['png', 'pdf'], **kwargs):
        """批量绘图"""
        data_path = Path(data_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = []
        for csv_file in data_path.glob('*.csv'):
            try:
                df = pd.read_csv(csv_file)
                fig = plot_func(df, **kwargs)
                
                for fmt in formats:
                    save_path = output_path / f"{csv_file.stem}.{fmt}"
                    fig.savefig(save_path, dpi=cls.config.dpi, bbox_inches='tight')
                
                plt.close(fig)
                results.append({'file': csv_file.name, 'status': 'success'})
            except Exception as e:
                results.append({'file': csv_file.name, 'status': 'failed', 'error': str(e)})
        
        return pd.DataFrame(results)


# ============================================================
# 快捷入口
# ============================================================

sp = SciPlot


if __name__ == "__main__":
    print("=" * 60)
    print("sci_plot - 科研绘图工具箱 (增强版)")
    print("=" * 60)
    print(f"""
中文字体: {sp.config._chinese_font or '未检测到'}
当前配色: {sp.config.palette}

图表方法:
  sp.scatter()      散点图      sp.line()         折线图
  sp.bar()          柱状图      sp.histogram()    直方图
  sp.pie()          饼图        sp.ring()         环形图
  sp.heatmap()      热力图      sp.box()          箱线图
  sp.violin()       小提琴图    sp.errorbar()     误差线图
  sp.stack()        堆叠面积图  sp.multiline_fill() 填充多线图
  sp.dual_axis()    双Y轴图     sp.bar3d()        3D柱状图

配色方案: {', '.join(sp.Palettes.list_palettes().keys())}

配置方法:
  sp.config.palette = 'Set1'      # 切换配色
  sp.config.tick_inward = False   # 外向刻度
  sp.config.save('out', ['png'])  # 保存图片
    """)