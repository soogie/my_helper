import streamlit as st
import pandas as pd
import pickle
import os
import warnings

# Suppress deprecation warnings from legacy pickles
warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- Configuration ---
FIVEWORDS_PATH = 'data/fivewords.pkl'
HISTORY_PATH = 'history.csv'

def load_data():
    """Load the candidate list and history."""
    if not os.path.exists(FIVEWORDS_PATH):
        st.error(f"{FIVEWORDS_PATH} not found.")
        return [], []
    
    try:
        with open(FIVEWORDS_PATH, 'rb') as f:
            data = pickle.load(f)
            # Handle various pkl formats (list, Series, DataFrame)
            if isinstance(data, list):
                candidates = data
            elif isinstance(data, pd.Series):
                candidates = data.tolist()
            elif isinstance(data, pd.DataFrame):
                candidates = data.iloc[:, 0].tolist()
            else:
                candidates = list(data)
    except Exception as e:
        st.error(f"Error loading {FIVEWORDS_PATH}: {e}")
        return [], []
            
    # Load history.csv (Expected: headerless, comma-separated on one or more lines)
    history_words = []
    if os.path.exists(HISTORY_PATH):
        try:
            # Try reading as headerless CSV
            df_h = pd.read_csv(HISTORY_PATH, header=None)
            history_words = df_h.values.flatten().tolist()
            # Filter out NaN/invalid entries
            history_words = [str(w).strip().upper() for w in history_words if pd.notna(w)]
        except Exception:
            history_words = []
        
    return candidates, history_words

def save_history(word):
    """Add a solved word to history.csv in a headerless, comma-separated format."""
    candidates, history_words = load_data()
    
    word = word.strip().upper()
    if word not in history_words:
        history_words.append(word)
        # Save as single row comma-separated
        try:
            df_new = pd.DataFrame([history_words])
            df_new.to_csv(HISTORY_PATH, header=None, index=False)
        except Exception as e:
            st.error(f"Failed to save history: {e}")

def is_match(candidate, guess, result):
    """Robust Wordle filtering logic."""
    if len(candidate) != 5:
        return False
    
    candidate = candidate.upper()
    guess = guess.upper()
    
    cand_list = list(candidate)
    guess_list = list(guess)
    
    # 1. Check Green (2)
    for i in range(5):
        if result[i] == '2':
            if candidate[i] != guess[i]:
                return False
            cand_list[i] = None
            guess_list[i] = None
            
    # Count occurrences in candidate (excluding Greens)
    cand_counts = {}
    for char in cand_list:
        if char is not None:
            cand_counts[char] = cand_counts.get(char, 0) + 1
            
    # 2. Check Yellow (1)
    for i in range(5):
        if result[i] == '1':
            char = guess_list[i]
            if candidate[i] == char: # Must not be at this position
                return False
            if cand_counts.get(char, 0) > 0:
                cand_counts[char] -= 1
            else:
                return False
                
    # 3. Check Gray (0)
    for i in range(5):
        if result[i] == '0':
            char = guess_list[i]
            if candidate[i] == char:
                return False
            # Gray means this letter doesn't appear more than we've assigned to Green/Yellow
            if cand_counts.get(char, 0) > 0:
                return False
                
    return True

# --- Streamlit UI ---
st.set_page_config(page_title="Wordle Helper", layout="centered")
st.title("Wordle Helper")

candidates, history_words = load_data()

# Exclude already solved words
solved_set = set(history_words)
initial_candidates = [c for c in candidates if str(c).upper() not in solved_set]

if 'filtered_list' not in st.session_state:
    st.session_state.filtered_list = initial_candidates

with st.sidebar:
    if st.button("Reset Filter"):
        st.session_state.filtered_list = initial_candidates
        st.rerun()

# User Input
user_input = st.text_input("Enter attempt (e.g. ABIDE00001):", placeholder="WORD + 5 digits (0:Gray, 1:Yellow, 2:Green)")

if user_input and len(user_input) == 10:
    word = user_input[:5].upper()
    result = user_input[5:]
    
    if not word.isalpha() or not result.isdigit():
        st.warning("Invalid input format. Use 5 letters followed by 5 digits.")
    else:
        # Filter current list
        st.session_state.filtered_list = [c for c in st.session_state.filtered_list if is_match(str(c), word, result)]
        st.success(f"Filtered by {word} with result {result}")

# Display Results
st.subheader(f"Candidates ({len(st.session_state.filtered_list)})")

if st.session_state.filtered_list:
    # Most likely candidate
    top_word = str(st.session_state.filtered_list[0]).upper()
    st.info(f"Recommended Next Guess: **{top_word}**")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("All Candidates:")
        st.write(", ".join([str(c) for c in st.session_state.filtered_list]))
    
    with col2:
        if st.button(f"Mark '{top_word}' as SOLVED"):
            save_history(top_word)
            st.success(f"Added {top_word} to history!")
            # Re-load and reset
            candidates, history_words = load_data()
            solved_set = set(history_words)
            st.session_state.filtered_list = [c for c in candidates if str(c).upper() not in solved_set]
            st.rerun()
else:
    st.write("No matching candidates found.")

st.divider()
st.caption("Instructions: Enter your guess and the feedback (0: Not in word/Gray, 1: Wrong spot/Yellow, 2: Correct spot/Green).")
