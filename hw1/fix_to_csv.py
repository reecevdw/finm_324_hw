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


