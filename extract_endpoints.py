import csv
import json
import sys

def load_json_data(file_path):
    """ Load JSON data from a file. """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_contract_names(file_path):
    """ Load contract names from the provided CSV file. """
    contracts = set()
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contracts.add(row['Contract Name'])  # Adjusting for the correct column name
    return contracts

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_endpoints.py <input.json> <contracts.csv>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    contracts_csv_path = sys.argv[2]

    json_data = load_json_data(json_file_path)
    contract_names = load_contract_names(contracts_csv_path)

    endpoints = []
    # Iterate through the data to extract endpoints and check contracts
    for item in json_data['imdata']:
        if 'fvAEPg' in item:
            endpoint_name = item['fvAEPg']['attributes']['name']
            matched_contracts = []
            tnVzBrCPName_fvRsCons = None
            tnVzBrCPName_fvRsProv = None
            for child in item['fvAEPg'].get('children', []):
                if 'fvRsCons' in child:
                    tnVzBrCPName_fvRsCons = child['fvRsCons']['attributes'].get('tnVzBrCPName', None)
                    if tnVzBrCPName_fvRsCons and tnVzBrCPName_fvRsCons in contract_names:
                        matched_contracts.append(tnVzBrCPName_fvRsCons)
                if 'fvRsProv' in child:
                    tnVzBrCPName_fvRsProv = child['fvRsProv']['attributes'].get('tnVzBrCPName', None)
                    if tnVzBrCPName_fvRsProv and tnVzBrCPName_fvRsProv in contract_names:
                        matched_contracts.append(tnVzBrCPName_fvRsProv)
            if matched_contracts:
                endpoints.append((endpoint_name, ', '.join(set(matched_contracts)), tnVzBrCPName_fvRsCons, tnVzBrCPName_fvRsProv))

    # Write results to a CSV file
    output_file_path = 'matched_endpoints.csv'
    with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Endpoint Name', 'Matched Contracts', 'tnVzBrCPName (fvRsCons)', 'tnVzBrCPName (fvRsProv)'])
        for endpoint, contracts, tnVzBrCPName_fvRsCons, tnVzBrCPName_fvRsProv in endpoints:
            writer.writerow([endpoint, contracts, tnVzBrCPName_fvRsCons, tnVzBrCPName_fvRsProv])

    print(f"File '{output_file_path}' has been generated with the matched endpoints and their associated contracts.")

