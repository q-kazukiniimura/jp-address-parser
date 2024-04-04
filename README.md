# Japanese Address Parser
This Python script is designed to parse Japanese address strings provided in a CSV file (`data/full_address.csv`). The parsed addresses are then exported to another CSV file (`data/parsed_address.csv`). The script consists of several functions to handle the import, parsing, and export processes.

## Usage:
1. Ensure that the `data/full_address.csv` file containing the address data is present.
2. Install requrired libraries below:
``` shell:
pip install normalize_japanese_addresses
```
3. Execute the script below:
```shell:
python jpAddressParser.py
```

## Parsed Category and Difinition
* country: The country, if explicitly provided in the address.
* postalCode: The postal code of the address, if provided.
* prefecture: The prefecture or administrative division (都 - to, 道 - dou, 府 - hu, 県 - ken) of Japan. 
* county: The group of local administrative area (郡 - gun) of Japan.
* city: The municipalities (市 - shi, 町 - cho/machi, 村 - son/mura) or special wards of Tokyo (区 - ku, 特別区) of Japan.
* ward: The ward (区 - ku) of Japan without special wards of Tokyo, if applicable.
* town: The town (町 - machi) or village (村 - mura), if applicable.
* neighborhood: The neighborhood or a specific area following a city
* banchi: The banchi (番地) number, representing a specific plot of land or building.
* go: The go (号) number, an additional identifier for a building or unit.
* buildingName: The name of the building, if provided.
* roomNumber: The room number, if provided.
* floorNumber: The floor number, if provided.

## Requirements:
* Python 3.x
* [normalize_japanese_addresses](https://pypi.org/project/normalize-japanese-addresses/)
* CSV file (`full_address.csv`) containing Japanese address data in the specified format.
