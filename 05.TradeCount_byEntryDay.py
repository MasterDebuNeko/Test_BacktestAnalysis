import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython.display import display

# Assuming trade_results_df is available from previous steps
# If not, uncomment and run the first cell from before to generate it:
# from IPython import get_ipython
# from IPython.display import display
# excel_file_path = '/content/GF ADR GC BE2R.xlsx' # <--- CHANGE THIS
# desired_stop_loss = 0.002 # <--- CHANGE THIS
# try:
#     trade_results_df = calc_r_multiple_and_risk(excel_file_path, desired_stop_loss)
# except Exception as e:
#     print(f"❌ Error loading data: {e}")
#     trade_results_df = pd.DataFrame() # Create empty df to prevent errors below

try:
    df = trade_results_df.copy()
except NameError:
    print("❌ Error: 'trade_results_df' is not defined.")
    print("โปรดรันเซลล์ที่คำนวณ R-Multiples และ Risk ก่อนเซลล์นี้")
    # Exit the cell execution gracefully if trade_results_df is missing
    get_ipython().run_cell_magic('javascript', '', 'IPython.notebook.execute_prev_cell()') # Attempt to run previous cell
    raise # Re-raise the error to stop current cell execution


# Ensure required columns exist
required_cols = ['Entry Time', 'Profit(R)']
if not all(col in df.columns for col in required_cols):
    missing = [col for col in required_cols if col not in df.columns]
    raise KeyError(f"คอลัมน์ที่จำเป็นไม่ครบถ้วน: {missing}. ตรวจสอบ calc_r_multiple_and_risk.")


# Prepare data for plotting and table
df = df[df['Entry Time'].notnull()].copy() # Filter out rows with missing Entry Time and create a copy

# Ensure Entry Time and Profit(R) are correct types
df['Entry Time'] = pd.to_datetime(df['Entry Time'])
df['Profit(R)'] = df['Profit(R)'].astype(float)

# Add Entry Day of Week and short code
df['Entry Day'] = df['Entry Time'].dt.day_name()
day_name_to_code = {
    'Sunday': 'SUN', 'Monday': 'MON', 'Tuesday': 'TUE',
    'Wednesday': 'WED', 'Thursday': 'THU', 'Friday': 'FRI',
    'Saturday': 'SAT'
}
df['Entry Day Code'] = df['Entry Day'].map(day_name_to_code)

# Categorize trades by result
df['Result Type'] = 'Breakeven' # Default
df.loc[df['Profit(R)'] > 0, 'Result Type'] = 'Win'
df.loc[df['Profit(R)'] < 0, 'Result Type'] = 'Loss'

# Define the desired order of days (Sun-Fri) and result types
day_order = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI']
result_order = ['Win', 'Loss', 'Breakeven'] # Order for plotting and table columns

# Count trades by Day Code and Result Type
trade_counts = df.groupby(['Entry Day Code', 'Result Type']).size().unstack(fill_value=0)

# Ensure all days and result types are present, even if counts are zero
for day in day_order:
    if day not in trade_counts.index:
        trade_counts.loc[day] = 0 # Add row for missing day

for result in result_order:
    if result not in trade_counts.columns:
        trade_counts[result] = 0 # Add column for missing result type

# Reindex and reorder columns according to the desired order
trade_counts = trade_counts.reindex(day_order)
trade_counts = trade_counts[result_order]

# Calculate total trades per day
trade_counts['Total'] = trade_counts.sum(axis=1)

# --- Prepare data for the Summary Table ---
# We need both counts and percentages in the table.
# Let's create a new DataFrame for the table
summary_data = []
for day_code in day_order:
    day_counts = trade_counts.loc[day_code]
    total_trades_day = day_counts['Total']

    row_data = {'Entry Day': day_code}
    for result_type in result_order:
        count = day_counts[result_type]
        percentage = (count / total_trades_day) * 100 if total_trades_day > 0 else 0
        row_data[f'{result_type} Count'] = count
        row_data[f'{result_type} %'] = percentage

    row_data['Total Trades'] = total_trades_day
    summary_data.append(row_data)

summary_df = pd.DataFrame(summary_data)

# Define the desired column order for the table
table_column_order = [
    'Entry Day',
    'Win Count', 'Win %',
    'Loss Count', 'Loss %',
    'Breakeven Count', 'Breakeven %',
    'Total Trades'
]
summary_df = summary_df[table_column_order]

# Sort by the defined day order
summary_df['Entry Day'] = pd.Categorical(summary_df['Entry Day'], categories=day_order, ordered=True)
summary_df = summary_df.sort_values('Entry Day').reset_index(drop=True)


# Define colors (used for plotting)
colors = {
    'Win': 'deepskyblue',
    'Loss': 'salmon',
    'Breakeven': '#b0b0b0' # gray
}

# --- Plotting ---
print("Trade Counts and Percentage by Entry Day and Result Type (Sun-Fri) - Chart")
fig, ax = plt.subplots(figsize=(12, 7))

# Calculate bar width and positions
bar_width = 0.25
x = np.arange(len(day_order)) # x-axis positions for each day group

# Plot bars for each result type
rects1 = ax.bar(x - bar_width, trade_counts['Win'], bar_width, label='Win', color=colors['Win'])
rects2 = ax.bar(x, trade_counts['Loss'], bar_width, label='Loss', color=colors['Loss'])
rects3 = ax.bar(x + bar_width, trade_counts['Breakeven'], bar_width, label='Breakeven', color=colors['Breakeven'])

# Function to add percentage and count labels above bars with custom formatting
def add_labels_custom_format(rects, result_type, colors_dict, trade_counts_df, total_col):
    label_color = colors_dict[result_type] # Get the color for this result type

    for i, rect in enumerate(rects):
        height = rect.get_height()
        total_trades_day = trade_counts_df.iloc[i][total_col]
        center_x = rect.get_x() + rect.get_width() / 2

        # Anchor point for labels is the top center of the bar
        label_anchor_y = height

        # Add percentage label (above count)
        if total_trades_day > 0:
            percentage = (height / total_trades_day) * 100
            ax.annotate(f'{percentage:.1f}%', # No parentheses, add % sign
                        xy=(center_x, label_anchor_y),
                        xytext=(0, 18),  # Positive offset to move up
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize='medium', fontweight='bold', color=label_color) # Use color of the bar
        elif height == 0 and total_trades_day > 0:
             # Special case: 0 count, but total > 0. Still show 0%
             ax.annotate(f'0.0%', # No parentheses, add % sign
                         xy=(center_x, label_anchor_y), # Anchor at height 0
                         xytext=(0, 18), # Same offset as above
                         textcoords="offset points",
                         ha='center', va='bottom',
                         fontsize='medium', fontweight='bold', color=label_color)


        # Add count label (below percentage)
        if height > 0 or total_trades_day == 0: # Always show 0 count, or show count for non-zero bars
             ax.annotate(f'{int(height)}',
                         xy=(center_x, label_anchor_y),
                         xytext=(0, 3),  # Small positive offset
                         textcoords="offset points",
                         ha='center', va='bottom',
                         fontsize='small', color=label_color) # Use color of the bar


# Add labels to each set of bars, passing the result type and colors dictionary
add_labels_custom_format(rects1, 'Win', colors, trade_counts, 'Total')
add_labels_custom_format(rects2, 'Loss', colors, trade_counts, 'Total')
add_labels_custom_format(rects3, 'Breakeven', colors, trade_counts, 'Total')


# Set up axes and labels
ax.set_xlabel('Entry Day of Week')
ax.set_ylabel('Number of Trades')
ax.set_title('Trade Counts and Percentage by Entry Day and Result Type (Sun-Fri)')
ax.set_xticks(x)
ax.set_xticklabels(day_order)
ax.legend(title='Result Type')
ax.grid(axis='y', linestyle='--', alpha=0.7) # Add horizontal grid lines

# Adjust y-axis limits to make space for labels above the highest bar
ax.set_ylim(0, trade_counts[['Win', 'Loss', 'Breakeven']].max().max() * 1.45) # Buffer

plt.tight_layout() # Adjust layout
plt.show()


# --- Display the Summary Table ---
print("\nSummary Table: Trade Counts and Percentage by Entry Day and Result Type (Sun-Fri)")
# Format percentages for display
formatted_summary_df = summary_df.copy()
for result_type in result_order:
    formatted_summary_df[f'{result_type} %'] = formatted_summary_df[f'{result_type} %'].map('{:.1f}%'.format)

# Hide the index for cleaner display
display(formatted_summary_df.style.hide(axis="index"))
