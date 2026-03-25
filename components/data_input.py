"""
components/data_input.py - 数据输入组件
======================================
包含数据上传、手动输入、示例数据等功能
"""

import streamlit as st
import pandas as pd
import numpy as np


def data_input_section():
    """数据输入区域"""
    st.sidebar.header("📁 数据输入")
    
    data_source = st.sidebar.radio("选择数据来源", 
                                    ["上传文件", "手动输入", "示例数据"])
    
    df = None
    
    if data_source == "上传文件":
        df = _upload_file()
    elif data_source == "手动输入":
        df = _manual_input()
    else:  # 示例数据
        df = _example_data()
    
    return df


def _upload_file():
    """文件上传处理"""
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
            return df
        except Exception as e:
            st.sidebar.error(f"读取失败: {e}")
    return None


def _manual_input():
    """手动输入数据"""
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
            return pd.DataFrame(rows, columns=[c.strip() for c in col_names])
        except Exception as e:
            st.sidebar.error(f"格式错误: {e}")
    return None


def _example_data():
    """生成示例数据"""
    example_type = st.sidebar.selectbox(
        "选择示例数据",
        ["正弦余弦", "随机散点", "分组数据", "误差线数据", "时间序列", "多列对比"]
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
    elif example_type == "时间序列":
        dates = pd.date_range('2024-01-01', periods=100)
        df = pd.DataFrame({
            'Date': dates,
            'Value_A': np.cumsum(np.random.randn(100)) + 100,
            'Value_B': np.cumsum(np.random.randn(100)) + 50
        })
    else:  # 多列对比
        df = pd.DataFrame({
            'Method': ['A', 'B', 'C', 'D'],
            'Score1': [85, 92, 78, 95],
            'Score2': [88, 90, 82, 93],
            'Score3': [82, 94, 80, 96]
        })
    
    st.sidebar.success(f"✅ {example_type}")
    return df