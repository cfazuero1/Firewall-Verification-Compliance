import csv
import sys

def normalize(text):
    """Helper function to clean and normalize text for matching."""
    return text.strip().lower()

def process_csv_files(file1_path, file2_path, output_file_path):
    # Read the two CSV files into lists of dictionaries
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        reader1 = csv.DictReader(file1)
        reader2 = csv.DictReader(file2)

        # Convert readers to lists for easier matching
        rows1 = list(reader1)
        rows2 = list(reader2)

    # Columns to match
    columns_to_match = ['Source Address', 'Destination Address', 'Service', 'Application', 'Source Zone', 'Destination Zone']
    columns_to_match_with_name = ['Name'] + columns_to_match

    # Prepare to store the paired rows
    paired_rows = []

    # Perform the matching manually
    for i, row1 in enumerate(rows1):
        for j, row2 in enumerate(rows2):
            # Check if the relevant columns match between the two rows
            if all(normalize(row1[col]) == normalize(row2[col]) for col in columns_to_match):
                # Store the row from file1 followed by the matching row from file2
                row_file1 = [row1[col] for col in columns_to_match_with_name] + [i + 1]
                row_file2 = [row2[col] for col in columns_to_match_with_name] + [j + 1]
                paired_rows.append(row_file1)
                paired_rows.append(row_file2)

    # Add the 'Document' column with alternating values 'Extraction' and 'NPD'
    for idx, row in enumerate(paired_rows):
        row.append('Extraction' if idx % 2 == 0 else 'NPD')

    # Write the paired rows to the output CSV
    with open(output_file_path, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        # Write header
        writer.writerow(columns_to_match_with_name + ['Row', 'Document'])
        # Write paired rows
        writer.writerows(paired_rows)

if __name__ == '__main__':
    # Ensure two input files are provided as arguments
    if len(sys.argv) != 3:
        print("Usage: python script_name.py NFV_Extraction.csv NFV_matches.csv")
        sys.exit(1)

    # Get the file paths from the command-line arguments
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    output_file_path = 'NFV_matched_rows_in_pairs_with_document.csv'

    # Call the processing function
    process_csv_files(file1_path, file2_path, output_file_path)

    print(f"Processed and saved output to {output_file_path}")
