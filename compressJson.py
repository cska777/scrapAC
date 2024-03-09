import json
import csv
import gzip
import shutil

def json_to_csv(input_file, output_file):
    with open(input_file, 'r') as json_file:
        data = json.load(json_file)

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def compress_file(input_file, output_file):
    with open(input_file, 'rb') as f_in:
        with gzip.open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

if __name__ == "__main__":
    input_json_file = 'allocine_top_movies.json'
    output_csv_file = 'films.csv'
    output_gzip_file = 'films.csv.gz'

    # Convert JSON to CSV
    json_to_csv(input_json_file, output_csv_file)

    # Compress CSV to gzip
    compress_file(output_csv_file, output_gzip_file)
