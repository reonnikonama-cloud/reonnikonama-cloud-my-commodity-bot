import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplfinance as mpf

def generate_chart_image(df: pd.DataFrame, output_filename: str = "chart.png") -> str:
    if df.empty or len(df) < 20:
        raise ValueError("チャート生成に必要なデータ数が不足しています。")

    plot_df = df.tail(50).copy()
    
    add_plots = []
    if "SMA20" in plot_df.columns:
        add_plots.append(mpf.make_addplot(plot_df["SMA20"], color="dodgerblue", width=1.0))
    if "SMA50" in plot_df.columns:
        add_plots.append(mpf.make_addplot(plot_df["SMA50"], color="orange", width=1.0))

    style = mpf.make_mpf_style(
        base_mpf_style='nightclouds',
        rc={'font.sans-serif': ['Arial', 'Dejavu Sans']}
    )
    
    fig, _ = mpf.plot(
        plot_df,
        type='candle',
        addplot=add_plots,
        volume=True,
        panel_ratios=(3, 1),
        figsize=(10, 6),
        style=style,
        returnfig=True
    )
    
    fig.savefig(output_filename, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return output_filename
