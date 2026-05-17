## YEARLY RUN RATE MODEL COMPARISON

# Project Description

The purpose of this project is to demonstrate the predictive difference between a traditional model of projecting a periodic metric and a slightly more complex historical projection model 

# Data Source and Description

The source data for this project is sourced from the Federal Reserve Bank of St. Louis (FRED) from their report "Retail Sales: Building Materials and Supplies Dealers (MRTSSM4441USN)". At the time of download, this report had last been updated on 3/14/2026. The data is total sales aggregated by month from January 1992 to present, reported in Millions of dollars.

This source was chosen for this demonstration due to the notable seasonality of the reported industry, a deliberatly extreme example to showcase the limitations of traditional prediction models. 

# Model Descriptions

*Traditional Model* 

The traditional model predicts period totals by assuming linear growth throughout the period. This is a simpler prediction calculation -- for each grain, the period to-date sum is found for the projected metric, divided by the elapsed grain count, and multiplied by the total number of grains in the period. 

In the example of this project, you would project the year's revenue thusly;

        **([Year to-date Sales] / [Month Number]) * 12**

*Historical Model*

The historical model predicts period totals using historical grain trends to specifically account for seasonality and regular cycles in periods. These calculations are slightly more complex than the traditional model and rely on historic data being present. For each row in the dataset the period to-date sum is calculated as a percent of the actual period sum, then averaged accross all same-grains in the data set. The average can then be extrapolated by dividing a grain's period to-date sum by the average period total percent.

In the example of this project, you would project the year's revenue thusly;

        **[Year to-date Sales] / (Average of ([Year to-date Sales] / [Actual Yearly Sales]) for each month)**

# Project Findings

As expected, the historical model is exceptionally more accurate more quickly than the traditional model. December is negligible as both models are exact because of the math behind the predictions, and of the 11 months the historical model projected more accurately in 10 instances.

The traditional model shows pretty clearly its shortfall in seasonal contexts; after January it undershot projections by $72.7B, February (the slowest month in this industry) had this model shooting $80B short of actual. This model then quickly corrects as the more busy summer months shift the YTD sales, but in the last 6 months we can observe the heavier summer months cause an over correction, and by October the model was predicting $4.5B over actual.

The historical model begins much more accurately as it can account for the fact that winter months are slow and to compensate for the lower sales in those months. As the summer months are calculated, it is able to correctly hold back from over compensating like the traditional model would.

Another important trend to note is the ability to converge to 0 difference for each model. The historical model increases the difference from actual MoM 2 times (in April and November), where the traditional model increases the difference MoM 4 times (in February, August, September, and October). This is a direct effect of the over correcting from the busy summer months.

In conclusion, the historical model is more consistent, accurate, and reliable than a traditional model for metric projection in seasonal periods.

```
Month  Hist Projection  Hist Diff  Trad Projection  Trad Diff Closer Model  Margin
  Jan           429593      13736           343152     -72705   Historical   58969
  Feb           424048       8191           335898     -79959   Historical   71768
  Mar           422376       6519           359784     -56073   Historical   49554
  Apr           425886      10029           384177     -31680   Historical   21651
  May           422941       7084           402101     -13756   Historical    6672
  Jun           419451       3594           410400      -5457   Historical    1863
  Jul           419310       3453           416343        486  Traditional   -2967
  Aug           416643        786           417567       1710   Historical     924
  Sep           416197        340           417969       2112   Historical    1773
  Oct           416386        529           420325       4468   Historical    3940
  Nov           415168       -689           418067       2210   Historical    1521
  Dec           415857          0           415857          0          N/A       0
```

# How to Run The Code

Running the code will provide a pop-out window showing a matplotlib chart of a time series for 2025 projections as difference from actual for each model, with a zoomed in secondary graph for August-December as both models converge to a smaller scale.

The final dataframe shown above also prints to the terminal.