import re
import sys
from collections import defaultdict

def clean_pattern(pattern):
    # Remove special characters and spaces from the pattern
    return re.sub(r'[^\w]', '', pattern)

def main(patterns_file, target_file):
    try:
        # Open and read patterns from patterns_file
        with open(patterns_file, 'r') as pf:
            patterns = pf.readlines()

        # Open and read target_file
        with open(target_file, 'r') as tf:
            target_lines = tf.readlines()

        # Dictionary to keep count of each pattern
        pattern_counts = defaultdict(int)

        # Process each pattern
        for pattern in patterns:
            cleaned_pattern = clean_pattern(pattern.strip())

            if cleaned_pattern:
                # Count occurrences of the cleaned pattern in the target lines
                count = sum(cleaned_pattern in line for line in target_lines)
                pattern_counts[cleaned_pattern] += count

        # Print the counts
        for pattern, count in pattern_counts.items():
            print(f"Pattern: {pattern}, Count: {count}")

    except FileNotFoundError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py patterns.txt target_file.txt")
        sys.exit(1)

    patterns_file = sys.argv[1]
    target_file = sys.argv[2]

    main(patterns_file, target_file)
