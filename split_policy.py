import csv
import re
import sys

def split_text(value):
    # This regex will match the text before the first number and then the rest
    match = re.match(r"([^\d]*\d+)(.*)", value)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return value, ''  # Return the original value if no match is found

def process_csv(input_file, output_file):
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Skip header if present
        
        with open(output_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            # Write header
            writer.writerow(['NPD ID', 'Policy Name'])
            
            # Process each row
            for row in reader:
                if row:
                    first_column_value = row[0]
                    npd_id, policy_name = split_text(first_column_value)
                    writer.writerow([npd_id, policy_name])

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_csv_file> <output_csv_file>")
    else:
        input_csv_file = sys.argv[1]
        output_csv_file = sys.argv[2]
        process_csv(input_csv_file, output_csv_file)
