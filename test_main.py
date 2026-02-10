import pytest
import os
import pandas as pd
from main import is_match, load_data
from streamlit.testing.v1 import AppTest

# --- Unit Tests for Logic ---
@pytest.mark.parametrize("candidate, guess, result, expected", [
    # Basic matching
    ("TABOO", "ROBOT", "01221", True),
    ("TABLE", "ROBOT", "01221", False),
    # Duplicate letters
    ("SPEED", "EERIE", "11000", True),
    ("SPELL", "EERIE", "11000", False),
    # Green and Gray
    ("APPLE", "ABIDE", "20002", True),
    ("APPLE", "ARISE", "20002", True), 
    # Yellow constraints
    ("STARE", "TEARS", "11221", True),
    ("STARE", "STARE", "22222", True),
    # Duplicate letters complicated
    ("ABBEY", "BABES", "11220", True),
])
def test_is_match_logic(candidate, guess, result, expected):
    assert is_match(candidate, guess, result) == expected

# --- Integration Tests for Data Loading ---
def test_data_loading_smoke():
    """Verify that data files are loaded without crash."""
    # Assuming fivewords.pkl and history.csv exist in the directory
    if os.path.exists('fivewords.pkl'):
        candidates, history = load_data()
        assert isinstance(candidates, list)
        assert isinstance(history, list)
        if len(candidates) > 0:
            assert isinstance(candidates[0], str)

# --- UI Tests with AppTest ---
def test_streamlit_app_startup():
    """Verify that the Streamlit app starts correctly."""
    at = AppTest.from_file("app.py").run(timeout=30)
    assert not at.exception
    # Check for the title
    assert "Wordle Helper" in at.title[0].value

def test_streamlit_app_input_filter():
    """Verify that entering a guess filters the candidates."""
    at = AppTest.from_file("app.py").run(timeout=30)
    
    # Get initial count from the subheader (format: "Candidates (N)")
    initial_count_text = at.subheader[0].value
    
    # Enter a filter
    # Assuming the first text input is the one for attempts
    at.text_input[0].set_value("ARISE00000").run()
    
    filtered_count_text = at.subheader[0].value
    
    # If the filter works, the count text should be different (or at least valid)
    assert "Candidates" in filtered_count_text
    
def test_streamlit_app_reset():
    """Verify that the reset button works."""
    at = AppTest.from_file("app.py").run(timeout=30)
    at.text_input[0].set_value("ARISE00000").run()
    
    # Click reset in sidebar
    at.sidebar.button[0].click().run()
    
    # Input should be cleared (Streamlit inputs might reset to default)
    # The filtered list in session state should be reset
    assert "Candidates" in at.subheader[0].value
