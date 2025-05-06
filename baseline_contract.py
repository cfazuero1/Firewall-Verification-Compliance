import csv
import json
import sys
import ipaddress
from collections import defaultdict

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

def load_ep_data(ep_data_file):
    """ Load IP addresses associated with endpoints from the EP_Data file. """
    ep_data = defaultdict(list)
    with open(ep_data_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            epg_name = row[4]  # Assuming EPG name is in the 5th column (index 4)
            ip_address = row[2]  # Assuming IP is in the 3rd column (index 2)
            ep_data[epg_name].append(ip_address)
    return ep_data

def find_matching_subnet(ip, subnets):
    """ Find and return the subnet that contains the IP address. """
    try:
        ip_addr = ipaddress.ip_address(ip)
        for subnet_str, subnet in subnets.items():
            if ip_addr in subnet:
                return subnet_str
    except ValueError:
        return ""  # Return an empty string if the IP address is invalid
    return ""

def search_ip_in_json(endpoint_name, json_data):
    """ Search the JSON data for the IP address in the parent fvAEPg, child fvCEp, attribute 'ip'. """
    for item in json_data['imdata']:
        if 'fvAEPg' in item:
            if item['fvAEPg']['attributes']['name'] == endpoint_name:
                for child in item['fvAEPg'].get('children', []):
                    if 'fvCEp' in child:
                        return child['fvCEp']['attributes'].get('ip', '')
    return ""

def determine_consumer_to_provider(global_consumers, global_providers, contract, preferred_group):
    """ Determine if the contract should be marked as 'yes' in the 'Consumer to Provider' column. """
    if preferred_group == "exclude" and contract in global_providers:
        return "yes"
    return "no"

def recheck_and_update_subnets_in_output_file(output_file_path, subnets):
    """ Recheck and update the 'Subnet' column if the IP belongs to a different subnet. """
    updated_rows = []
    
    with open(output_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ip_list = row['IP'].split(',')
            matched_subnet = ""
            for ip in ip_list:
                if ip:
                    matching_subnet = find_matching_subnet(ip, subnets)
                    if matching_subnet and not matched_subnet:
                        matched_subnet = matching_subnet
            row['Subnet'] = matched_subnet
            updated_rows.append(row)
    
    with open(output_file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python script.py <GSU_Baseline.csv> <GSU_contracts_with_filters_and_ports.csv> <EP_Data_2024_08_15-14_35.csv> <input.json>")
        sys.exit(1)

    baseline_file_path = sys.argv[1]
    contracts_file_path = sys.argv[2]
    ep_data_file = sys.argv[3]
    json_file_path = sys.argv[4]
    output_file_path = 'baseline_contracts.csv'

    subnets = load_data(baseline_file_path, is_subnet=True)
    contract_names = load_data(contracts_file_path, is_subnet=False)
    ep_data = load_ep_data(ep_data_file)  # Load the EP_Data

    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # To track all consumers and providers across all endpoints
    global_consumers = {}
    global_providers = {}

    # First pass to collect all consumers and providers
    for item in json_data['imdata']:
        if 'fvAEPg' in item:
            endpoint_name = item['fvAEPg']['attributes']['name']
            preferred_group = item['fvAEPg']['attributes'].get('prefGrMemb', '')

            for child in item['fvAEPg'].get('children', []):
                if 'fvRsCons' in child:
                    contract = child['fvRsCons']['attributes'].get('tnVzBrCPName', '')
                    global_consumers.setdefault(contract, []).append((endpoint_name, preferred_group))
                if 'fvRsProv' in child:
                    contract = child['fvRsProv']['attributes'].get('tnVzBrCPName', '')
                    global_providers.setdefault(contract, []).append((endpoint_name, preferred_group))

    # Second pass to determine baseline contract and write results
    with open(output_file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Endpoint Name', 'Type of Endpoint', 'Contract associated to Endpoint', 'Preferred Group', 'IP', 'Subnet', 'Consumer to Provider', 'IP in Baseline Subnet', 'Baseline Contract'])
        
        for item in json_data['imdata']:
            if 'fvAEPg' in item:
                endpoint_name = item['fvAEPg']['attributes']['name']
                preferred_group = item['fvAEPg']['attributes'].get('prefGrMemb', '')

                consumers = []
                providers = []

                for child in item['fvAEPg'].get('children', []):
                    if 'fvRsCons' in child:
                        contract = child['fvRsCons']['attributes'].get('tnVzBrCPName', '')
                        consumers.append(contract)
                    if 'fvRsProv' in child:
                        contract = child['fvRsProv']['attributes'].get('tnVzBrCPName', '')
                        providers.append(contract)

                # Determine "Consumer to Provider"
                consumer_to_provider = "no"
                for contract in consumers:
                    if contract in global_providers:
                        for prov_endpoint, prov_group in global_providers[contract]:
                            if prov_group == "exclude" and preferred_group == "exclude":
                                consumer_to_provider = "yes"
                                break

                for contract in providers:
                    if contract in global_consumers:
                        for cons_endpoint, cons_group in global_consumers[contract]:
                            if cons_group == "exclude" and preferred_group == "exclude":
                                consumer_to_provider = "yes"
                                break

                # Combine all IPs associated with the endpoint
                associated_ips = ep_data.get(endpoint_name, [])
                combined_ips = ','.join(associated_ips)

                # If no IPs are found, search in the JSON file
                if not combined_ips:
                    associated_ip = search_ip_in_json(endpoint_name, json_data)
                    combined_ips = associated_ip if associated_ip else ""

                # Find matching subnet for the associated IPs
                matching_subnet = ""
                for ip in associated_ips:
                    subnet = find_matching_subnet(ip, subnets)
                    if subnet and not matching_subnet:
                        matching_subnet = subnet

                # Determine "IP in Baseline Subnet"
                ip_in_baseline_subnet = "yes" if matching_subnet else "no"

                # Set "Baseline Contract" based on "IP in Baseline Subnet"
                baseline_contract = ip_in_baseline_subnet

                # Write Consumers
                for contract in consumers:
                    writer.writerow([endpoint_name, 'Consumer', contract, preferred_group, combined_ips, matching_subnet, consumer_to_provider, ip_in_baseline_subnet, baseline_contract])
                
                # Write Providers
                for contract in providers:
                    writer.writerow([endpoint_name, 'Provider', contract, preferred_group, combined_ips, matching_subnet, consumer_to_provider, ip_in_baseline_subnet, baseline_contract])

    print(f"File '{output_file_path}' has been generated.")

    # Recheck and update the subnets for all IPs in the output file
    recheck_and_update_subnets_in_output_file(output_file_path, subnets)
    print("Recheck and update of subnets completed.")
