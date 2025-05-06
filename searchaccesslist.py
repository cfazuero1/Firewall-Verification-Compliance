import sys
import csv
import ipaddress

def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def parse_object_groups(lines, subnet):
    object_groups = {}
    for line in lines:
        if line.strip() and not line.startswith('#'):
            parts = line.strip().split()
            if len(parts) >= 2:
                object_group_name = parts[1]
                ip_address = parts[2] if len(parts) > 2 else None

                # Only process if ip_address is present and valid
                if ip_address:
                    try:
                        ip_obj = ipaddress.ip_address(ip_address)
                        if ip_obj in ipaddress.ip_network(subnet):
                            object_groups[object_group_name] = ip_address
                    except ValueError:
                        # Skip invalid IP addresses
                        pass
                else:
                    object_groups[object_group_name] = 'No IP'
    return object_groups

def parse_access_lists(lines):
    access_lists = []
    for line in lines:
        if line.strip() and not line.startswith('#'):
            parts = line.strip().split()
            if 'object-group' in parts:
                object_groups = parts[parts.index('object-group') + 1:]
                command = ' '.join(parts)
                access_lists.append((object_groups, command))
    return access_lists

def process_data(object_groups, access_lists):
    results = []
    for obj_groups, command in access_lists:
        for obj_group in obj_groups:
            if obj_group in object_groups:
                # Remove IP Address from results
                results.append((obj_group, command))
    return results

def write_csv(results, file_path):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Object Group Name', 'Access List Command'])
        writer.writerows(results)

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py object-groups.txt access-lists.txt")
        sys.exit(1)

    object_groups_file = sys.argv[1]
    access_lists_file = sys.argv[2]

    subnet = '172.31.40.16/28'  # Define the subnet to filter by

    object_groups_lines = load_file(object_groups_file)
    access_lists_lines = load_file(access_lists_file)

    object_groups = parse_object_groups(object_groups_lines, subnet)
    access_lists = parse_access_lists(access_lists_lines)

    results = process_data(object_groups, access_lists)

    write_csv(results, 'access_list_data.csv')
    print("CSV file 'access_list_data.csv' has been created successfully.")

if __name__ == "__main__":
    main()
