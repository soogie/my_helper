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
        if eval(query):
            new_words.append(word)
    return new_words


if len(st.session_state["words"]) == 0:
    df = pd.read_pickle("data/fivewords.pkl")
    st.session_state["words"] = df["word"]
    st.sidebar.text(f"{len(df)} data loaded.")

with st.form("input", clear_on_submit=True):

    new_query = st.text_input("Queryを追加")

    if st.form_submit_button("追加"):
        if new_query not in st.session_state["query_list"]:
            st.session_state["query_list"].append(new_query)

if len(st.session_state["words"]) < 500:
    st.dataframe(st.session_state["words"], height=2000, hide_index=False)

# サイドバー
if len(st.session_state["query_list"]) > 0:
    for query in st.session_state["query_list"]:
        st.session_state["words"] = word_check(st.session_state["words"], query)
        st.sidebar.text(f'{query} : {str(len(st.session_state["words"]))}')

if st.sidebar.button("クエリ削除"):
    st.session_state["query_list"] = []
    st.reload()
    


    
    