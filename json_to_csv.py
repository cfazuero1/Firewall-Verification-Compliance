import json
import csv
import sys

def json_to_csv(json_file):
    # Load JSON data
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Open CSV file for writing
    output_file = json_file.replace('.json', '.csv')
    with open(output_file, 'w', newline='') as csvfile:
        # Define CSV headers
        fieldnames = ['comment', 'policy', 'protocol', 'srcPort', 'srcCidr', 'destPort', 'destCidr', 'syslogEnabled']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write rules to CSV
        for rule in data.get('rules', []):
            # Ensure 'destPort' values are treated as text in Excel
            if 'destPort' in rule:
                rule['destPort'] = f'"{rule["destPort"]}"'
            writer.writerow(rule)
    
    print(f"CSV file '{output_file}' created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <json_file>")
    else:
        json_file = sys.argv[1]
        json_to_csv(json_file)
