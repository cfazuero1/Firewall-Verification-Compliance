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

---

## 📄 ACI GSU and NFV Contracts Verification

### Document Structure

#### ACI GSU Contracts

- **ACI GSU Contracts & Filters**: Extracted GSU contracts with the corresponding filters.
- **NPD 1.52 GSU Contracts**: Contracts from NPD 1.52.
- **Contracts that match NPD 1.52**: Contracts appearing in both ACI and NPD.
- **Missing**: Contracts in NPD but not in ACI.

#### ACI NFV Contracts

- **ACI NFV Contracts & Filters**: Extracted NFV contracts with filters.
- **NPD 1.52 Bowen-to-NFV Contracts**: Migrated from Bowen to NFV in NPD.
- **Contracts that match NPD 1.52**: Appears in both datasets.
- **Missing**: Present in NPD but not in ACI.

---

### ▶️ Run the Extraction Script

```bash
mv contracts_filters.txt contracts_filters.py
python contracts_filters.py gsu-contracts-out.json gsu-filters-out.json
python contracts_filters.py nfv-contracts-out.json nfv-filters-out.json

## 🌐 Interlink System Baseline Access Lists

The interlink system is baseline and located in the subnet: `172.31.40.16/28`  
**Host IP Range**: `172.31.40.17` – `172.31.40.30`

### Relevant Object Groups

```vbnet
object-group network OCTS_Gateway
 description OCTS Gateway Server
 network-object host 172.31.40.17

object-group network OCTS_NSW_Int
 description OCTS NSW Interlink
 network-object host 172.31.40.18

object-group network OCTS_VIC_Int
 description OCTS VIC Interlink
 network-object host 172.31.40.19

object-group network OCTS_OfficeSystem
 description OCTS Office System
 network-object host 172.31.40.20

