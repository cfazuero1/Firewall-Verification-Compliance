import csv
import ipaddress
import sys

# Ensure a CSV file argument is provided
if len(sys.argv) < 2:
    print("Usage: python script.py <csv_file>")
    sys.exit(1)

# Get the input file from the arguments
file_path = sys.argv[1]

# Function to check if the subnet is within the specified subnet or if it contains the target subnet
def check_subnet_in_range_corrected(source_or_dest, target_subnet):
    subnets = source_or_dest.split(";")
    for subnet in subnets:
        try:
            if subnet.strip().lower() == 'any':
                return 'Baseline'
            if ipaddress.IPv4Network(subnet.strip()).overlaps(ipaddress.IPv4Network(target_subnet)):
                return 'Baseline'
        except ValueError:
            continue
    return 'Non-Baseline'

# Define the target subnet
target_subnet = '10.96.0.0/13'

# Open the input CSV file and prepare for reading
with open(file_path, mode='r') as infile, open('meraki_baseline.csv', mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Read the header and append the new 'NPD' column
    header = next(reader)
    header.append('NPD')
    writer.writerow(header)

    # Process each row, checking Source and Destination against the target subnet
    for row in reader:
        source = row[1]  # Assuming 'Source' is in the second column
        destination = row[2]  # Assuming 'Destination' is in the third column
        
        # Check for Baseline condition in Source or Destination
        npd_value = check_subnet_in_range_corrected(source, target_subnet)
        if npd_value == 'Non-Baseline':
            npd_value = check_subnet_in_range_corrected(destination, target_subnet)
        
        # Append the NPD result and write the row to the output file
        row.append(npd_value)
        writer.writerow(row)

print("Output saved to meraki_baseline.csv")
