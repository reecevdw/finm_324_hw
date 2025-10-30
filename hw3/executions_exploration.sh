#!/bin/bash

# 1
wc -l /opt/assignment3/executions.csv > ~/finm_324_hw/hw3/a3_line_count.txt

# 2
wc -l /opt/assignment1/trading.fix >> ~/finm_324_hw/hw3/a3_line_count.txt

# 3
grep MSFT /opt/assignment3/executions.csv | head -n 10 > ~/finm_324_hw/hw3/a3_msft_count.txt

# 4
grep MSFT /opt/assignment1/trading.fix | head -n 10 >> ~/finm_324_hw/hw3/a3_msft_count.txt

# 5
cut -d',' -f4 /opt/assignment3/executions.csv | sort | uniq > ~/finm_324_hw/hw3/a3_unique_symbols.txt

# 6
cut -d',' -f4 /opt/assignment3/executions.csv | sort | uniq -c > ~/finm_324_hw/hw3/a3_symbols_count.txt

# 7
cut -d',' -f4 /opt/assignment3/executions.csv | grep NVDA > ~/finm_324_hw/hw3/a3_only_nvda.txt

# 8
cut -d',' -f4 /opt/assignment3/executions.csv | grep -v NVDA > ~/finm_324_hw/hw3/a3_all_except_nvda.txt