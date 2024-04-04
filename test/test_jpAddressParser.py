import unittest
import csv
import os
from jpAddressParser import *

class TestAddressParser(unittest.TestCase):

    def setUp(self):
        # Create a dummy CSV file for testing
        self.dummy_csv_file = "test_data.csv"
        self.test_csv_path = "test_export.csv"
        with open(self.dummy_csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["日本 東京都台東区蔵前4丁目3-12",])

    def tearDown(self):
        # Remove dummy CSV files after testing
        for file_path in [self.dummy_csv_file, self.test_csv_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_import_csv(self):
        data = import_csv(self.dummy_csv_file)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['full_address'], "日本 東京都台東区蔵前4丁目3-12")

    def test_export_csv(self):
        # Create dummy data
        data = [{'full_address': '日本 東京都台東区蔵前4丁目3-12', 'work': '日本 東京都台東区蔵前4丁目3-12'}]
        export_csv(data, self.test_csv_path)
        self.assertTrue(os.path.exists(self.test_csv_path))

    def test_extract_country(self):
        addr = {'work': '日本 東京都台東区蔵前4丁目3-12'}
        addr = extract_country(addr)
        self.assertEqual(addr['country'], '日本')

    def test_extract_postalcode(self):
        addr = {'work': '〒116-0013 東京都荒川区西日暮里2丁目19-1号'}
        addr = extract_postalcode(addr)
        self.assertEqual(addr['PostalCode'], '〒116-0013')

    def test_parse_address_pattern1(self):
        # Quantexa Office: Yammer Tokyo 12F, 2-1-1 Yaseu, Chuo-ku, Tokyo
        addr = {'work': '東京都中央区八重洲2-1-1 YANMAR TOKYO 12F'}
        addr = parse_address(addr)
        self.assertEqual(addr['prefecture'], '東京都')
        self.assertIsNone(addr['county'])
        self.assertEqual(addr['city'], '中央区')
        self.assertIsNone(addr['ward'])
        self.assertEqual(addr['neighborhood'], '八重洲二丁目')
        self.assertEqual(addr['banch'], '1')
        self.assertEqual(addr['go'], '1')
        self.assertEqual(addr['buildingName'], 'YANMAR TOKYO 12F')
        self.assertIsNone(addr['roomNumber'])
        self.assertIsNone(addr['floorNumber'])

    def test_parse_address_pattern2(self):
        # Complex Address: Watanabe 3, Kyutaromachi 4 Chome, Chuo-ku, Osaka-shi, Osaka
        addr = {'work': '大阪府大阪市中央区久太郎町４丁目渡辺３号'}
        addr = parse_address(addr)
        self.assertEqual(addr['prefecture'], '大阪府')
        self.assertIsNone(addr['county'])
        self.assertEqual(addr['city'], '大阪市')
        self.assertEqual(addr['ward'], '中央区')
        self.assertEqual(addr['neighborhood'], '久太郎町四丁目')
        self.assertEqual(addr['banch'], '渡辺3号')
        self.assertIsNone(addr['go'])
        self.assertIsNone(addr['buildingName'])
        self.assertIsNone(addr['roomNumber'])
        self.assertIsNone(addr['floorNumber'])


    def test_parse_address_pattern3(self):
        # Repeated same word in Address: Minami-nagano Agatamachi 477-1, Nagano-shi, Nagano
        addr = {'work': '長野県長野市南長野県町477-1'}
        addr = parse_address(addr)
        self.assertEqual(addr['prefecture'], '長野県')
        self.assertIsNone(addr['county'])
        self.assertEqual(addr['city'], '長野市')
        self.assertIsNone(addr['ward'])
        self.assertEqual(addr['neighborhood'], '大字南長野')
        self.assertEqual(addr['banch'], '県町477')
        self.assertEqual(addr['go'], '1')
        self.assertIsNone(addr['buildingName'])
        self.assertIsNone(addr['roomNumber'])
        self.assertIsNone(addr['floorNumber'])


    def test_parse_address_pattern4(self):
        # Address in county: Sakae 609-1, Shirahama, Nishimuro-gun, Wakayama
        addr = {'work': '和歌山県西牟婁郡白浜町栄609-2'}
        addr = parse_address(addr)
        self.assertEqual(addr['prefecture'], '和歌山県')
        self.assertEqual(addr['county'], '西牟婁郡')
        self.assertEqual(addr['city'], '白浜町')
        self.assertIsNone(addr['ward'])
        self.assertEqual(addr['neighborhood'], '栄')
        self.assertEqual(addr['banch'], '609')
        self.assertEqual(addr['go'], '2')
        self.assertIsNone(addr['buildingName'])
        self.assertIsNone(addr['roomNumber'])
        self.assertIsNone(addr['floorNumber'])

if __name__ == '__main__':
    unittest.main()