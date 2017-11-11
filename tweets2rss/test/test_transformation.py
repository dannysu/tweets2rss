import unittest
import json
import os

from tweets2rss.transformation import decorate

dir = os.path.dirname(__file__)

class TestTransformation(unittest.TestCase):

    def test_decorate_link_and_image(self):
        with open(os.path.join(dir, 'tweets/with_image.json'), 'r') as file:
            tweet = json.load(file)
        with open(os.path.join(dir, 'tweets/with_image.txt'), 'r') as file:
            expected_text = file.read().strip()
        result = decorate(tweet)
        self.assertEqual(result, expected_text)

if __name__ == '__main__':
    unittest.main()
