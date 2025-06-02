import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from data.data_fetcher import fetch_json_data

class TestDataFetcher(unittest.TestCase):
    def test_fetch_json_data(self):
        data = fetch_json_data('https://gist.githubusercontent.com/Yvenlee/1b028353e059f28a8d00768a2d3791fc/raw/b4f0310ade47261a518c77308900a16a1b53a516/games_cleaned.json')
        self.assertIsNotNone(data)

if __name__ == '__main__':
    unittest.main()
