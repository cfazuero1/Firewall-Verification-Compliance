import csv
import ipaddress
import sys

def load_subnets(file_path):
    """Load subnets from the GSU_Baseline.csv file."""
    subnets = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                subnet = ipaddress.ip_network(row['Boundary'])
                subnets[row['Boundary']] = subnet
            except ValueError as e:
                print(f"Error processing subnet: {row['Boundary']} - {e}")
    return subnets

def load_ep_data(file_path):
    """Load endpoint data from the EP_Data_2024_08_15-14_35.csv file."""
    ep_data = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            epg_name = row['EPG']
            ip_address = row['IP']
            ep_data[epg_name] = ip_address
    return ep_data

def find_matching_subnet(ip, subnets):
    """Find and return the subnet that contains the IP address."""
    try:
        ip_addr = ipaddress.ip_address(ip)
        for subnet_str, subnet in subnets.items():
            if ip_addr in subnet:
                return subnet_str
    except ValueError:
        return ""  # Return an empty string if the IP address is invalid
    return ""

def update_ip_and_subnet(ep_data, subnets, row):
    """Update the 'IP' and 'Subnet' fields based on the endpoint name and subnets."""
    endpoint_name = row['Endpoint Name']
    ip = ep_data.get(endpoint_name, "")
    subnet = find_matching_subnet(ip, subnets) if ip else ""
    row['IP'] = ip
    row['Subnet'] = subnet
    return row

def main(ep_data_file, baseline_file, contracts_file, output_file):
    subnets = load_subnets(baseline_file)
    ep_data = load_ep_data(ep_data_file)  # Load the EP_Data

    # Load the existing baseline contracts CSV file
    with open(contracts_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # Update the IP and Subnet columns in each row
    updated_rows = []
    for row in rows:
        updated_row = update_ip_and_subnet(ep_data, subnets, row)
        updated_rows.append(updated_row)

    # Write the updated rows back to a new CSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"File '{output_file}' has been generated.")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python script.py <EP_Data_2024_08_15-14_35.csv> <GSU_Baseline.csv> <GSU_baseline_contracts.csv> <output.csv>")
        sys.exit(1)

    ep_data_file = sys.argv[1]
    baseline_file = sys.argv[2]
    contracts_file = sys.argv[3]
    output_file = sys.argv[4]

    main(ep_data_file, baseline_file, contracts_file, output_file)
