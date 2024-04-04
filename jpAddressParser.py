import csv
import re
import sys
from datetime import datetime

from normalize_japanese_addresses import normalize
from concurrent.futures import ProcessPoolExecutor


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
            data_list.append({'full_address': " ".join(row), 'work': " ".join(row)})
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

def replace_strings_with_space(addr: dict) -> dict:
    """Replace specified strings with space in the address."""
    strings_to_replace = [",", "ポストコード", "〒無し", "〒なし", "郵便番号"]  # Add any other strings you want to replace with space
    for string in strings_to_replace:
        addr['work'] = addr['work'].replace(string, " ")
    return addr

def extract_country(addr: dict) -> dict:
    """Extract country information from address."""
    exceptions = ['日本橋', '日本生命', '日本電機', '日本技術', '日本製鋼', '日本郵便', '日本株式会社']
    if '日本国' in addr['work']:
        addr['work'] = addr['work'].replace('日本国', '')
        addr['country'] = '日本国'
    elif '日本' in addr['work'] and not any(ex in addr['work'] for ex in exceptions):
        addr['work'] = addr['work'].replace('日本', '')
        addr['country'] = '日本'
    elif 'JP' in addr['work']:
        addr['work'] = addr['work'].replace('JP', '')
        addr['country'] = 'JP'
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
    if '郡' in city and city.index('郡') != 0:
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

def parse_building_name(work: list) -> tuple:
    """Parse and return the building name and floor."""
    work = " ".join(work[1:]) if len(work) > 0 else ""

    floor_number_pattern = r'(\d{1,2}階|\d{1,2}F)'  # Regular expression pattern for floor numbers
    match = re.search(floor_number_pattern, work)
    if match:
        floor_number = match.group().strip()
        building_name = re.sub(floor_number_pattern, '', work).strip()
    else:
        floor_number = None
        building_name = work if len(work) != 0 else None
    return building_name, floor_number

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
    addr['buildingName'], addr['floorNumber'] = parse_building_name(work)
    addr['roomNumber'] = None
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

    with ProcessPoolExecutor() as executor:
        rec = list(executor.map(replace_strings_with_space, rec))
        # Extract country
        rec = list(executor.map(extract_country, rec))
        # Extract postalcode
        rec = list(executor.map(extract_postalcode, rec))
        # process address
        rec = list(executor.map(parse_address, rec))

    # Export CSV
    export_csv(rec, file_path.rsplit(".", 1)[0] + "_parsed.csv")

    end_time = datetime.now()
    print(f"End Time: {end_time}")
    processing_time = end_time - start_time
    print(f"Processing Time: {processing_time}")
