import streamlit as st
import pandas as pd
import sys
import os
import time
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_handler import DataHandler
from src.table_operations import TableOperations

# Initialize session state for data persistence
if 'table_data' not in st.session_state:
    st.session_state.table_data = {}

if 'table_column_order' not in st.session_state:
    st.session_state.table_column_order = {}

if 'last_saved' not in st.session_state:
    st.session_state.last_saved = {}

if 'undo_stack' not in st.session_state:
    st.session_state.undo_stack = {}

def main():
    st.set_page_config(page_title="Data Table Manager", layout="wide", page_icon="📊")
    
    # Add custom CSS for better styling
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        /* White background for data tables */
        .stDataFrame, .stDataFrame > div {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        /* White background for download button */
        .stDownloadButton > button {
            background-color: #ffffff !important;
            border: 1px solid #000000 !important;
            color: #000000 !important;
        }
        /* Remove hover effects */
        .stDownloadButton > button:hover {
            background-color: #ffffff !important;
            border: 1px solid #000000 !important;
            color: #000000 !important;
        }
        /* White background for sidebar */
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        /* White background for tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff !important;
        }
        /* Simple header styling */
        .main-header {
            background-color: #000000 !important;
            color: #ffffff;
            padding: 20px;
            margin-bottom: 20px;
        }
        /* Simple tab styling */
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            font-size: 16px;
            font-weight: normal;
            color: #000000;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #000000;
            border-bottom: 2px solid #000000;
        }
        /* Ensure black text for all elements */
        .stMarkdown, .stText, .stCaption {
            color: #000000 !important;
        }
        .main-header {
            text-align: center;
            background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            font-size: 16px;
            font-weight: bold;
        }
        .css-1kyxreq {
            justify-content: center;
        }
        .success-message {
            padding: 10px;
            border-radius: 5px;
            background-color: #d4edda;
            color: #155724;
            margin: 10px 0;
        }
        .info-message {
            padding: 10px;
            border-radius: 5px;
            background-color: #d1ecf1;
            color: #0c5460;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("<h1 class='main-header'>📊 Data Table Manager</h1>", unsafe_allow_html=True)
    
    # Save button at the top
    data_handler = DataHandler()
    if st.button("💾 Save All Data", type="primary"):
        save_all_data(data_handler)
        st.success("All data saved!")
    
    st.markdown("---")
    
    # Initialize components
    table_ops = TableOperations()
    
    # Create tabs with icons
    tab1, tab2, tab3 = st.tabs(["📋 Table 1", "📊 Table 2", "📈 Table 3"])
    
    # Tab 1
    with tab1:
        handle_tab_content(1, data_handler, table_ops)
    
    # Tab 2
    with tab2:
        handle_tab_content(2, data_handler, table_ops)
    
    # Tab 3
    with tab3:
        handle_tab_content(3, data_handler, table_ops)
    
    # Sidebar with improved organization
    with st.sidebar:
        st.header("⚙️ Application Controls")
        
        # Undo section
        st.subheader("🔄 Undo")
        if st.button("Undo Last Change", use_container_width=True):
            undo_last_change()
        
        # Last saved info
        st.subheader("🕒 Last Saved")
        for i in range(1, 4):
            if i in st.session_state.last_saved:
                st.caption(f"Table {i}: {st.session_state.last_saved[i]}")
            else:
                st.caption(f"Table {i}: Never")
        
        # Help section
        st.subheader("ℹ️ Help")
        st.markdown("""
        - Use tabs to switch between tables
        - Edit data directly in the table
        - Filter and sort using the operation tabs
        - Delete rows in batch using the delete tab
        - Download tables using the download button
        """)

def handle_tab_content(tab_number, data_handler, table_ops):
    """Handle content for each tab"""
    st.markdown(f"<h3 style='color: #4b6cb7;'>Table {tab_number} Data</h3>", unsafe_allow_html=True)
    
    # Initialize session state for this table if not exists
    if tab_number not in st.session_state.table_data:
        # Try to load existing data
        filename = f"table{tab_number}.csv"
        df = data_handler.read_file(filename)
        if df.empty:
            # Create empty DataFrame with default columns
            df = pd.DataFrame(columns=["Column1", "Column2", "Column3"])
        st.session_state.table_data[tab_number] = df
        st.session_state.table_column_order[tab_number] = list(df.columns)
        st.session_state.undo_stack[tab_number] = []
    
    # File upload for appending data
    st.markdown("##### 📤 Upload Data")
    uploaded_file = st.file_uploader(
        f"Upload CSV/Excel for Table {tab_number}",
        type=["csv", "xlsx", "xls"],
        key=f"uploader_{tab_number}",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Save current state for undo
            st.session_state.undo_stack[tab_number].append(
                st.session_state.table_data[tab_number].copy()
            )
            
            # Load new data
            if uploaded_file.name.endswith('.csv'):
                new_df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                new_df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format.")
                return
            
            # Validate columns
            current_df = st.session_state.table_data[tab_number]
            if not current_df.empty:
                # Check if columns match
                if not new_df.columns.equals(current_df.columns):
                    st.warning("⚠️ Column mismatch detected!")
                    st.write("Current table columns:", list(current_df.columns))
                    st.write("Uploaded file columns:", list(new_df.columns))
                    
                    # Offer options to handle mismatch
                    option = st.radio(
                        "How would you like to proceed?",
                        ("Append with column alignment", "Append as new columns", "Cancel upload"),
                        key=f"column_mismatch_{tab_number}"
                    )
                    
                    if option == "Cancel upload":
                        st.info("Upload cancelled.")
                        return
                    elif option == "Append with column alignment":
                        # Align columns and fill missing values with empty strings
                        for col in current_df.columns:
                            if col not in new_df.columns:
                                new_df[col] = ""
                        # Reorder columns to match current table
                        new_df = new_df[current_df.columns]
                    elif option == "Append as new columns":
                        # Add missing columns to current table
                        for col in new_df.columns:
                            if col not in current_df.columns:
                                current_df[col] = ""
                        # Update session state
                        st.session_state.table_data[tab_number] = current_df
            
            # Append to existing data
            combined_df = pd.concat([current_df, new_df], ignore_index=True)
            st.session_state.table_data[tab_number] = combined_df
            st.success(f"✅ Data appended to Table {tab_number}!")
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    # Display editable table
    if not st.session_state.table_data[tab_number].empty:
        st.markdown(f"**Table {tab_number}** (Editable)")
        
        # Column management
        with st.expander("📝 Column Management"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Add new column
                new_col_name = st.text_input("New Column Name", key=f"new_col_{tab_number}")
                if st.button("➕ Add Column", key=f"add_col_{tab_number}"):
                    if new_col_name and new_col_name not in st.session_state.table_data[tab_number].columns:
                        # Save current state for undo
                        st.session_state.undo_stack[tab_number].append(
                            st.session_state.table_data[tab_number].copy()
                        )
                        
                        # Add new column with empty values
                        st.session_state.table_data[tab_number][new_col_name] = ""
                        st.success(f"Column '{new_col_name}' added!")
                    elif new_col_name in st.session_state.table_data[tab_number].columns:
                        st.warning(f"Column '{new_col_name}' already exists!")
            
            with col2:
                # Delete columns
                if len(st.session_state.table_data[tab_number].columns) > 1:
                    cols_to_delete = st.multiselect(
                        "Select Columns to Delete",
                        st.session_state.table_data[tab_number].columns,
                        key=f"del_col_{tab_number}"
                    )
                    if st.button("🗑️ Delete Selected Columns", key=f"delete_col_{tab_number}"):
                        if cols_to_delete:
                            # Save current state for undo
                            st.session_state.undo_stack[tab_number].append(
                                st.session_state.table_data[tab_number].copy()
                            )
                            
                            # Delete columns
                            st.session_state.table_data[tab_number] = st.session_state.table_data[tab_number].drop(columns=cols_to_delete)
                            st.success(f"Columns {cols_to_delete} deleted!")
                        else:
                            st.warning("Please select at least one column to delete.")
                else:
                    st.info("Need at least one column to display data")
        
        # Create tabs for different operations
        op_tab1, op_tab2, op_tab3, op_tab4 = st.tabs(["✏️ Edit", "🔍 Filter", "🔄 Sort", "🗑️ Delete"])
        
        with op_tab1:
            st.markdown("###### Edit your data directly in the table below:")
            # Create editable dataframe
            edited_df = st.data_editor(
                st.session_state.table_data[tab_number],
                num_rows="dynamic",
                key=f"editor_{tab_number}",
                height=400,
                use_container_width=True
            )
            
            # Update session state if changes were made
            if not edited_df.equals(st.session_state.table_data[tab_number]):
                # Save current state for undo
                st.session_state.undo_stack[tab_number].append(
                    st.session_state.table_data[tab_number].copy()
                )
                
                # Update column order if it has changed
                if list(edited_df.columns) != list(st.session_state.table_data[tab_number].columns):
                    st.session_state.table_column_order[tab_number] = list(edited_df.columns)
                
                st.session_state.table_data[tab_number] = edited_df
                st.success("✅ Changes saved!")
        
        with op_tab2:
            st.markdown("###### Filter your data using the options below:")
            # Apply advanced filtering
            filtered_df = table_ops.advanced_filter_dataframe(st.session_state.table_data[tab_number], str(tab_number))
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            # Option to apply filter to main data
            if not filtered_df.equals(st.session_state.table_data[tab_number]) and not filtered_df.empty:
                if st.button("Apply Filter to Main Data", key=f"apply_filter_{tab_number}"):
                    # Save current state for undo
                    st.session_state.undo_stack[tab_number].append(
                        st.session_state.table_data[tab_number].copy()
                    )
                    st.session_state.table_data[tab_number] = filtered_df
                    st.success("✅ Filter applied to main data!")
        
        with op_tab3:
            st.markdown("###### Sort your data using the options below:")
            # Apply sorting
            sorted_df = table_ops.sort_dataframe(st.session_state.table_data[tab_number], str(tab_number))
            st.dataframe(sorted_df, use_container_width=True, height=400)
            
            # Option to apply sort to main data
            if not sorted_df.equals(st.session_state.table_data[tab_number]):
                if st.button("Apply Sort to Main Data", key=f"apply_sort_{tab_number}"):
                    # Save current state for undo
                    st.session_state.undo_stack[tab_number].append(
                        st.session_state.table_data[tab_number].copy()
                    )
                    st.session_state.table_data[tab_number] = sorted_df
                    st.success("✅ Sort applied to main data!")
        
        with op_tab4:
            st.markdown("###### Select rows to delete:")
            current_df = st.session_state.table_data[tab_number].copy()
            current_df["Select"] = False
            
            # Show dataframe with selection column
            edited_with_selection = st.data_editor(
                current_df,
                num_rows="fixed",
                key=f"delete_editor_{tab_number}",
                height=400,
                use_container_width=True
            )
            
            # Check which rows were selected for deletion
            selected_rows = edited_with_selection[edited_with_selection["Select"] == True]
            
            if not selected_rows.empty:
                st.warning(f"⚠️ {len(selected_rows)} rows selected for deletion")
                if st.button(f"🗑️ Delete {len(selected_rows)} Selected Rows", key=f"delete_button_{tab_number}"):
                    # Save current state for undo
                    st.session_state.undo_stack[tab_number].append(
                        st.session_state.table_data[tab_number].copy()
                    )
                    
                    # Remove selected rows (excluding the "Select" column)
                    indices_to_delete = selected_rows.index.tolist()
                    new_df = st.session_state.table_data[tab_number].drop(indices_to_delete).reset_index(drop=True)
                    st.session_state.table_data[tab_number] = new_df
                    st.success(f"✅ Deleted {len(indices_to_delete)} rows!")
                    
                    # Rerun to refresh the UI
                    st.rerun()
            else:
                st.info("ℹ️ Select rows by checking the 'Select' checkbox to delete them.")
        
        # Download button
        st.markdown("---")
        csv = convert_df_to_csv(st.session_state.table_data[tab_number])
        st.download_button(
            label="📥 Download Table Data",
            data=csv,
            file_name=f"table{tab_number}_data.csv",
            mime="text/csv",
            key=f"download_{tab_number}",
            use_container_width=True
        )
    else:
        st.info("ℹ️ No data available. Upload a file to get started.")

def save_all_data(data_handler):
    """Save all table data to files"""
    for tab_number in st.session_state.table_data:
        filename = f"table{tab_number}.csv"
        # Reorder columns according to user preference before saving
        if tab_number in st.session_state.table_column_order:
            df_to_save = st.session_state.table_data[tab_number].copy()
            # Reorder columns to match the user's preference
            columns_in_order = st.session_state.table_column_order[tab_number]
            # Add any new columns that might not be in the stored order
            for col in df_to_save.columns:
                if col not in columns_in_order:
                    columns_in_order.append(col)
            df_to_save = df_to_save[columns_in_order]
        else:
            df_to_save = st.session_state.table_data[tab_number]
        data_handler.write_file(df_to_save, filename)
        st.session_state.last_saved[tab_number] = datetime.now().strftime("%H:%M:%S")

def undo_last_change():
    """Undo the last change for all tables"""
    for tab_number in st.session_state.undo_stack:
        if st.session_state.undo_stack[tab_number]:
            # Restore previous state
            st.session_state.table_data[tab_number] = st.session_state.undo_stack[tab_number].pop()
    st.success("Last change undone!")

def convert_df_to_csv(df):
    """Convert DataFrame to CSV string"""
    return df.to_csv(index=False).encode('utf-8')

if __name__ == "__main__":
    main()