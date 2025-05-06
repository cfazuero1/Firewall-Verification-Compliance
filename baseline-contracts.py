import csv
import json
import sys
import ipaddress

def load_data(file_path, is_subnet=True):
    """ Load data from a CSV file and return a dictionary for subnets or a set for contract names. """
    data = {} if is_subnet else set()
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        if is_subnet:
            for row in reader:
                try:
                    data[row['Boundary']] = ipaddress.ip_network(row['Boundary'])
                except ValueError as e:
                    print(f"Error processing network: {row['Boundary']} - {e}")
        else:
            for row in reader:
                data.add(row['Contract Name'])
    return data

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python script.py <GSU_Baseline.csv> <GSU_contracts_with_filters_and_ports.csv> <input.json>")
        sys.exit(1)

    baseline_file_path = sys.argv[1]
    contracts_file_path = sys.argv[2]
    json_file_path = sys.argv[3]
    output_file_path = 'baseline_contracts.csv'

    subnets = load_data(baseline_file_path, is_subnet=True)
    contract_names = load_data(contracts_file_path, is_subnet=False)

    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    with open(output_file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Contract Name', 'Endpoint Name', 'IP', 'MAC', 'Contract Name (fvRsCons)', 'Contract Name (fvRsProv)', 'Subnet', 'Match Contract (fvRsCons)', 'Match Contract (fvRsProv)', 'Baseline'])
        for item in json_data['imdata']:
            if 'fvAEPg' in item:
                endpoint_name = item['fvAEPg']['attributes']['name']
                for epg in item['fvAEPg'].get('children', []):
                    if 'fvCEp' in epg:
                        attributes = epg['fvCEp']['attributes']
                        ip_addr = attributes['ip']
                        fvCEp_mac = attributes['mac']
                        subnet_entry = ""
                        for subnet_str, subnet in subnets.items():
                            if ipaddress.ip_address(ip_addr) in subnet:
                                subnet_entry = subnet_str
                                break
                        tnVzBrCPName_fvRsCons = None
                        tnVzBrCPName_fvRsProv = None
                        contract_name = None
                        for rel in item['fvAEPg'].get('children', []):
                            if 'fvRsCons' in rel:
                                tnVzBrCPName_fvRsCons = rel['fvRsCons']['attributes'].get('tnVzBrCPName', None)
                            if 'fvRsProv' in rel:
                                tnVzBrCPName_fvRsProv = rel['fvRsProv']['attributes'].get('tnVzBrCPName', None)
                                contract_name = tnVzBrCPName_fvRsProv  # Assuming contract name comes from fvRsProv
                        match_contract_fvRsCons = "yes" if tnVzBrCPName_fvRsCons in contract_names else "no"
                        match_contract_fvRsProv = "yes" if tnVzBrCPName_fvRsProv in contract_names else "no"
                        baseline = "yes" if subnet_entry and match_contract_fvRsCons == "yes" and match_contract_fvRsProv == "yes" else "no"
                        writer.writerow([contract_name, endpoint_name, ip_addr, fvCEp_mac, tnVzBrCPName_fvRsCons, tnVzBrCPName_fvRsProv, subnet_entry, match_contract_fvRsCons, match_contract_fvRsProv, baseline])

    print(f"File '{output_file_path}' has been generated.")
