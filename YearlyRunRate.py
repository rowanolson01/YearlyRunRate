import pandas as pd
import matplotlib.pyplot as plt

#Load and clean data
df = pd.read_csv('Yearly Run Rate/BMandSD Retail Sales.csv')
df = df.rename(columns={'MRTSSM4441USN': 'total_revenue'})
df['observation_date'] = pd.to_datetime(df['observation_date'])
df['year'] = df['observation_date'].dt.year

#Create dataframe with the yearly sums for all years prior to 2025. This is so 2025 (the test set) does not influence historical data and eliminates 2026 partial data
yearly_df = df.groupby('year')['total_revenue'].sum().reset_index()
yearly_df = yearly_df[yearly_df['year'] < 2025]
yearly_df = yearly_df.rename(columns={'total_revenue': 'yearly_total'})

#Calculate YTD revenue and the YTD percent of EOY revenue for each row
df = df.merge(yearly_df[['year', 'yearly_total']], on='year', how='left')
df['ytd_sum'] = df.groupby('year')['total_revenue'].cumsum()
df['ytd_pct'] = df['ytd_sum'] / df['yearly_total']

#Create dataframe with the average YTD percent for each month from historical data
avg_ytd_pct = df.groupby(df['observation_date'].dt.month)['ytd_pct'].mean().reset_index()
avg_ytd_pct = avg_ytd_pct.rename(columns={'observation_date': 'month'})

#Create dataframe for 2025 test data
actual_2025 = df[df['year'] == 2025]['total_revenue'].sum()
df_2025 = df[df['year'] == 2025].copy()
df_2025['month_num'] = range(1, 13)

#Projects EOY total revenue for each month based on the YTD revenue in 2 methods -- The Historical Model calculates EOY total by 
#calculating the monthly YTD % against the actual YTD revenue [YTD Revenue / Avg YTD %] for each month. The Simple Model assumes linear growth, calculating 
#EOY total [YTD Revenue / Elapsed Months * 12] for each month. Each model calculates projected EOY total revenueas well as the difference between the projected and actual
#EOY totals
df_2025['runrate_hist'] = df_2025['ytd_sum'] / avg_ytd_pct['ytd_pct'].values
df_2025['diff_hist'] = df_2025['runrate_hist'] - actual_2025
df_2025['runrate_trad'] = (df_2025['ytd_sum'] / df_2025['month_num']) * 12
df_2025['diff_trad'] = df_2025['runrate_trad'] - actual_2025

#Clean 2025 dataframe
final_df = df_2025[['observation_date', 'ytd_sum', 'runrate_hist', 'diff_hist', 'runrate_trad', 'diff_trad']]

#Create linear chart for 2025 difference between project and actual EOY total revenue for each month
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#D9D9D9')
ax.set_facecolor('#D9D9D9')
ax.plot(final_df['observation_date'], final_df['diff_hist'], color='#2563EB', marker='o', label='Historical Model')
ax.plot(final_df['observation_date'], final_df['diff_trad'], color='#DC2626', marker='s', label='Traditional Model')
ax.axhline(0, color='#555555', linewidth=0.8, linestyle='--')
ax.set_ylim(-100000, 25000)
ax.set_xlim(final_df['observation_date'].min() - pd.Timedelta(days=10),
            final_df['observation_date'].max() + pd.Timedelta(days=10))
ax.set_xticks(final_df['observation_date'])
ax.set_xticklabels([d.strftime('%b') for d in final_df['observation_date']],
                    fontfamily='Calibri', fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
for label in ax.get_yticklabels():
    label.set_fontfamily('Calibri')
    label.set_fontweight('bold')
ax.set_title('2025 Run Rate Difference from Actual, Traditional versus Historical Model (Millions of Dollars)',
             fontfamily='Calibri', fontweight='bold', fontsize=13, color='#1a1a1a')
ax.set_xlabel('2025', fontfamily='Calibri', fontweight='bold', fontsize=11)
ax.set_ylabel('Projected - Actual EOY Revenue Difference (Millions of Dollars)', fontfamily='Calibri', fontweight='bold', fontsize=10)
legend = ax.legend(prop={'family': 'Calibri', 'weight': 'bold'})
legend.get_frame().set_visible(False)
ax.spines[['top', 'right']].set_visible(False)
y_total = 125000
ax.axvspan(pd.Timestamp(final_df[final_df['observation_date'].dt.month == 8]['observation_date'].values[0]) - pd.Timedelta(days=12),
           pd.Timestamp(final_df[final_df['observation_date'].dt.month == 12]['observation_date'].values[0]) + pd.Timedelta(days=12),
           ymin=((-2500 + 100000) / y_total),
           ymax=((5000 + 100000) / y_total),
           fill=False, edgecolor='#555555', linewidth=1.2, linestyle='--')

#Insert secondary chart with a more compaact y axis to better visualize convergence from August to December
inset = fig.add_axes([0.55, 0.27, 0.42, 0.36])
inset.set_facecolor('#D9D9D9')
zoom = final_df[final_df['observation_date'].dt.month >= 8]
inset.plot(zoom['observation_date'], zoom['diff_hist'], color='#2563EB', marker='o')
inset.plot(zoom['observation_date'], zoom['diff_trad'], color='#DC2626', marker='s')
inset.axhline(0, color='#555555', linewidth=0.8, linestyle='--')
inset.set_ylim(-2500, 5000)
inset.set_xticks(zoom['observation_date'])
inset.set_xticklabels([d.strftime('%b') for d in zoom['observation_date']],
                       fontfamily='Calibri', fontweight='bold', fontsize=9)
inset.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
for label in inset.get_yticklabels():
    label.set_fontfamily('Calibri')
    label.set_fontweight('bold')
    label.set_fontsize(9)
inset.spines[['top', 'right']].set_visible(False)
inset.spines[['left', 'bottom']].set_linewidth(0.8)
plt.tight_layout(pad=1.5)

plt.show()

final_df['closer'] = final_df.apply(
    lambda x: 'N/A' if abs(x['diff_hist']) == abs(x['diff_trad'])
    else ('Historical' if abs(x['diff_hist']) < abs(x['diff_trad']) else 'Traditional'), axis=1)
final_df['margin'] = final_df.apply(
    lambda x: 0 if x['closer'] == 'N/A'
    else abs(x['diff_trad']) - abs(x['diff_hist']), axis=1)

#Clean final output table and label which model was more accurate and by what margin for each month
summary = final_df[['observation_date', 'runrate_hist', 'diff_hist', 'runrate_trad', 'diff_trad', 'closer', 'margin']].copy()
summary.columns = ['Month', 'Hist Projection', 'Hist Diff', 'Trad Projection', 'Trad Diff', 'Closer Model', 'Margin']
summary['Month'] = summary['Month'].dt.strftime('%b')
for col in ['Hist Projection', 'Hist Diff', 'Trad Projection', 'Trad Diff', 'Margin']:
    summary[col] = summary[col].round(0).astype(int)
print(summary.to_string(index=False))