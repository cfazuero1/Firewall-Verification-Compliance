import json
import csv
import sys

def main(contracts_file, filters_file):
    # Load the JSON data
    with open(contracts_file) as f1:
        contracts_data = json.load(f1)

    # Load the filter data
    with open(filters_file) as f2:
        filters_data = json.load(f2)

    # Extract filter names and their dToPort values
    filter_dToPort_map = {}

    for filter_item in filters_data.get("imdata", []):
        vz_filter = filter_item.get("vzFilter", {})
        filter_name = vz_filter.get("attributes", {}).get("name", "")
        entries = vz_filter.get("children", [])

        # Collect dToPort values for this filter
        dToPorts = []
        for entry in entries:
            vz_entry = entry.get("vzEntry", {})
            dToPort = vz_entry.get("attributes", {}).get("dToPort", "")
            if dToPort == "unspecified":
                dToPort = filter_name  # Replace "unspecified" with filter name
            dToPorts.append(dToPort)

        if filter_name:
            filter_dToPort_map[filter_name] = ";".join(dToPorts)

    # Prepare CSV data
    csv_data = []
    for contract_item in contracts_data.get("imdata", []):
        # Extract attributes from vzBrCP
        contract_attr = contract_item.get("vzBrCP", {}).get("attributes", {})
        contract_name = contract_attr.get("name")
        contract_descr = contract_attr.get("descr", "")

        # Extract vzSubj name and filter names
        vz_subj_name = ""
        filter_names = []
        dToPort_values = []

        for child in contract_item.get("vzBrCP", {}).get("children", []):
            vz_subj = child.get("vzSubj", {})
            if vz_subj:
                vz_subj_attr = vz_subj.get("attributes", {})
                vz_subj_name = vz_subj_attr.get("name", "")

                # Extract tnVzFilterName from vzRsSubjFiltAtt
                for subj_child in vz_subj.get("children", []):
                    vz_rs_subj_filt_att = subj_child.get("vzRsSubjFiltAtt", {})
                    if vz_rs_subj_filt_att:
                        filt_attr = vz_rs_subj_filt_att.get("attributes", {})
                        tn_vz_filter_name = filt_attr.get("tnVzFilterName", "")
                        if tn_vz_filter_name:
                            filter_names.append(tn_vz_filter_name)
                            dToPort_values.append(filter_dToPort_map.get(tn_vz_filter_name, "permit-any"))

        # Join filter names and dToPort values with semicolons
        filter_names_str = ";".join(filter_names) if filter_names else "permit-any"
        dToPort_values_str = ";".join(dToPort_values) if dToPort_values else "permit-any"

        # Append the contract details to CSV data
        csv_data.append([contract_name, contract_descr, vz_subj_name, filter_names_str, dToPort_values_str])

    # Write to CSV
    output_file = 'contracts_with_filters_and_ports.csv'
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Contract Name', 'Description', 'vzSubj Name', 'Filter Names', 'dToPort Values'])
        writer.writerows(csv_data)

    print(f"CSV file '{output_file}' created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <contracts.json> <filters.json>")
        sys.exit(1)

    contracts_file = sys.argv[1]
    filters_file = sys.argv[2]

    main(contracts_file, filters_file)
