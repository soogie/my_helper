import unittest
import pandas as pd
from unittest.mock import patch
import streamlit as st  # Import streamlit

# Import the function to be tested, not the entire file
from main import word_check, load_data # Only import word_check


class TestWordCheck(unittest.TestCase):
    def setUp(self):
        # create dummy dataframe for testing
        data = {'word': ["apple", "apply", "apric", "grape", "crane", "cloud"]}
        self.df = pd.DataFrame(data)
        
        self.words = data["word"]

    def tearDown(self):
        # Clean up st.session_state after each test
        pass

    def test_all_not_in(self):
        # Test case for "all" query - characters not in the word
        query = "all 'ae'"
        result = word_check(self.words, query)
        self.assertEqual(result, ["cloud"])

        query = "all 'ap'"
        result = word_check(self.words, query)
        self.assertEqual(result, ["cloud"])

        query = "all 'aplec'"
        result = word_check(self.words, query)
        self.assertEqual(result, [])
        
        query = "all 'cr'"
        result = word_check(self.words, query)
        self.assertEqual(result, ["apple", "apply"])
        
        query = "all 'xzw'"
        result = word_check(self.words, query)
        self.assertEqual(result, self.words)
    

    def test_position_match(self):
        # Test case for position match query
        query = ["word[0] == 'a'", "word[4] == 'e'"]
        result = word_check(self.words, query)
        self.assertEqual(result, ["apple"])
        
        query = ["word[0] == 'a'", "word[3] == 'i'"]
        result = word_check(self.words, query)
        self.assertEqual(result, ["apric"])

        query = ["word[0] == 'g'", "word[4] == 'e'"]
        result = word_check(self.words, query)
        self.assertEqual(result, ["grape"])
        
    def test_position_not_match(self):
        # Test case for position not match query
        query = "word[0] != 'a'"
        result = word_check(self.words, query)
        self.assertEqual(result, ["grape", "crane", "cloud"])

        query = "word[2] != 'r'"
        result = word_check(self.words, query)
        self.assertEqual(result, ["apple","apply","grape", "crane", "cloud"])

    def test_contains_char(self):
        # Test case for contains character query
        query = "'p' in word"
        result = word_check(self.words, query)
        self.assertEqual(result, ["apple", "apply", "apric", "grape"])
        
        query = "'a' in word"
        result = word_check(self.words, query)
        self.assertEqual(result, ["apple", "apply", "apric", "grape", "crane"])
        
        query = "'z' in word"
        result = word_check(self.words, query)
        self.assertEqual(result, [])

    def test_not_contains_char(self):
        # Test case for not contains character query
        query = "'p' not in word"
        result = word_check(self.words, query)
        self.assertEqual(result, ["crane", "cloud"])
        
        query = "'z' not in word"
        result = word_check(self.words, query)
        self.assertEqual(result, self.words)
        
        query = "'a' not in word"
        result = word_check(self.words, query)
        self.assertEqual(result, ["cloud"])

    def test_multiple_conditions_position(self):
        # Test with multiple conditions (should be handled in the app, not directly in word_check)
        query = ["word[0] == 'a'", "'p' in word"]
        result = word_check(self.words, query)
        self.assertEqual(result, ["apple", "apply", "apric"])
        
        query = ["word[0] != 'a'", "'r' in word"]
        result = word_check(self.words, query)
        self.assertEqual(result, ["grape","crane"])

    def test_multiple_conditions_mix(self):
        query = ["word[0] == 'a'", "'p' not in word"]
        result = word_check(self.words, query)
        self.assertEqual(result, [])
        
    def test_load_data(self):
        word, history = load_data()
        self.assertEqual(len(word),39933)
        self.assertEqual(len(history),1352)

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
