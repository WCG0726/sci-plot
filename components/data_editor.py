"""
components/data_editor.py - 数据编辑组件
========================================
包含数据预览和编辑功能
"""

import streamlit as st
import pandas as pd
import numpy as np


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
    
    # 显示数据表
    st.markdown("**数据表格:**")
    
    # 提供两种编辑模式
    edit_mode = st.radio("编辑模式", ["查看模式", "编辑模式"], horizontal=True, key="edit_mode")
    
    if edit_mode == "编辑模式":
        try:
            edited = st.data_editor(
                st.session_state.edited_df,
                use_container_width=True,
                num_rows="fixed",
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


def show_data_preview(df):
    """显示数据预览"""
    with st.expander("📋 数据预览", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**行数:** {df.shape[0]}")
            st.write(f"**列数:** {df.shape[1]}")
        with col2:
            st.write(f"**数值列:** {len(df.select_dtypes(include=[np.number]).columns)}")
            st.write(f"**类别列:** {len(df.select_dtypes(exclude=[np.number]).columns)}")
        
        # 显示描述性统计
        if st.checkbox("显示描述统计"):
            st.dataframe(df.describe())