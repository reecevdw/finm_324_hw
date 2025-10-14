# Please create a program called fix_to_csv.py, which will require two parameters: --input_fix_file and --output_csv_file.


# This program will do the following:

# Parse FIX messages to extract relevant fields. In this assignment we are ignoring all messages other than:
# Limit orders being sent to the market - MsgType (35) = NewOrderSingle (D)
# Fills received on those orders (ignore partial fills) - MsgType (35) = ExecutionReport (8) and ExecType (150) = FILL (2) and OrderStatus (39) = FILLED (2) and OrdType (40) = LIMIT (2)
# For each "Fill" notification, look up corresponding New Order Single (this way you ignore unfilled orders or rejections)
# For each "Fill", output a line in csv which contains: ClOrdID (11), TransactTime (60) from the original order and the execution, Symbol (55), Side (54), OrderQty(38), LimitPrice (44), average execution price aka AvgPx (6), exchange/broker aka LastMkt (30)
# The output file will be in the following format. Please ensure the columns names are the same, the actual values may be different:
# OrderID,OrderTransactTime,ExecutionTransactTime,Symbol,Side,OrderQty,LimitPrice,AvgPx,LastMkt
# ID1542,20250910-08:00:00.377,20250910-08:00:00.509,YANG,1,27,23.700000,23.170000,ID1516
# ID1572,20250910-08:00:00.450,20250910-08:00:00.692,IREN,1,30,31.290000,31.290000,ID1516
# ID1632,20250910-08:00:00.747,20250910-08:00:00.982,DJT,2,53,16.910000,16.910000,ID1516
# ID1711,20250910-08:00:00.866,20250910-08:00:01.006,AMD,2,80,159.560000,160.110000,ID1516
# ID1732,20250910-08:00:00.920,20250910-08:00:01.042,SOFI,2,4,25.860000,25.890000,ID1516
# ID1770,20250910-08:00:00.983,20250910-08:00:01.156,WOLF,1,100,1.820000,1.800000,ID1516
# ID1815,20250910-08:00:01.147,20250910-08:00:01.264,YINN,2,100,50.200000,51.540000,ID1516
# ID1832,20250910-08:00:01.195,20250910-08:00:01.324,NIO,1,1,6.260000,6.030000,ID1516
# ID1836,20250910-08:00:01.196,20250910-08:00:01.334,NIO,1,1,6.260000,6.030000,ID1516
# ID1832,20250910-08:00:01.195,20250910-08:00:01.324,NIO,1,1,6.260000,6.030000,ID1517
# ID1836,20250910-08:00:01.196,20250910-08:00:01.334,NIO,1,1,6.260000,6.030000,ID1517

import argparse, csv
from decimal import Decimal, InvalidOperation

HEADER = [
    "OrderID","OrderTransactTime","ExecutionTransactTime",
    "Symbol","Side","OrderQty","LimitPrice","AvgPx","LastMkt",
]

def must_endwith(path, ext):
    if not path.lower().endswith(ext):
        raise argparse.ArgumentTypeError(f"{path} must end with {ext}")
    return path

def parse_line(line):
    """Return dict of FIX tag->value from 'ts : FIX' line. None if malformed."""
    if " : " not in line:
        return None
    _, msg = line.split(" : ", 1)
    msg = msg.strip().replace("^A", "\x01").rstrip("\x01$")  # support both SOH and literal ^A
    fields = {}
    for part in msg.split("\x01"):
        if "=" in part:
            k, v = part.split("=", 1)
            fields[k] = v
    return fields

def fmt6(x):
    if not x: return ""
    try:      return f"{Decimal(x):.6f}"
    except InvalidOperation:
        return x

if __name__ == "__main__":
    p = argparse.ArgumentParser(prog="fix_to_csv", description="Filled LIMIT orders to CSV")
    p.add_argument("--input_fix_file",  required=True, type=lambda s: must_endwith(s, ".fix"))
    p.add_argument("--output_csv_file", required=True, type=lambda s: must_endwith(s, ".csv"))
    args = p.parse_args()

    # Collect NewOrderSingle LIMIT (35=D & 40=2) by ClOrdID (11)
    orders = {}  # 11 -> {needed order fields}
    fills  = []  # list of fills (joined later)

    with open(args.input_fix_file, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            fields = parse_line(raw.rstrip("\n"))
            if not fields:
                continue

            mt = fields.get("35", "")

            # NewOrderSingle LIMIT
            if mt == "D" and fields.get("40") == "2":
                oid = fields.get("11", "")
                if oid:
                    orders[oid] = {
                        "OrderID": oid,
                        "OrderTransactTime": fields.get("60", ""),
                        "Symbol": fields.get("55", ""),
                        "Side": fields.get("54", ""),
                        "OrderQty": fields.get("38", ""),
                        "LimitPrice": fields.get("44", ""),
                    }

            # ExecutionReport full fill LIMIT (35=8, 150=2, 39=2, 40=2)
            elif mt == "8" and fields.get("150") == "2" and fields.get("39") == "2" and fields.get("40") == "2":
                oid = fields.get("11", "")
                if oid:
                    fills.append({
                        "OrderID": oid,
                        "ExecutionTransactTime": fields.get("60", ""),
                        "AvgPx": fields.get("6", ""),
                        "LastMkt": fields.get("30", ""),
                    })

    # Join fills to orders on ClOrdID (11) and write CSV
    out_rows, skipped = [], 0
    for fx in fills:
        o = orders.get(fx["OrderID"])
        if not o:
            skipped += 1
            continue
        out_rows.append({
            "OrderID": o["OrderID"],
            "OrderTransactTime": o["OrderTransactTime"],
            "ExecutionTransactTime": fx["ExecutionTransactTime"],
            "Symbol": o["Symbol"],
            "Side": o["Side"],
            "OrderQty": o["OrderQty"],
            "LimitPrice": fmt6(o["LimitPrice"]),
            "AvgPx": fmt6(fx["AvgPx"]),
            "LastMkt": fx["LastMkt"],
        })

    with open(args.output_csv_file, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=HEADER)
        w.writeheader(); w.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {args.output_csv_file}" +
          (f" (skipped {skipped} unmatched fills)" if skipped else ""))
