import json
import csv
import sys

def main(contracts_file):
    # Load the JSON data
    with open(contracts_file) as f1:
        contracts_data = json.load(f1)

    # Prepare CSV data
    csv_data = []
    for contract_item in contracts_data.get("imdata", []):
        contract_attr = contract_item.get("vzBrCP", {}).get("attributes", {})
        contract_name = contract_attr.get("name")
        contract_descr = contract_attr.get("descr", "")

        # Append the contract details to CSV data
        csv_data.append([contract_name, contract_descr])

    # Write to CSV
    output_file = 'contracts_only.csv'
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Contract Name', 'Description'])
        writer.writerows(csv_data)

    print(f"CSV file '{output_file}' created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <contracts.json>")
        sys.exit(1)

    contracts_file = sys.argv[1]

    main(contracts_file)
