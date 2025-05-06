# VGCCC Firewall Compliance Verification Suite

This repository contains a suite of Python scripts developed to ensure compliance between firewall configurations and the Network Policy Document (NPD) for the **Victorian Gambling and Casino Control Commission (VGCCC)** Wagering and Gambling Standard (WBS).  
The primary objective is to verify that the implemented firewall rules and network contracts align with the documented policies, identifying any discrepancies or undocumented rules.

---

## 🔍 Baseline Palo Alto Rules Verification

Files named `[Data Centre]_rows.csv` contain the row numbers from each corresponding `[Data Centre]_Extraction.csv` file. These rows represent rules that have been discarded due to either a match or a mismatch.

These rows correspond to the master document:  
**Palo Alto Verification v6.xlsx**

### 🔧 How to Run

```bash
python3 separate_baseline_rules.py GSU_rows.csv GSU_Extraction.csv GSU_address_groups.csv GSU_export_objects_addresses.csv GSU_Baseline.csv
python3 separate_baseline_rules.py AWS_rows.csv AWS_Extraction.csv AWS_address_groups.csv AWS_export_objects_addresses.csv AWS_Baseline.csv
python3 separate_baseline_rules.py EMP_rows.csv EMP_Extraction.csv EMP_address_groups.csv EMP_export_objects_addresses.csv EMP_Baseline.csv
python3 separate_baseline_rules.py NB2_rows.csv NB2_Extraction.csv NB2_address_groups.csv NB2_export_objects_addresses.csv NB2_Baseline.csv
python3 separate_baseline_rules.py NFV_rows.csv NFV_Extraction.csv NFV_address_groups.csv NFV_export_objects_addresses.csv NFV_Baseline.csv

This will generate a file called `baseline_rules_filtered.csv` that contains the subnet(s) associated with each rule.

