import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Assuming trade_results_df is available from previous steps
# If not, ensure you run the cells that load and process your data first.
try:
    df = trade_results_df.copy()
except NameError:
    print("❌ Error: 'trade_results_df' is not defined.")
    print("โปรดรันเซลล์ที่คำนวณ R-Multiples และ Risk ก่อนเซลล์นี้")
    # Exit the cell execution gracefully if trade_results_df is missing
    from IPython import get_ipython
    get_ipython().run_cell_magic('javascript', '', 'IPython.notebook.execute_prev_cell()')
    raise # Re-raise the error to stop current cell execution

# Ensure the required columns exist
required_cols = ['MFE(R)', 'Profit(R)']
if not all(col in df.columns for col in required_cols):
    missing = [col for col in required_cols if col not in df.columns]
    raise KeyError(f"คอลัมน์ที่จำเป็นไม่ครบถ้วนสำหรับ histogram: {missing}. ตรวจสอบ calc_r_multiple_and_risk.")

# Filter for negative trades and drop NaNs in MFE(R)
# We filter for Profit(R) < 0 first, then drop NaNs in MFE(R)
df_losses = df[df['Profit(R)'] < 0].copy()
df_plot = df_losses.dropna(subset=['MFE(R)']).copy()


# Handle empty dataframe case after filtering and dropping NaNs
if df_plot.empty:
    print("ℹ️ ไม่มีเทรดที่ขาดทุนหรือไม่มีข้อมูล MFE(R) ที่ถูกต้องสำหรับเทรดที่ขาดทุน. ไม่สามารถสร้างกราฟ histogram ได้")
else:
    # Calculate Median and 70th Percentile *from the losing trades' MFE(R)*
    mfe_values_losses = df_plot['MFE(R)']
    median_mfe_losses = mfe_values_losses.median()
    percentile_70_mfe_losses = mfe_values_losses.quantile(0.70) # Use 0.70 for 70th percentile

    # Create the histogram
    plt.figure(figsize=(12, 7)) # Slightly wider figure to accommodate labels

    ax = sns.histplot(data=df_plot, x='MFE(R)', kde=False, color='salmon', edgecolor='white', alpha=0.8, bins=50) # Changed color to salmon for losses

    # Add vertical lines for Median and 70th Percentile (based on losing trades)
    ax.axvline(median_mfe_losses, color='purple', linestyle='dashed', linewidth=1.5, label=f'Median (Losses) ({median_mfe_losses:.2f} R)')
    ax.axvline(percentile_70_mfe_losses, color='green', linestyle='dashed', linewidth=1.5, label=f'70th Percentile (Losses) ({percentile_70_mfe_losses:.2f} R)')

    # Add labels and title
    ax.set_xlabel('MFE (R-Multiple)')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of MFE for Losing Trades')
    ax.grid(axis='y', linestyle='--', alpha=0.7) # Add a grid on the y-axis

    # Add a legend to identify the vertical lines
    ax.legend()

    plt.show()
