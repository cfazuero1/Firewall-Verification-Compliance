import csv
import sys

# Function to load Security Zones from GSU_Baseline_Subnet_Zone.csv
def load_security_zones(zones_file):
    security_zones = set()  # Use a set for faster lookup
    with open(zones_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            security_zones.add(row['Security Zone'].strip())
    return security_zones

# Function to parse comma-separated values
def parse_comma_separated_values(value_string):
    return [item.strip() for item in value_string.split(',')] if value_string else []

# Function to parse addresses (comma-separated inside brackets)
def parse_addresses(address_string):
    # Remove brackets if present and split by commas
    address_string = address_string.strip().strip('[]')
    return [item.strip().replace("'", "") for item in address_string.split(',')]

# Function to modify the rules based on zones and addresses
def modify_rules(rules_file, zones_file, output_file):
    security_zones = load_security_zones(zones_file)

    with open(rules_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # Parse the Source Zone and Destination Zone (comma-separated values)
            source_zones = parse_comma_separated_values(row['Source Zone'])
            destination_zones = parse_comma_separated_values(row['Destination Zone'])

            # Parse the Source Address and Destination Address (comma-separated inside brackets)
            source_addresses = parse_addresses(row['Source Address'])
            destination_addresses = parse_addresses(row['Destination Address'])

            # Convert source_addresses and destination_addresses into semicolon-separated strings
            row['Source Address'] = ';'.join(source_addresses)
            row['Destination Address'] = ';'.join(destination_addresses)

            # Initialize the columns Subnet and Address or Group
            row['Subnet'] = row.get('Subnet', '')
            row['Address or Group'] = row.get('Address or Group', '')

            # Check Source Zone matches
            for zone in source_zones:
                if zone.strip() in security_zones or zone.strip().lower() == 'any':  # Check for security zone match or 'any'
                    if any(('any' == addr.replace("'", "").lower() or 'rfc-1918' in addr.lower()) and not '[negate]' in addr.lower() for addr in source_addresses):
                        row['Subnet'] = 'Any Baseline'
                        row['Address or Group'] = 'Any Baseline'
                    elif any('[negate] rfc-1918' in addr.lower() for addr in source_addresses):
                        row['Subnet'] = 'Negate'
                        row['Address or Group'] = 'Negate'

            # Check Destination Zone matches
            for zone in destination_zones:
                if zone.strip() in security_zones or zone.strip().lower() == 'any':  # Check for security zone match or 'any'
                    if any(('any' == addr.replace("'", "").lower() or 'rfc-1918' in addr.lower()) and not '[negate]' in addr.lower() for addr in destination_addresses):
                        row['Subnet'] = 'Any Baseline'
                        row['Address or Group'] = 'Any Baseline'
                    elif any('[negate] rfc-1918' in addr.lower() for addr in destination_addresses):
                        row['Subnet'] = 'Negate'
                        row['Address or Group'] = 'Negate'

            # Write updated row to output file
            writer.writerow(row)

# Main function to handle arguments and call the modify_rules function
def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <GSU_baseline_rules_filtered.csv> <GSU_Baseline_Subnet_Zone.csv>")
        sys.exit(1)

    rules_file = sys.argv[1]
    zones_file = sys.argv[2]
    output_file = 'updated_baseline_rules_filtered.csv'  # Updated output file name

    modify_rules(rules_file, zones_file, output_file)
    print(f"Updated rules saved to {output_file}")

if __name__ == "__main__":
    main()

