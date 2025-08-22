import pandas as pd
import streamlit as st

class TableOperations:
    @staticmethod
    def advanced_filter_dataframe(df: pd.DataFrame, tab_id: str = "") -> pd.DataFrame:
        """
        Advanced DataFrame filtering with multiple options
        """
        if df.empty:
            return df
            
        st.markdown("### 🔍 Filtering Options")
        columns = df.columns.tolist()
        
        # Create filters for each column
        filters = {}
        cols = st.columns(min(len(columns), 3))
        
        for i, col in enumerate(columns):
            with cols[i % 3]:
                if df[col].dtype in ['object', 'category']:
                    unique_values = df[col].unique()
                    selected_values = st.multiselect(
                        f"Filter {col}",
                        unique_values,
                        default=None,
                        key=f"filter_{col}_{tab_id}"
                    )
                    if selected_values:
                        filters[col] = selected_values
                elif df[col].dtype in ['int64', 'float64']:
                    min_val = float(df[col].min())
                    max_val = float(df[col].max())
                    values = st.slider(
                        f"Range for {col}",
                        min_val, max_val,
                        (min_val, max_val),
                        key=f"range_{col}_{tab_id}"
                    )
                    filters[col] = values
        
        # Apply filters
        filtered_df = df.copy()
        for col, filter_val in filters.items():
            if isinstance(filter_val, list) and filter_val:
                filtered_df = filtered_df[filtered_df[col].isin(filter_val)]
            elif isinstance(filter_val, tuple) and len(filter_val) == 2:
                filtered_df = filtered_df[
                    (filtered_df[col] >= filter_val[0]) &
                    (filtered_df[col] <= filter_val[1])
                ]
        
        return filtered_df
    
    @staticmethod
    def sort_dataframe(df: pd.DataFrame, tab_id: str = "") -> pd.DataFrame:
        """
        Sort DataFrame by selected columns
        """
        if df.empty:
            return df
            
        st.markdown("### 🔄 Sorting Options")
        columns = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            sort_column = st.selectbox("Sort by", columns, key=f"sort_col_{tab_id}")
        with col2:
            sort_order = st.radio("Order", ["Ascending", "Descending"], key=f"sort_order_{tab_id}")
        
        if sort_column:
            ascending = sort_order == "Ascending"
            df = df.sort_values(by=sort_column, ascending=ascending)
        
        return df

    @staticmethod
    def editable_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create an editable Streamlit DataFrame
        """
        if df.empty:
            st.info("No data to display. Add some data to get started.")
            return df
            
        return st.data_editor(
            df,
            num_rows="dynamic",  # Allow adding/deleting rows
            column_config={col: st.column_config.Column() for col in df.columns},
            height=400
        )
    
    @staticmethod
    def batch_delete_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Allow users to select and delete multiple rows
        """
        if df.empty:
            return df
            
        st.markdown("### 🗑️ Batch Delete Rows")
        
        # Create a checkbox column for selection
        selection_col = "Select"
        
        # Show dataframe with selection checkboxes
        st.dataframe(df, use_container_width=True)
        
        # Get row indices to delete
        row_indices = st.multiselect(
            "Select rows to delete (by index)",
            options=df.index.tolist(),
            help="Select the row indices you want to delete"
        )
        
        if row_indices:
            if st.button("Delete Selected Rows"):
                # Remove selected rows
                new_df = df.drop(row_indices).reset_index(drop=True)
                st.success(f"Deleted {len(row_indices)} rows!")
                return new_df
        
        return df