import os
import sys
import csv

def read_csv(file_path):
    """
    Read CSV file and return a list of dictionaries representing each row.
    """
    data = []
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return data

def analyze_policy_files(npd_changes, zone_data, policy_folder):
    """
    Analyze each policy file in the folder and compare it with the NPD changes and Zone data.
    """
    results = []

    for policy_file in os.listdir(policy_folder):
        if policy_file.endswith(".csv"):
            policy_path = os.path.join(policy_folder, policy_file)
            policy_data = read_csv(policy_path)

            # Extract tech sep and change number from the filename
            parts = policy_file.split(' ')
            tech_sep = parts[2]
            change_number = parts[3].replace('.csv', '')

            # Find corresponding NPD change
            matching_change = None
            for change in npd_changes:
                if change['Tech Sep'] == tech_sep and change['Change Number'] == change_number:
                    matching_change = change
                    break
            
            if not matching_change:
                continue

            # Extract NPD change details
            npd_source_zone = matching_change['Source Zone']
            npd_dest_zone = matching_change['Destination Zone']
            npd_service = matching_change['Service']
            change_history_number = matching_change['Change History#']

            # Analyze each policy entry
            for policy in policy_data:
                policy_source_zones = [zone.strip().lower() for zone in policy['Source Zone'].split(',')]
                policy_dest_zones = [zone.strip().lower() for zone in policy['Destination Zone'].split(',')]
                policy_service = policy['Service'].lower()

                # Check source zone match
                source_zone_match = "Not Found"
                for source_zone in policy_source_zones:
                    for zone in zone_data:
                        if source_zone == zone['Firewall Zone'].lower() and zone['NPD Zone'].lower() == npd_source_zone.lower():
                            source_zone_match = "Matched"
                            break
                    if source_zone_match == "Matched":
                        break

                # Check destination zone match
                dest_zone_match = "Not Found"
                for dest_zone in policy_dest_zones:
                    for zone in zone_data:
                        if dest_zone == zone['Firewall Zone'].lower() and zone['NPD Zone'].lower() == npd_dest_zone.lower():
                            dest_zone_match = "Matched"
                            break
                    if dest_zone_match == "Matched":
                        break

                # Check service match
                service_match = "Matched" if npd_service.lower() in policy_service else "Not Matched"

                results.append({
                    'Policy Name': policy['Name'],
                    'Source Zone Match': source_zone_match,
                    'Destination Zone Match': dest_zone_match,
                    'Service': policy['Service'],
                    'Service Match': service_match,
                    'Change Number': change_number,
                    'Change History#': change_history_number,
                    'Tech Sep': tech_sep
                })

    return results

def save_results(results, output_file):
    """
    Save the analysis results to a CSV file.
    """
    with open(output_file, mode='w', newline='') as file:
        fieldnames = [
            'Policy Name', 'Source Zone Match', 'Destination Zone Match',
            'Service', 'Service Match', 'Change Number', 'Change History#', 'Tech Sep'
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    # Check if correct arguments are provided
    if len(sys.argv) != 4:
        print("Usage: python analyze_policies.py <NPD_Changes_File> <Zone_File> <Policies_Folder>")
        sys.exit(1)

    # Read arguments
    npd_changes_file = sys.argv[1]
    zone_file = sys.argv[2]
    policies_folder = sys.argv[3]

    # Read input files
    npd_changes = read_csv(npd_changes_file)
    zone_data = read_csv(zone_file)

    # Analyze policies
    results = analyze_policy_files(npd_changes, zone_data, policies_folder)

    # Save results to a CSV file
    output_file = "policy_analysis_results.csv"
    save_results(results, output_file)

    print(f"Results saved to {output_file}")
