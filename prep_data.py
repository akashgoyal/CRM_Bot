import os
import json
import requests
import zipfile
import pandas as pd
from pathlib import Path
from llama_index.core.program import LLMTextCompletionProgram, MultiModalLLMCompletionProgram
from llama_index.core.bridge.pydantic import BaseModel, Field
from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, )
import re
import prompts
import llms

#
class DataPreparation:
    def __init__(self, url, data_dir, tableinfo_dir, extracted_data_dir):
        self.url = url
        self.data_dir = data_dir
        self.tableinfo_dir = tableinfo_dir
        self.extracted_data_dir = extracted_data_dir
        self.dfs = []
        self.table_infos = []
        self.engine = None
        self.metadata_obj = None
        self.program = None
        self.llm = llms.selected_llm
        class TableInfo(BaseModel):
            table_name: str = Field(..., description="table name (must be underscores and NO spaces)")
            table_summary: str = Field(..., description="short, concise summary/caption of the table")
        self.TableInfo = TableInfo
        # create data_dir and tableinfo_dir if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.tableinfo_dir, exist_ok=True)


    def download_and_extract_data(self):
        if not os.path.exists(self.data_dir) or len(os.listdir(self.data_dir)) < 2:
            response = requests.get(self.url)
            with open('data.zip', 'wb') as file:
                file.write(response.content)
            with zipfile.ZipFile('data.zip', 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)

    def process_csv_files(self):
        csv_files = sorted([f for f in self.extracted_data_dir.glob("*.csv")])
        for csv_file in csv_files:
            print(f"processing file: {csv_file}")
            try:
                df = pd.read_csv(csv_file)
                self.dfs.append(df)
            except Exception as e:
                print(f"Error parsing {csv_file}: {str(e)}")

    def create_llmtextcompletion_program(self, llm, prompt_str):
        program = LLMTextCompletionProgram.from_defaults(output_cls=self.TableInfo, llm=llm, prompt_template_str=prompt_str)
        return program

    def _get_tableinfo_with_index(self, idx: int) -> str:
        results_gen = Path(self.tableinfo_dir).glob(f"{idx}_*")
        results_list = list(results_gen)
        if len(results_list) == 0:
            return None
        elif len(results_list) == 1:
            path = results_list[0]
            return self.TableInfo.parse_file(path)
        else:
            raise ValueError(f"More than one file matching index: {list(results_gen)}")

    def process_table_infos(self):
        table_names = set()
        for idx, df in enumerate(self.dfs):
            table_info = self._get_tableinfo_with_index(idx)
            if table_info:
                self.table_infos.append(table_info)
            else:
                while True:
                    df_str = df.head(10).to_csv()
                    table_info = self.program(
                        table_str=df_str,
                        exclude_table_name_list=str(list(table_names)),
                    )
                    table_name = table_info.table_name
                    print(f"Processed table: {table_name}")
                    if table_name not in table_names:
                        table_names.add(table_name)
                        break
                    else:
                        # try again
                        print(f"Table name {table_name} already exists, trying again.")
                        pass

                out_file = f"{self.tableinfo_dir}/{idx}_{table_name}.json"
                json.dump(table_info.dict(), open(out_file, "w"))
            self.table_infos.append(table_info)

    def sanitize_column_name(self, col_name):
        return re.sub(r"\W+", "_", col_name)

    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str):
        # Sanitize column names
        sanitized_columns = {col: self.sanitize_column_name(col) for col in df.columns}
        df = df.rename(columns=sanitized_columns)

        # Dynamically create columns based on DataFrame columns and data types
        columns = [
            Column(col, String if dtype == "object" else Integer)
            for col, dtype in zip(df.columns, df.dtypes)
        ]

        # create table
        table = Table(table_name, self.metadata_obj, *columns)
        # create table in db
        self.metadata_obj.create_all(self.engine)
        # Insert data from DataFrame into the table
        with self.engine.connect() as conn:
            for _, row in df.iterrows():
                insert_stmt = table.insert().values(**row.to_dict())
                conn.execute(insert_stmt)
            conn.commit()

    def prepare_data(self):
        # self.download_and_extract_data()
        # print("Data downloaded and extracted")
        self.process_csv_files()
        print("process_csv_files - done")
        self.program = self.create_llmtextcompletion_program(self.llm, prompts.get_tablename_summary_str)
        print("create_llmtextcompletion_program - done")
        self.process_table_infos()
        print("process_table_infos - done")

        self.engine = create_engine("sqlite:///:memory:")
        self.metadata_obj = MetaData()
        for idx, df in enumerate(self.dfs):
            tableinfo = self._get_tableinfo_with_index(idx)
            print(f"Creating table: {tableinfo.table_name}")
            self.create_table_from_dataframe(df, tableinfo.table_name)
        print("Data preparation - done")


# data_prep = DataPreparation(
#     url="https://github.com/ppasupat/WikiTableQuestions/releases/download/v1.0.2/WikiTableQuestions-1.0.2-compact.zip",
#     data_dir=Path("./wiki_data"),
#     tableinfo_dir="./wiki_data/WikiTableQuestions_TableInfo",
#     extracted_data_dir=Path("./wiki_data/WikiTableQuestions/csv/200-csv"),
# )
# data_prep.prepare_data()
