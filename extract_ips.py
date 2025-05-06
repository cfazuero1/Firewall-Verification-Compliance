import json
import sys

def load_json_data(file_path):
    """ Load JSON data from a file. """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def find_ip_addresses(json_data):
    """ Extract and print IP addresses from the JSON data. """
    ip_addresses = []
    for item in json_data['imdata']:
        if 'fvAEPg' in item:
            for child in item['fvAEPg'].get('children', []):
                if 'fvCEp' in child and 'ip' in child['fvCEp']['attributes']:
                    ip_address = child['fvCEp']['attributes']['ip']
                    ip_addresses.append(ip_address)
    return ip_addresses

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python extract_ips.py <input.json>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    json_data = load_json_data(json_file_path)
    ip_addresses = find_ip_addresses(json_data)

    if ip_addresses:
        print("Found IP addresses:")
        for ip in ip_addresses:
            print(ip)
    else:
        print("No IP addresses found in the JSON file.")
