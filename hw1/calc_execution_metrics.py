import argparse
import pandas as pd
import numpy as np

def must_endwith(path, ext):
    if not path.lower().endswith(ext):
        raise argparse.ArgumentTypeError(f"{path} must end with {ext}")
    return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="calc_execution_metrics",
        description="Compute per-exchange execution speed and price improvement from filled orders CSV."
    )
    parser.add_argument(
        "--input_csv_file",
        required=True,
        type=lambda s: must_endwith(s, ".csv"),
        help="Input CSV (from fix_to_csv.py)"
    )
    parser.add_argument(
        "--output_metrics_file",
        required=True,
        type=lambda s: must_endwith(s, ".csv"),
        help="Output CSV with metrics"
    )
    args = parser.parse_args()

    # Read CSV
    df = pd.read_csv(args.input_csv_file)

    # Ensure required columns exist
    required_cols = [
        "OrderID","OrderTransactTime","ExecutionTransactTime","Symbol",
        "Side","OrderQty","LimitPrice","AvgPx","LastMkt"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {missing}")

    # Parse datetimes (handles microseconds; coerce invalid)
    df["OrderTransactTime"] = pd.to_datetime(df["OrderTransactTime"], format="%Y%m%d-%H:%M:%S.%f", errors="coerce")
    df["ExecutionTransactTime"] = pd.to_datetime(df["ExecutionTransactTime"], format="%Y%m%d-%H:%M:%S.%f", errors="coerce")

    # Convert numerics
    df["Side"] = df["Side"].astype(str)  # keep as string '1'/'2'
    df["LimitPrice"] = pd.to_numeric(df["LimitPrice"], errors="coerce")
    df["AvgPx"] = pd.to_numeric(df["AvgPx"], errors="coerce")

    # Execution speed in seconds
    df["ExecSpeedSecs"] = (df["ExecutionTransactTime"] - df["OrderTransactTime"]).dt.total_seconds()

    # Price improvement (never negative):
    #  - Buy (Side==1): improvement = max(LimitPrice - AvgPx, 0)
    #  - Sell(Side==2): improvement = max(AvgPx - LimitPrice, 0)
    is_buy = df["Side"] == "1"
    is_sell = df["Side"] == "2"
    df["PriceImprovement"] = np.where(
        is_buy, df["LimitPrice"] - df["AvgPx"],
        np.where(is_sell, df["AvgPx"] - df["LimitPrice"], np.nan)
    )
    df["PriceImprovement"] = df["PriceImprovement"].clip(lower=0)

    # Drop rows where key fields are missing (cannot compute metrics)
    df = df.dropna(subset=["LastMkt", "ExecSpeedSecs", "PriceImprovement"])

    # Group by exchange/broker (LastMkt) and compute averages
    metrics = (
        df.groupby("LastMkt", dropna=False)
          .agg(
              AvgPriceImprovement=("PriceImprovement", "mean"),
              AvgExecSpeedSecs=("ExecSpeedSecs", "mean"),
          )
          .reset_index()
    )

    # Write output
    metrics.to_csv(args.output_metrics_file, index=False)

    print(f"Wrote metrics for {len(metrics)} exchanges to {args.output_metrics_file}")