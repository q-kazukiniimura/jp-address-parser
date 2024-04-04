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

## Requirements:
* Python 3.x
* [normalize_japanese_addresses](https://pypi.org/project/normalize-japanese-addresses/)
* CSV file (`full_address.csv`) containing Japanese address data in the specified format.
