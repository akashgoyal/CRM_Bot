import os
import streamlit as st
os.environ["AI71_API_KEY"] = st.secrets["AI71_API_KEY"]

import pandas as pd
from PIL import Image
import io
import base64
import re, json
import requests
import llms
from llama_index.core.base.llms.types import CompletionResponse

from main_agent1 import text2sql
text2sql_obj = text2sql()

import random
import base64
image_files = ["dr_img1.png", "dr_img2.png", "dr_img3.png"]


def analyse_response(query, response):
    prompt = f"""
        Given the query: {query} 
        Analyse its response: {response}
        Is the query and response about a single entity or multiple entities?

        If it is about a single entity, return the Role & Name in JSON format.
        Output must be in JSON format, keys should be "Role" and "Name".
        Don't create any new keys. Use only "Role" and "Name".
        Return only the JSON output, don't attach any other text.
        Make sure the output only have JSON format. No other text.
        Example:
        {{
            "Role": "Doctor",
            "Name": "Michael Johnson"
        }}
        
        Otherwise, return 0.
        """
    response = llms.selected_llm.complete(prompt)
    return response


def get_doctor_info(json_response):
    name = json_response.get("Name", "Michael Johnson")
    address = "4th Square, Cool City, NYC, USA"
    age = 37
    image_path = image_files[random.randint(0, 2)]
    with open(image_path, "rb") as image_file:
        img = base64.b64encode(image_file.read()).decode('utf-8')
    return { "name": name, "address": address, "age": age, "image": img }

def get_patient_info():
    pass


def display_response_as_table(response):
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        # st.error("Invalid JSON response")
        st.text(response)
        return None

    result_df = None
    if isinstance(data, dict):
        if all(isinstance(value, list) and all(isinstance(item, dict) for item in value) for value in data.values()):
            dfs = {}
            for category, items in data.items():
                dfs[category] = pd.DataFrame(items)
            return dfs
        elif all(not isinstance(value, (dict, list)) for value in data.values()):
            result_df = pd.DataFrame([data])
        elif all(isinstance(value, list) and len(value) == len(next(iter(data.values()))) for value in data.values()):
            result_df = pd.DataFrame(data)
        else:
            # st.warning("Unrecognized data structure")
            st.json(data)
            result_df = None
    elif isinstance(data, list):
        result_df = pd.DataFrame(data)
    else:
        # st.warning("Unrecognized data structure")
        st.json(data)
        result_df = None
    
    return result_df


def main():
    st.title("Hospitals in State - CRM bot")

    st.sidebar.title("Database Selection")
    database = st.sidebar.selectbox("Choose a database", ["Chain of Hospitals", "Chain of Schools"])

    if database == "Chain of Hospitals":
        st.sidebar.write("DB for a Government Top Tier Medical Officer. This database contains information about Hospitals, Doctors, Patients records in the specific state.")
    else:
        st.sidebar.write("NOT YET IMPLEMENTED. But this will have details of Schools, Students, Teachers, etc. in the specific state.")

    st.subheader("Hello Medical Officer. Chat with the Healthcare Database")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "table" in message:
                if isinstance(message["table"], dict):
                    for category, df in message["table"].items():
                        st.subheader(category)
                        st.table(df)
                else:
                    st.table(message["table"])

    if prompt := st.chat_input("What would you like to know?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            # response = process(prompt)
            response = text2sql_obj.text2sql_response(prompt)
        except Exception as e:
            response = f"An error occurred: {str(e)}"

        with st.chat_message("assistant"):
            # st.markdown(response)
            df = display_response_as_table(response)
            analysis_resp = analyse_response(prompt, response)

            print(analysis_resp)
            if isinstance(analysis_resp, CompletionResponse):
                try:
                    analysis_resp = json.loads(analysis_resp.text)
                except json.JSONDecodeError:
                    print("Error: Unable to parse the response as JSON")
                    analysis_resp = {}
            elif isinstance(analysis_resp, str):
                try:
                    analysis_resp = json.loads(analysis_resp)
                except json.JSONDecodeError:
                    print("Error: Unable to parse the response as JSON")
                    analysis_resp = {}

            print("##########")
            print(analysis_resp)
            print("##########")
            print(type(analysis_resp))
            print("###########")
            doctor_card = None
            if isinstance(analysis_resp, dict) and 'Role' in analysis_resp and 'Name' in analysis_resp:
                if analysis_resp["Role"].lower() == "doctor":
                    doc_dict = get_doctor_info(analysis_resp)
                    doc_col1, doc_col2 = st.columns(2)
                    with doc_col1:
                        img_bytes = base64.b64decode(doc_dict["image"])
                        st.image(img_bytes, caption="Doctor's Photo", use_column_width=True)
                    with doc_col2:
                        st.header(doc_dict["name"])
                        st.subheader(f"{doc_dict['age']} years")
                        st.subheader(f"{doc_dict['address']}")
            else:
                print("The response does not contain 'Role' and 'Name' keys or is not about a doctor.")
            
            if df is not None:
                if isinstance(df, dict):
                    for category, category_df in df.items():
                        # st.subheader(category)
                        # st.table(category_df)
                        df = category_df
                
                st.table(df)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "",
                    "table": df
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })


if __name__ == "__main__":
    main()