import csv
import re
import sys

from normalize_japanese_addresses import normalize


def check_arguments():
    """Check if command-line arguments are properly specified."""
    if len(sys.argv) < 2:
        print("File path is not specified.")
        sys.exit(1)
    return sys.argv[1]

def import_csv(file_path: str) -> list:
    """ Read a CSV file from the path and return a list of dictionaries """
    data_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
                data_list.append({'full_address': row[0], 'work': row[0]})
    return data_list

def export_csv(data: list, file_path: str):
    try:
        header = [*data[0].keys()]
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_country(addr: dict) -> dict:
    if '日本' in addr['work']:
        addr['work'] = addr['work'].replace('日本', '')
        addr['country'] = '日本'
    else:
        addr['country'] = None
    return addr

def extract_postalcode(addr: dict) -> dict:
    postal_code_pattern = r'(〒?\d{3}-\d{4}|〒?\d{7})'

    match = re.search(postal_code_pattern, addr.get('work', ''))
    if match:
        postal_code = match.group()
        addr['work'] = re.sub(postal_code_pattern, '', addr['work'])
        addr['PostalCode'] = postal_code
    else:
        addr['PostalCode'] = None

    return addr

def parse_address(addr: dict) -> dict:
    work = addr['work'].split()
    parsed = normalize(work[0])
    # Prefecture
    addr['prefecture'] = parsed['pref']
    # County, city and ward
    county = None
    ward = None
    city = parsed['city']
    if '郡' in city:
        county = city.split('郡')[0] + '郡'
        city = city.split('郡')[-1]
    elif parsed['pref'] != '東京都' and '区' in city:
        ward = city.split('市')[1]
        city = city.split('市')[0] + '市'
    addr.update({'county': county, 'city': city, 'ward': ward})
    # Neighborhood
    chome = { 
            '一丁目': '1丁目',
            '二丁目': '2丁目',
            '三丁目': '3丁目',
            '四丁目': '4丁目',
            '五丁目': '5丁目',
            '六丁目': '6丁目',
            '七丁目': '7丁目',
            '八丁目': '8丁目',
            '九丁目': '9丁目',
            '十丁目': '10丁目'
    }
    kanji_chome_in_town = re.search('|'.join(list(chome.keys())), parsed['town'])
    numeric_chome_in_address = re.search('|'.join(list(chome.values())), addr['work'])
    if kanji_chome_in_town and numeric_chome_in_address:
        addr['neighborhood'] = parsed['town'].replace(kanji_chome_in_town.group(), numeric_chome_in_address.group())
    else:
        addr['neighborhood'] = parsed['town']
    # banch/go
    addr_split = parsed['addr'].split("-")
    addr['banch'] = addr_split[0]
    addr['go'] = " ".join(addr_split[1:]) if len(addr_split) > 0 else None
    # buildingName and others
    addr['buildingName'] = " ".join(work[1:]) if len(work) > 0 else None
    addr['roomNumber'] = None
    addr['floorNumber'] = None
    del addr['work']

    return addr


if __name__ == "__main__":
    # Check arguments
    file_path = check_arguments()
    # CSV data import
    rec = import_csv(file_path)
    # Extract country
    rec = [extract_country(r) for r in rec]
    # Extract postalcode
    rec = [extract_postalcode(r) for r in rec]
    # parse address
    rec = [parse_address(r) for r in rec]
    # Export CSV
    export_csv(rec, file_path.rsplit(".", 1)[0] + "_parsed.csv")
