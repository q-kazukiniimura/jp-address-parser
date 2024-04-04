import csv
import re
import sys
from datetime import datetime

from normalize_japanese_addresses import normalize


def check_arguments():
    """Check if command-line arguments are properly specified."""
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    return sys.argv[1]

def import_csv(file_path: str) -> list:
    """Read a CSV file from the path and return a list of dictionaries."""
    data_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data_list.append({'full_address': row[0], 'work': row[0]})
    return data_list

def export_csv(data: list, file_path: str):
    """Write data to a CSV file."""
    try:
        header = data[0].keys()  # No need to cast to list
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_country(addr: dict) -> dict:
    """Extract country information from address."""
    exceptions = ['日本橋', '日本生命', '日本電機', '日本技術', '日本製鉄', '日本郵便', '日本株式会社']
    if '日本' in addr['work'] and not any(ex in addr['work'] for ex in exceptions):
        addr['work'] = addr['work'].replace('日本', '')
        addr['country'] = '日本'
    elif 'JP' in addr['work']:
        addr['work'] = addr['work'].replace('JP', '')
        addr['country'] = 'JP'
    elif '日本国' in addr['work']:
        addr['work'] = addr['work'].replace('日本国', '')
        addr['country'] = '日本国'
    else:
        addr['country'] = None
    return addr

def extract_postalcode(addr: dict) -> dict:
    """Extract postal code from address."""
    postal_code_pattern = r'(〒?\d{3}-\d{4}|〒?\d{7})'
    match = re.search(postal_code_pattern, addr.get('work', ''))
    if match:
        postal_code = match.group()
        addr['work'] = re.sub(postal_code_pattern, '', addr['work'])
        addr['PostalCode'] = postal_code
    else:
        addr['PostalCode'] = None
    return addr

def parse_prefecture(parsed_address: dict) -> str:
    """Parse and return the prefecture."""
    return parsed_address['pref']

def parse_county_city_ward(parsed_address: dict) -> tuple:
    """Parse and return the county, city, and ward."""
    city = parsed_address['city']
    # Avoiding the parsing of cities with a "郡" at the beginning, such as "郡山市".
    if '郡' in city and city.index('郡') == 0:
        county = city.split('郡')[0] + '郡'
        city = city.split('郡')[-1]
        return county, city, None
    elif parsed_address['pref'] != '東京都' and '区' in city:
        ward = city.split('市')[1]
        city = city.split('市')[0] + '市'
        return None, city, ward
    else:
        return None, city, None

def parse_neighborhood(parsed_address: dict, kanji_chome: str, numeric_chome: str) -> str:
    """Parse and return the neighborhood."""
    neighborhood = parsed_address['town']
    if kanji_chome and numeric_chome:
        neighborhood = neighborhood.replace(kanji_chome.group(), numeric_chome.group())
    return neighborhood

def parse_banch_go(parsed_address: dict) -> tuple:
    """Parse and return the banch and go."""
    addr_split = parsed_address['addr'].split("-")
    banch = addr_split[0]
    go = " ".join(addr_split[1:]) if len(addr_split) > 1 else None
    return banch, go

def parse_building_name(work: list) -> str:
    """Parse and return the building name."""
    return " ".join(work[1:]) if len(work) > 1 else None

def parse_address(addr: dict) -> dict:
    """Parse address details."""
    work = addr['work'].split()
    parsed_address = normalize(work[0])

    addr['prefecture'] = parse_prefecture(parsed_address)
    addr['county'], addr['city'], addr['ward'] = parse_county_city_ward(parsed_address)

    chome = {'一丁目': '1丁目', '二丁目': '2丁目', '三丁目': '3丁目', '四丁目': '4丁目',
             '五丁目': '5丁目', '六丁目': '6丁目', '七丁目': '7丁目', '八丁目': '8丁目',
             '九丁目': '9丁目', '十丁目': '10丁目'}
    kanji_chome_in_town = re.search('|'.join(list(chome.keys())), parsed_address['town'])
    numeric_chome_in_address = re.search('|'.join(list(chome.values())), addr['work'])
    addr['neighborhood'] = parse_neighborhood(parsed_address, kanji_chome_in_town, numeric_chome_in_address)

    addr['banch'], addr['go'] = parse_banch_go(parsed_address)
    addr['buildingName'] = parse_building_name(work)
    addr['roomNumber'] = None
    addr['floorNumber'] = None
    del addr['work']

    return addr

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Start Time: {start_time}")

    # Check arguments
    file_path = check_arguments()
    # CSV data import
    rec = import_csv(file_path)
    print(f"Records Processed: {len(rec)}")
    # Extract country
    rec = [extract_country(r) for r in rec]
    # Extract postalcode
    rec = [extract_postalcode(r) for r in rec]
    # parse address
    rec = [parse_address(r) for r in rec]
    # Export CSV
    export_csv(rec, file_path.rsplit(".", 1)[0] + "_parsed.csv")

    end_time = datetime.now()
    print(f"End Time: {end_time}")
    processing_time = end_time - start_time
    print(f"Processing Time: {processing_time}")
