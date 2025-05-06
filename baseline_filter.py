import csv
import argparse
import os
import sys

def filter_and_deduplicate_csv(csv_file_path, txt_file_path, output_csv_path='baseline_rows.csv'):
    """
    Filters rows from a CSV file based on a list of unique values from a text file,
    removes duplicate rows, and saves the result to a new CSV file.

    Parameters:
    - csv_file_path (str): Path to the input CSV file.
    - txt_file_path (str): Path to the text file containing unique values.
    - output_csv_path (str): Path to the output CSV file. Defaults to 'baseline_rows.csv'.
    """
    # Check if input files exist
    if not os.path.isfile(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' does not exist.")
        sys.exit(1)
    if not os.path.isfile(txt_file_path):
        print(f"Error: Text file '{txt_file_path}' does not exist.")
        sys.exit(1)

    # Load the list of unique values from the text file
    try:
        with open(txt_file_path, 'r') as file:
            unique_list = set(line.strip() for line in file if line.strip())
    except Exception as e:
        print(f"Error reading text file: {e}")
        sys.exit(1)

    # Read the CSV file and filter rows
    try:
        with open(csv_file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)  # Assuming the first row is the header
            filtered_rows = []
            seen_rows = set()

            for row in reader:
                if row[0] in unique_list:
                    row_tuple = tuple(row)
                    if row_tuple not in seen_rows:
                        seen_rows.add(row_tuple)
                        filtered_rows.append(row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    # Write the filtered and deduplicated rows to a new CSV file
    try:
        with open(output_csv_path, 'w', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header)  # Write the header
            writer.writerows(filtered_rows)
        print(f"Filtered and deduplicated CSV saved to: {output_csv_path}")
    except Exception as e:
        print(f"Error writing to output CSV file: {e}")
        sys.exit(1)

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Filter CSV rows based on a text file and remove duplicates.')
    parser.add_argument('csv_file', help='Path to the input CSV file.')
    parser.add_argument('text_file', help='Path to the text file containing unique values.')
    args = parser.parse_args()

    # Define the output file name
    output_file = 'baseline_rows.csv'

    # Call the filtering function
    filter_and_deduplicate_csv(args.csv_file, args.text_file, output_file)

if __name__ == "__main__":
    main()
