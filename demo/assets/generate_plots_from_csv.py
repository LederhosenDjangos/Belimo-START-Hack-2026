from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main():
    assets_dir = Path(__file__).resolve().parent

    actuator_csv = assets_dir / "actuator_position_window.csv"
    dp_csv = assets_dir / "delta_p.csv"
    dpdt_csv = assets_dir / "delta_p_derivative_bounds.csv"

    if not actuator_csv.exists() or not dp_csv.exists() or not dpdt_csv.exists():
        missing = [
            str(p.name)
            for p in [actuator_csv, dp_csv, dpdt_csv]
            if not p.exists()
        ]
        raise FileNotFoundError(
            f"Missing CSV file(s) in {assets_dir}: {', '.join(missing)}"
        )

    actuator_df = pd.read_csv(actuator_csv)
    dp_df = pd.read_csv(dp_csv)
    dpdt_df = pd.read_csv(dpdt_csv)

    fig1, ax1 = plt.subplots(figsize=(9, 4))
    if len(actuator_df.index) > 0:
        for series_name in actuator_df["series"].dropna().unique():
            series_df = actuator_df[actuator_df["series"] == series_name]
            ax1.plot(series_df["elapsed_s"], series_df["value"], label=series_name)
    ax1.set_xlabel("Time since Start d∆p/dt Example [s]")
    ax1.set_ylabel("position [%]")
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
    fig1.tight_layout()
    fig1.savefig(assets_dir / "actuator_position_window.png", dpi=150, bbox_inches="tight")
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(9, 4))
    if len(dp_df.index) > 0:
        ax2.plot(dp_df["elapsed_s"], dp_df["delta_p_bar"], color="orange")
    ax2.set_xlabel("Time since Start d∆p/dt Example [s]")
    ax2.set_ylabel("∆p [bar]")
    fig2.tight_layout()
    fig2.savefig(assets_dir / "delta_p.png", dpi=150, bbox_inches="tight")
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(9, 4))
    if len(dpdt_df.index) > 0:
        for series_name in dpdt_df["series"].dropna().unique():
            series_df = dpdt_df[dpdt_df["series"] == series_name]
            ax3.plot(series_df["elapsed_s"], series_df["value"], label=series_name)
    ax3.set_xlabel("Time since Start d∆p/dt Example [s]")
    ax3.set_ylabel("d∆p/dt [bar/s]")
    ax3.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
    fig3.tight_layout()
    fig3.savefig(assets_dir / "delta_p_derivative_bounds.png", dpi=150, bbox_inches="tight")
    plt.close(fig3)

    print(f"Saved plots to {assets_dir}")


if __name__ == "__main__":
    main()
