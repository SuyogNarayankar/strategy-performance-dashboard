import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Creating the DataFrame from your provided data
data = {
    'Date': ['01 Aug 2024', '02 Aug 2024', '05 Aug 2024', '06 Aug 2024', '07 Aug 2024', '08 Aug 2024',
             '09 Aug 2024', '12 Aug 2024', '13 Aug 2024', '14 Aug 2024', '16 Aug 2024', '19 Aug 2024',
             '20 Aug 2024', '21 Aug 2024', '22 Aug 2024', '23 Aug 2024', '26 Aug 2024', '27 Aug 2024',
             '28 Aug 2024', '29 Aug 2024', '30 Aug 2024', '02 Sep 2024', '03 Sep 2024', '04 Sep 2024',
             '05 Sep 2024', '06 Sep 2024', '09 Sep 2024', '10 Sep 2024', '11 Sep 2024', '12 Sep 2024',
             '13 Sep 2024', '16 Sep 2024', '17 Sep 2024', '18 Sep 2024', '19 Sep 2024', '20 Sep 2024',
             '23 Sep 2024', '24 Sep 2024', '25 Sep 2024', '26 Sep 2024', '27 Sep 2024', '30 Sep 2024',
             '01 Oct 2024', '03 Oct 2024', '04 Oct 2024', '07 Oct 2024', '08 Oct 2024'],
    'Put': [-14407, 20415, 2272, 2287, 2347, 23340, 7620, 18630, -16927, 2452, 35032, 3180,
            6075, -11677, 8115, -2055, -4755, 19000, 14820, 3735, 8010, -1635, -12720, 16222,
            4522, -20137, 41167, 19245, 2947, 23497, 18682, -6757, 10177, 2272, -21030, 5392,
            17025, -13410, 15502, 12975, -4410, -5280, -7155, -1687, -4762, -8055, 25620],
    'Call': [16702, -19185, 15892, -14550, -5197, -10815, -1987, -15270, 22500, -6082, -14040, 5595,
             -2820, 1185, -1147, 4185, 9015, -9113, -2298, -75, -2947, -2820, -975, 997, -3172,
             20197, -8362, -8235, -817, -13785, -12465, 4080, -8092, -5122, 6495, -13418, -10972,
             9427, -2175, -3000, 18855, 14134, -1485, 31132, -23332, 7065, -13702],
}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'], format='%d %b %Y')
df.set_index('Date', inplace=True)


# Calculate Total P&L
df['Total'] = df['Put'] + df['Call']

# Calculate Cumulative P&L
df['Cumulative_Total'] = df['Total'].cumsum()
initial_capital = 1300000  # ₹13 lac
df['Cumulative_Total_on_Capital'] = initial_capital + df['Cumulative_Total']

# Calculate Cumulative P&L for Call and Put
df['Cumulative_Call'] = df['Call'].cumsum()
df['Cumulative_Put'] = df['Put'].cumsum()

# Calculate Maximum Drawdown
df['Cumulative_Max'] = df['Cumulative_Total'].cummax()
df['Drawdown'] = df['Cumulative_Total'] - df['Cumulative_Max']
max_dd = df['Drawdown'].min()
max_dd_date = df['Drawdown'].idxmin()

# Insights
total_profit_loss = df['Total'].sum()
best_trading_day = df['Total'].idxmax()
worst_trading_day = df['Total'].idxmin()
average_daily_profit_loss = df['Total'].mean()
average_call = df['Call'].mean()
average_put = df['Put'].mean()
total_days_in_profit = (df['Total'] > 0).sum()
total_days_in_loss = (df['Total'] < 0).sum()
volatility = df['Total'].std()
winning_percentage = (total_days_in_profit / len(df)) * 100
drawdown_duration = (df['Drawdown'] < 0).astype(int).groupby((df['Drawdown'] >= 0).astype(int).cumsum()).cumsum().max()
max_consecutive_winning_days = (df['Total'] > 0).astype(int).groupby((df['Total'] <= 0).cumsum()).cumsum().max()
max_consecutive_losing_days = (df['Total'] < 0).astype(int).groupby((df['Total'] >= 0).cumsum()).cumsum().max()
capital_at_risk = (max_dd / initial_capital) * 100
sharpe_ratio = (df['Total'].mean() / df['Total'].std()) * np.sqrt(252)
downside_returns = df['Total'][df['Total'] < 0]
sortino_ratio = (df['Total'].mean() / downside_returns.std()) * np.sqrt(252) if not downside_returns.empty else np.nan
calmar_ratio = (df['Cumulative_Total'].iloc[-1] / abs(max_dd)) if max_dd < 0 else np.nan
days_to_recover = abs((df.index[df['Cumulative_Total'] >= df['Cumulative_Total'].loc[max_dd_date]].min() - max_dd_date).days)

# Create plots with enhanced aesthetics
def create_figure(title, x, y, name, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=name, line=dict(color=color)))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Amount (Rs)',
                      template='plotly', plot_bgcolor='rgba(255, 255, 255, 1)', 
                      yaxis=dict(tickformat=',', showgrid=True, zeroline=True))
    return fig

# Create a bar chart for the Daily Total P&L (not cumulative) with colors for profit/loss
def create_bar_chart_with_colors(title, x, y):
    colors = ['green' if val > 0 else 'red' for val in y]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y, marker_color=colors, name='Daily Total P&L'))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='P&L (Rs)', 
                      template='plotly', plot_bgcolor='rgba(255, 255, 255, 1)', 
                      yaxis=dict(tickformat=',', showgrid=True, zeroline=True))
    return fig

# Ensure only trading days are considered (already done by the data, as non-trading days are not included)

# Function to create a bar chart for Call and Put P&L separately
def create_separate_bar_chart(title, x, y, name, color):
    fig = go.Figure()
    
    # Add the bars
    fig.add_trace(go.Bar(x=x, y=y, name=name, marker_color=color))

    # Update layout
    fig.update_layout(title=title,
                      xaxis_title='Date',
                      yaxis_title='P&L (Rs)',
                      template='plotly',
                      plot_bgcolor='rgba(255, 255, 255, 1)',
                      yaxis=dict(tickformat=',', showgrid=True, zeroline=True))
    
    return fig

# Create separate bar charts for Call and Put P&L
fig_call_pnl = create_separate_bar_chart(
    'Daily Call P&L',
    df.index,
    df['Call'],
    'Call P&L',
    'orange'
)

fig_put_pnl = create_separate_bar_chart(
    'Daily Put P&L',
    df.index,
    df['Put'],
    'Put P&L',
    'magenta'
)

# Create the bar chart for Daily Total P&L with green for profit and red for loss
fig6 = create_bar_chart_with_colors('Daily Total P&L (Profit: Green, Loss: Red)', df.index, df['Total'])


fig1 = create_figure('Cumulative Total on ₹13 Lac Capital', df.index, df['Cumulative_Total_on_Capital'], 
                     'Cumulative Total on ₹13 Lac Capital', 'blue')

fig2 = create_figure('Cumulative Total', df.index, df['Cumulative_Total'], 
                     'Cumulative Total', 'green')

fig3 = create_figure('Cumulative Total of Call Leg', df.index, df['Cumulative_Call'], 
                     'Cumulative Call Leg', 'orange')

fig4 = create_figure('Cumulative Total of Put Leg', df.index, df['Cumulative_Put'], 
                     'Cumulative Put Leg', 'magenta')

fig5 = create_figure('Maximum Drawdown', df.index, df['Drawdown'], 
                     'Maximum Drawdown', 'purple')


# Streamlit App Layout
st.title("Startegy Performance Dashboard")

# Display Charts
st.plotly_chart(fig2)
st.plotly_chart(fig6)
st.plotly_chart(fig_call_pnl)  # Bar chart for Call P&L
st.plotly_chart(fig_put_pnl)   # Bar chart for Put P&L
# st.plotly_chart(fig1)
st.plotly_chart(fig3)
st.plotly_chart(fig4)
st.plotly_chart(fig5)



# Display Insights
st.subheader("Insights")
insights = [
    f"**Total Profit/Loss:** ₹{total_profit_loss:.2f}",
    f"**Best Trading Day:** {best_trading_day.strftime('%d %b %Y')} with a profit of ₹{df['Total'].max():.2f}",
    f"**Worst Trading Day:** {worst_trading_day.strftime('%d %b %Y')} with a loss of ₹{df['Total'].min():.2f}",
    f"**Average Daily Profit/Loss:** ₹{average_daily_profit_loss:.2f}",
    f"**Average Profit for Call Leg:** ₹{average_call:.2f}",
    f"**Average Profit for Put Leg:** ₹{average_put:.2f}",
    f"**Total Days in Profit:** {total_days_in_profit}",
    f"**Total Days in Loss:** {total_days_in_loss}",
    f"**Volatility (Std Dev of Returns):** ₹{volatility:.2f}",
    f"**Winning Percentage:** {winning_percentage:.2f}%",
    f"**Drawdown Duration:** {drawdown_duration} days",
    f"**Max Consecutive Winning Days:** {max_consecutive_winning_days}",
    f"**Max Consecutive Losing Days:** {max_consecutive_losing_days}",
    f"**Capital at Risk (Max Drawdown):** {capital_at_risk:.2f}%",
    f"**Sharpe Ratio:** {sharpe_ratio:.2f}",
    f"**Sortino Ratio:** {sortino_ratio:.2f}",
    f"**Calmar Ratio:** {calmar_ratio:.2f}",
    f"**Days to Recover from Max Drawdown:** {days_to_recover} days"
]

for insight in insights:
    st.write(insight)
