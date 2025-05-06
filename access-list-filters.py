import sys
import csv

# Load the baseline data from the CSV file
def load_baseline_data(baseline_csv):
    baseline_data = {}
    with open(baseline_csv, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            baseline_data[row['Object Group']] = {
                'Nested Object Groups': row['Nested Object Groups'],
                'Baseline Subnet': row['Baseline Subnet']
            }
    return baseline_data

# Parse the access lists and check object groups against the baseline data
def parse_access_lists_with_baseline(access_lists_file, baseline_data, output_file):
    results = []
    with open(access_lists_file, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split()

            # Extract object groups that follow 'object-group'
            object_groups = []
            for i in range(len(parts)):
                if parts[i] == 'object-group' and i + 1 < len(parts):
                    object_groups.append(parts[i + 1])

            # Check if the object groups or their nested groups are baseline
            for obj_group in object_groups:
                if obj_group in baseline_data:
                    baseline_info = baseline_data[obj_group]
                    if baseline_info['Baseline Subnet'] == 'true':
                        results.append(line)
                        break
                    else:
                        # Check nested object groups
                        nested_groups = baseline_info['Nested Object Groups'].split(';')
                        if any(baseline_data.get(nested_group, {}).get('Baseline Subnet') == 'true' for nested_group in nested_groups):
                            results.append(line)
                            break

    # Write the results to the output CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Access List Command'])
        for result in results:
            writer.writerow([result])

# Main function to run the program with arguments
def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <access-lists.txt> <object_groups_with_baseline.csv>")
        sys.exit(1)

    access_lists_file = sys.argv[1]  # Input access lists file
    baseline_csv = sys.argv[2]  # Input CSV file with baseline data
    output_file = 'filtered_access_lists.csv'  # Output CSV file

    # Load the baseline data from the CSV file
    baseline_data = load_baseline_data(baseline_csv)

    # Parse access lists and check against baseline data
    parse_access_lists_with_baseline(access_lists_file, baseline_data, output_file)

    print(f"CSV file '{output_file}' has been created successfully.")

if __name__ == "__main__":
    main()
