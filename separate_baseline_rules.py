import csv
import ipaddress

# Function to load subnets from AWS_Baseline.csv
def load_subnets(subnets_file):
    subnets = []
    with open(subnets_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            subnet = row['Boundary'].strip()
            subnets.append(subnet)
    return subnets

# Function to load IP addresses and their names from AWS_export_objects_addresses.csv
def load_ips(addresses_file):
    ips = {}
    with open(addresses_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['\ufeff"Name"'].strip().replace('"', '')
            ip = row['Address'].strip()
            ips[name] = ip
    return ips

# Function to check if an IP address belongs to any subnet
def check_ip_in_subnets(ip, subnets):
    for subnet in subnets:
        try:
            # Check if the IP and subnet are compatible (IPv4 vs IPv6)
            if ipaddress.ip_network(ip, strict=False).subnet_of(ipaddress.ip_network(subnet)):
                return subnet
        except (ValueError, TypeError):  # Handle incompatible IP types or invalid IPs
            continue
    return None

# Function to generate the first output file for IPs and subnets
def generate_output(ips, subnets, output_file):
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'IP', 'Subnet'])
        for name, ip in ips.items():
            subnet = check_ip_in_subnets(ip, subnets)
            writer.writerow([name, ip, subnet if subnet else ""])

# Function to load address groups from AWS_address_groups.csv
def load_address_groups(address_groups_file):
    groups = []
    with open(address_groups_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            group_name = row['\ufeff"Name"'].strip().replace('"', '')
            addresses = row['Addresses'].strip().split(';')
            groups.append((group_name, addresses))
    return groups

# Function to generate the second output for groups and subnets
def generate_group_output(groups, ips, subnets, output_file_2):
    ip_to_subnet = {name: check_ip_in_subnets(ip, subnets) for name, ip in ips.items() if check_ip_in_subnets(ip, subnets)}
    
    with open(output_file_2, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Addresses', 'Subnet'])
        for group_name, addresses in groups:
            group_subnets = set()
            for address in addresses:
                subnet = ip_to_subnet.get(address, None)
                if subnet:
                    group_subnets.add(subnet)
            writer.writerow([group_name, ';'.join(addresses), ';'.join(group_subnets) if group_subnets else ""])

# Function to load extraction rules from AWS_Extraction.csv
def load_extraction_rules(extraction_file):
    rules = []
    with open(extraction_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule = row.copy()
            rule['Source Address'] = row['Source Address'].strip().split(';')
            rule['Destination Address'] = row['Destination Address'].strip().split(';')
            rules.append(rule)
    return rules

# Function to directly generate baseline_rules_filtered.csv without the IP column
def generate_extraction_output_filtered(rules, groups, ips, subnets, rows_file, output_file_filtered):
    ip_to_subnet = {name: check_ip_in_subnets(ip, subnets) for name, ip in ips.items() if check_ip_in_subnets(ip, subnets)}
    group_to_subnet = {group_name: ';'.join({ip_to_subnet.get(addr) for addr in addresses if ip_to_subnet.get(addr)}) 
                       for group_name, addresses in groups}

    rows_to_remove = []
    with open(rows_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('\ufeffrow', '').strip():
                rows_to_remove.append(int(row['\ufeffrow'].strip()))

    with open(output_file_filtered, 'w', newline='') as f:
        writer = csv.writer(f)
        headers = list(rules[0].keys()) + ['Subnet', 'Address or Group']
        writer.writerow(headers)
        print ('Dropping rules below:\n')
        for idx, rule in enumerate(rules):
            if idx + 2 in rows_to_remove:
                print ((idx+2), rule['\ufeffName'])
                continue  # Skip rows that are in rows_to_remove
            
            subnets_in_rule = set()
            addresses_or_groups = set()
            
            # Check for matches in Source and Destination Address
            for addr in rule['Source Address'] + rule['Destination Address']:
                if addr in ip_to_subnet and ip_to_subnet[addr]:
                    subnets_in_rule.add(ip_to_subnet[addr])
                    addresses_or_groups.add(addr)
                if addr in group_to_subnet and group_to_subnet[addr]:
                    subnets_in_rule.update(group_to_subnet[addr].split(';'))
                    addresses_or_groups.add(addr)

            # Write rule with the new columns, without IP column
            writer.writerow(list(rule.values()) + 
                            [';'.join(subnets_in_rule) if subnets_in_rule else "",
                             ';'.join(addresses_or_groups) if addresses_or_groups else ""])
        print ('')

# Main function to process all files and generate outputs
def main(AWS_rows_file, AWS_Extraction_file, AWS_address_groups_file, AWS_export_objects_addresses_file, AWS_Baseline_file):
    subnets = load_subnets(AWS_Baseline_file)
    ips = load_ips(AWS_export_objects_addresses_file)
    groups = load_address_groups(AWS_address_groups_file)
    
    # Generate the first output for individual IPs and subnets
    output_file_1 = 'addresses.csv'
    generate_output(ips, subnets, output_file_1)

    # Generate the second output for groups and subnets
    output_file_2 = 'addresses_groups.csv'
    generate_group_output(groups, ips, subnets, output_file_2)

    # Generate the third output directly as baseline_rules_filtered.csv without IP column
    rules = load_extraction_rules(AWS_Extraction_file)
    output_file_filtered = 'baseline_rules_filtered.csv'
    generate_extraction_output_filtered(rules, groups, ips, subnets, AWS_rows_file, output_file_filtered)

    print(f"Generated files: {output_file_1}, {output_file_2}, {output_file_filtered}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 6:
        print("Usage: script.py AWS_rows.csv AWS_Extraction.csv AWS_address_groups.csv AWS_export_objects_addresses.csv AWS_Baseline.csv")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
