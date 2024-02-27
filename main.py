import re
import pandas as pd
import streamlit as st


st.title("wordle helper")
if "query_list" not in st.session_state:
    st.session_state["query_list"] = []

if "words" not in st.session_state:
    st.session_state["words"] = []

def word_check(words, query):
    new_words = []
    for word in words:
        if query[:3] == "all":
            pattern = r"'([^']*)'"
            string = re.findall(pattern, query)
            if all(char not in word for char in f"{string}"):
                new_words.append(word)
            
        elif eval(query):
            new_words.append(word)
    return new_words


if len(st.session_state["words"]) == 0:
    df = pd.read_pickle("data/fivewords.pkl")
    st.session_state["words"] = df["word"]
    st.sidebar.text(f"{len(df)} data loaded.")
words = st.session_state["words"]

type_select = st.radio("タイプ選択", ["直接入力", "位置指定", "位置除外", "含む", "含まない", "全部除く"])
with st.form("input", clear_on_submit=True):
    if type_select == "直接入力":
        new_query = st.text_input("追加するクエリ")
    elif type_select == "位置指定" or type_select == "位置除外":
        pos = st.radio("何文字目？", [1, 2, 3, 4, 5], index=None, horizontal=True)
        char = st.text_input("1文字", max_chars=1)
        if pos and char:
            if type_select == "位置指定":
                new_query = f"word[{pos - 1}] == '{char}'"
            else:
                new_query = f"word[{pos - 1}] != '{char}'"
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

# サイドバー
if len(st.session_state["query_list"]) > 0:
    for query in st.session_state["query_list"]:
        words = word_check(words, query)
        st.sidebar.text(f'{query} : {str(len(words))}')

if st.sidebar.button("クエリ削除"):
    st.session_state["query_list"] = []
    

st.markdown(", ".join(words))

    
    
