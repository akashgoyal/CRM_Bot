import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import re, json

# from main_agent1 import text2sql
# @st.cache_resource
# def get_text2sql_object():
#     return text2sql()
# text2sql_obj = get_text2sql_object()

import requests
def process(query):
    url = "http://localhost:8000/text2sql"
    payload = { "query": query }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result['result']
    else:
        print(f"Error: {response.status_code}")
        return response.text
    
##
def display_response_as_table(response):
    try:
        # Try to parse the response as JSON
        data = json.loads(response)
    except json.JSONDecodeError:
        st.error("Invalid JSON response")
        st.text(response)
        return

    result_df = None
    if isinstance(data, dict):
        # Case 1: Multiple categories with lists of dictionaries
        if all(isinstance(value, list) and all(isinstance(item, dict) for item in value) for value in data.values()):
            for category, items in data.items():
                st.subheader(category)
                df = pd.DataFrame(items)
                # st.table(df)
                result_df = df
        
        # Case 2: Single dictionary with simple key-value pairs
        elif all(not isinstance(value, (dict, list)) for value in data.values()):
            df = pd.DataFrame([data])
            # st.table(df)
            result_df = df
        
        # Case 3: Dictionary with lists of equal length
        elif all(isinstance(value, list) and len(value) == len(next(iter(data.values()))) for value in data.values()):
            df = pd.DataFrame(data)
            # st.table(df)
            result_df = df

        else:
            st.warning("Unrecognized data structure")
            st.json(data)
            result_df = None
    
    elif isinstance(data, list):
        df = pd.DataFrame(data)
        # st.table(df)
        result_df = df
    
    else:
        st.warning("Unrecognized data structure")
        st.json(data)
        result_df = None
    
    return result_df
##

# Function to convert dataframe to image
def dataframe_to_image(df):
    table_html = df.to_html(index=False)
    return f"<img src='data:image/png;base64,{base64.b64encode(table_html.encode()).decode()}' style='width:100%'>"


# Streamlit app
def main():
    st.title("Healthcare Database Chatbot")

    # Sidebar
    st.sidebar.title("Database Selection")
    database = st.sidebar.selectbox("Choose a database", ["Database One", "Database Two"])

    # Database description
    if database == "Database One":
        st.sidebar.write("Database One contains information about hospital staff and patient records.")
    else:
        st.sidebar.write("Database Two contains information about medical procedures and equipment inventory.")

    # Main chat interface
    st.subheader("Chat with the Healthcare Database")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get LLM response using text2sql
        try:
            response = process(prompt)
        except Exception as e:
            response = f"An error occurred: {str(e)}"

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
            df = display_response_as_table(response)
            st.markdown(st.table(df))

            # Example: Display an image (you may need to adjust this based on your actual response format)
            if "image" in response.lower():
                image = Image.open("placeholder_image.png")
                st.image(image, caption="Placeholder Image")

            # Example: Display a table (you may need to adjust this based on your actual response format)
            if "table" in response.lower():
                # This is a placeholder. You should parse the actual SQL result into a DataFrame
                df = pd.DataFrame({
                    "Column1": [1, 2, 3],
                    "Column2": ["A", "B", "C"]
                })
                st.table(df)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()