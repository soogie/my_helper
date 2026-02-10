import re
import pandas as pd
import streamlit as st

# --- Core Logic (No Streamlit) ---

def word_check(words, query):
    """
    Filters a list of words based on a query.

    Args:
        words: A list of words (strings).
        query: A string or list of strings representing the filtering condition.

    Returns:
        A list of words that match the query.
    """
    new_words = []
    for word in words:
        if isinstance(query, str):
            if query[:3] == "all":
                pattern = r"'([^']*)'"
                string = re.findall(pattern, query)
                if all(char not in word for char in f"{string[0]}"):
                    new_words.append(word)
            else:
                try:
                    res = eval(query)
                except SyntaxError as e:
                    raise Exception(f"SyntaxError in {query}")
                except NameError as e:
                    raise Exception(f"NameError in {query}")
                    
                if res:
                    new_words.append(word)
        elif isinstance(query, list):
            if len(query) == 2:
                if eval(query[0]) and eval(query[1]):
                    new_words.append(word)
    return new_words

def load_data():
    """
    Loads data (word list and history) from files.

    Returns:
        A tuple containing the list of words and the history list.
    """
    df = pd.read_pickle("data/fivewords.pkl")
    with open("history.csv", "r") as f:  # 最新版の取得はget_history.py
        history = f.read().split(",")
        history = [h.lower() for h in history]
    return list(df["word"]), history


# --- Streamlit App Logic ---

def main():
    st.title("wordle helper")

    if "query_list" not in st.session_state:
        st.session_state["query_list"] = []

    if "words" not in st.session_state:
        st.session_state["words"], st.session_state["history"] = load_data()
    
    words = st.session_state["words"]
    history = st.session_state["history"]

    st.sidebar.text(f"{len(words)} data loaded.")

    mode_select = st.radio("history", ["ON", "OFF"], index=1)
    type_select = st.radio("タイプ選択", ["直接入力", "位置指定", "位置除外", "含む", "含まない", "全部除く"])

    with st.form("input", clear_on_submit=True):
        new_query = "" # Initialize new_query
        if type_select == "直接入力":
            new_query = st.text_input("追加するクエリ")
        elif type_select == "位置指定" or type_select == "位置除外":
            pos = st.radio("何文字目？", [1, 2, 3, 4, 5], index=None, horizontal=True)
            char = st.text_input("1文字", max_chars=1)
            if pos and char:
                if type_select == "位置指定":
                    new_query = f"word[{pos - 1}] == '{char}'"
                else:
                    new_query = [f"word[{pos - 1}] != '{char}'", f"'{char}' in word"]
        else:
            string = st.text_input("1文字or文字列")
            if string:
                if type_select == "含む":
                    new_query = f"'{string}' in word"
                elif type_select == "全部除く":
                    new_query = f"all(char not in word for char in '{string}')" 
                else:
                    new_query = f"'{string}' not in word"

        if st.form_submit_button("追加"):
            if new_query not in st.session_state["query_list"]:
                st.session_state["query_list"].append(new_query)

    # Sidebar
    if len(st.session_state["query_list"]) > 0:
        for query in st.session_state["query_list"]:
            words = word_check(words, query)
            st.sidebar.text(f'{query} : {str(len(words))}')

    if st.sidebar.button("クエリ削除"):
        st.session_state["query_list"] = []
        st.rerun()

    # Mode OFF
    words2 = words.copy()
    if mode_select == "ON":
        for word in words2.copy():
            if word in history:
                words2.remove(word)

    st.markdown(", ".join(words2))
    
if __name__ == "__main__":
    main()
