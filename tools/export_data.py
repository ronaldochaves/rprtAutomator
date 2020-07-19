# Standard imports
import csv


def dict_data_as_dict_rows(dict_data):
    num_rows = len(dict_data[list(dict_data.keys())[0]])
    data_rows = []
    for i in range(num_rows):
        row = {}
        for key in dict_data.keys():
            row[key] = dict_data[key][i]
        data_rows.append(row)
    return data_rows


def as_dict(dict_data, outfile_path):
    data_rows = dict_data_as_dict_rows(dict_data)
    with open(outfile_path, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=dict_data.keys(), quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)
