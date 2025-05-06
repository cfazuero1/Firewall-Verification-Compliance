import csv
import sys

def compare_policies(file1_path, file2_path, output_file_path):
    # Read the first CSV and store policy names from the first column
    with open(file1_path, 'r', newline='') as file1:
        reader1 = csv.reader(file1)
        policies_file1 = [row[0] for row in reader1 if row]  # Extract policy names from first column

    # Open second CSV and find matches
    with open(file2_path, 'r', newline='') as file2, open(output_file_path, 'w', newline='') as output_file:
        reader2 = csv.reader(file2)
        writer = csv.writer(output_file)
        writer.writerow(['Index', 'Policy Name'])  # Write headers for output file

        for index, row in enumerate(reader2):
            if len(row) < 2:
                continue  # Skip rows that don't have at least 2 columns

            policy_file2 = row[1]  # Get policy name from the second column of the second file

            if policy_file2 in policies_file1:  # Check if policy from second file exists in first file
                writer.writerow([index, policy_file2])  # Write index and policy name to output file

    print(f"Output saved to {output_file_path}")

# Main function to handle arguments
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python compare_policies.py <file1.csv> <file2.csv> <output.csv>")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output_file = sys.argv[3]

    # Call the function with file paths provided as arguments
    compare_policies(file1, file2, output_file)
