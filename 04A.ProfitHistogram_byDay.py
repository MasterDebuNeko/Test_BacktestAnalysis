import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from IPython.display import display

# Load your trade DataFrame
# Assuming trade_results_df exists from the previous cell execution
# If you are running this cell independently, make sure trade_results_df is loaded or created first.
try:
    df = trade_results_df.copy()
except NameError:
    print("❌ Error: 'trade_results_df' is not defined.")
    print("โปรดรันเซลล์ที่คำนวณ R-Multiples และ Risk ก่อนเซลล์นี้")
    # Exit the cell execution gracefully if trade_results_df is missing
    get_ipython().run_cell_magic('javascript', '', 'IPython.notebook.execute_prev_cell()') # Attempt to run previous cell
    raise # Re-raise the error to stop current cell execution


# Ensure required columns exist and are sorted by Entry Time
required_cols = ['Entry Time', 'Profit(R)', 'Entry Day']
if not all(col in df.columns for col in required_cols):
    missing = [col for col in required_cols if col not in df.columns]
    raise KeyError(f"คอลัมน์ที่จำเป็นไม่ครบถ้วน: {missing}. ตรวจสอบ calc_r_multiple_and_risk.")

# Prepare Entry Date and Cumulative R columns, sorted by Entry Time
df = df.sort_values('Entry Time').reset_index(drop=True)
df = df[df['Entry Time'].notnull()].copy() # Filter out rows with missing Entry Time and create a copy

# Ensure Entry Time and Profit(R) are correct types
df['Entry Time'] = pd.to_datetime(df['Entry Time'])
df['Entry Day'] = df['Entry Time'].dt.day_name() # Recalculate Entry Day based on sorted/cleaned Entry Time
df['Profit(R)'] = df['Profit(R)'].astype(float)

# Filter out rows with NaN in 'Profit(R)' before calculating anything else
df_valid = df.dropna(subset=['Profit(R)']).copy()

# Define the order of days of the week
day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

print("## R-Multiple Histograms by Entry Day")

# Set up the figure and axes for subplots
# Calculate the number of days with valid trades to determine grid size
days_with_valid_trades = df_valid['Entry Day'].unique()
num_days_with_valid_trades = len(days_with_valid_trades)

# Determine the number of rows and columns for subplots (e.g., max 2 columns)
ncols = 2
nrows = (num_days_with_valid_trades + ncols - 1) // ncols # Ceiling division

# Create subplots only if there are valid trades on at least one day
if num_days_with_valid_trades > 0:
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, 5 * nrows), squeeze=False)
    axes = axes.flatten() # Flatten the 2D array of axes for easy iteration
else:
    print("ℹ️ ไม่มีเทรดที่มี Profit(R) ที่ถูกต้องในข้อมูล.")
    axes = [] # Empty list if no valid trades

ax_idx = 0 # Counter for which axis to use

# Prepare list to store summary stats for the table
daily_summary_stats = []

# Iterate through each day of the week in order
for day in day_order:
    df_day = df_valid[df_valid['Entry Day'] == day].copy()

    # 1. Data Filter: Skip if no valid trades on this day
    if df_day.empty:
        print(f"ℹ️ ไม่มีเทรดที่เข้าในวัน {day} และมี Profit(R) ที่ถูกต้อง. ข้ามการสร้างกราฟสำหรับวันนี้.")
        continue # Skip to the next day

    # Extract valid R values for this day
    r_values_day = df_day['Profit(R)']

    # Calculate Metrics for this day
    n_win_day = (r_values_day > 0).sum()
    n_loss_day = (r_values_day < 0).sum()
    total_trades_day = len(r_values_day)
    expectancy_day = r_values_day.mean()
    win_rate_day = 100 * (n_win_day / total_trades_day) if total_trades_day > 0 else 0.0
    avg_win_day = r_values_day[r_values_day > 0].mean()
    avg_loss_day = r_values_day[r_values_day < 0].mean()

    # Add daily stats to the list
    daily_summary_stats.append({
        "Entry Day": day,
        "Expectancy (R)": round(expectancy_day, 2) if pd.notnull(expectancy_day) else "N/A",
        "Win Rate (%)": round(win_rate_day, 2),
        "Avg Win (R)": round(avg_win_day, 2) if pd.notnull(avg_win_day) else "N/A",
        "Avg Loss (R)": round(avg_loss_day, 2) if pd.notnull(avg_loss_day) else "N/A",
        "Number of Win": n_win_day,
        "Number of Loss": n_loss_day,
        "Total Trades": total_trades_day
    })


    # --- Plot Histogram for the current day ---
    if total_trades_day > 0:
        ax = axes[ax_idx] # Get the next available subplot axis

        # Use the filtered series for plotting.
        ax.hist(r_values_day[r_values_day > 0], bins=15, color='deepskyblue', alpha=0.7, label=f'Wins (n={n_win_day})', edgecolor='white')
        ax.hist(r_values_day[r_values_day < 0], bins=15, color='salmon', alpha=0.7, label=f'Losses (n={n_loss_day})', edgecolor='white')

        # Add expectancy line if valid for this day
        if pd.notnull(expectancy_day):
            ax.axvline(expectancy_day, color='purple', linestyle='dashed', linewidth=1.5, label=f'Expectancy ({expectancy_day:.2f} R)')

        ax.set_title(f'{day} R-Multiple Distribution')
        ax.set_xlabel('Profit(R)')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(axis='y', alpha=0.75)

        ax_idx += 1 # Move to the next subplot axis


# Hide any unused subplots
for i in range(ax_idx, len(axes)):
    fig.delaxes(axes[i])

# Adjust layout for subplots
if num_days_with_valid_trades > 0:
    plt.tight_layout(rect=[0, 0, 1, 0.95]) # Adjust layout to make space for a potential overall title
    # fig.suptitle('R-Multiple Distribution by Entry Day', fontsize=16, y=1.02) # Optional: Add a main title
    plt.show()
else:
     print("ℹ️ ไม่สามารถสร้างกราฟ Histogram ใดๆ ได้ เนื่องจากไม่มีเทรดที่มี Profit(R) ที่ถูกต้อง.")


# 4. Output Daily Summary Table
print("\n## Daily R-Multiple Performance Summary")
if daily_summary_stats:
    daily_stats_df = pd.DataFrame(daily_summary_stats)
    # Ensure days are in the desired order in the table
    daily_stats_df['Entry Day'] = pd.Categorical(daily_stats_df['Entry Day'], categories=day_order, ordered=True)
    daily_stats_df = daily_stats_df.sort_values('Entry Day')
    display(daily_stats_df.style.hide(axis="index")) # Use display to show the table neatly
else:
    print("ℹ️ ไม่มีข้อมูลสรุปประจำวัน เนื่องจากไม่มีเทรดที่มี Profit(R) ที่ถูกต้อง.")
