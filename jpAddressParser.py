import csv
import re

from normalize_japanese_addresses import normalize


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
    parsed = normalize(addr['work'])
    addr['prefecture'] = parsed['pref']

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

    addr['neighborhood'] = parsed['town']
    addr['banch'] = parsed['addr']
    addr['go'] = parsed['addr']
    addr['buildingName'] = None
    addr['roomNumber'] = None
    addr['floorNumber'] = None
    del addr['work']

    return addr


if __name__ == "__main__":
    # CSV data import
    rec = import_csv("data/full_address.csv")
    # Extract country
    rec = [extract_country(r) for r in rec]
    # Extract postalcode
    rec = [extract_postalcode(r) for r in rec]
    # parse address
    rec = [parse_address(r) for r in rec]
    # Export CSV
    export_csv(rec, "data/parsed_address.csv")

