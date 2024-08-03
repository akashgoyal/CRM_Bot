from prep_data import DataPreparation
from pathlib import Path
from typing import List

from llama_index.core.objects import (SQLTableNodeMapping, ObjectIndex, SQLTableSchema,)
from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.retrievers import SQLRetriever
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core.llms import ChatResponse

class SqlModule:
    def __init__(self, data_prep_obj):
        self.table_parser_component = None
        self.sql_parser_component = None

        self.data_prep_obj = data_prep_obj
        self.engine = self.data_prep_obj.engine
        self.table_infos = self.data_prep_obj.table_infos
        self.text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(dialect=self.engine.dialect.name)

        #
        self.sql_database = SQLDatabase(self.engine)
        self.table_node_mapping = SQLTableNodeMapping(self.sql_database)
        self.table_schema_objs = [
            SQLTableSchema(table_name=t.table_name, context_str=t.table_summary)
            for t in self.table_infos
        ]

        self.obj_index = ObjectIndex.from_objects(self.table_schema_objs, self.table_node_mapping, VectorStoreIndex,) 
        #(embed_model=llms.together_m2bert_2k_init))
        self.obj_retriever = self.obj_index.as_retriever(similarity_top_k=3)
        self.sql_retriever = SQLRetriever(self.sql_database)

    def get_table_context_str(self, table_schema_objs: List[SQLTableSchema]):
        """Get table context string."""
        context_strs = []
        for table_schema_obj in table_schema_objs:
            table_info = self.sql_database.get_single_table_info(
                table_schema_obj.table_name
            )
            if table_schema_obj.context_str:
                table_opt_context = (
                    " The table description is: " + table_schema_obj.context_str
                )
                table_info += table_opt_context

            context_strs.append(table_info)
        return "\n\n".join(context_strs)

    def parse_response_to_sql(self, response: ChatResponse) -> str:
        """Parse response to SQL."""
        response = response.message.content
        sql_query_start = response.find("SQLQuery:")
        if sql_query_start != -1:
            response = response[sql_query_start:]
            # TODO: move to removeprefix after Python 3.9+
            if response.startswith("SQLQuery:"):
                response = response[len("SQLQuery:") :]
        sql_result_start = response.find("SQLResult:")
        if sql_result_start != -1:
            response = response[:sql_result_start]
        return response.strip().strip("```").strip()

    def run(self):
        self.table_parser_component = FnComponent(fn=self.get_table_context_str)
        print("table_parser_component - DONE")
        self.sql_parser_component = FnComponent(fn=self.parse_response_to_sql)
        print("sql_parser_component - DONE")
        

## args
url = "https://github.com/ppasupat/WikiTableQuestions/releases/download/v1.0.2/WikiTableQuestions-1.0.2-compact.zip"
data_dir = Path("./wiki_data")
tableinfo_dir = "./wiki_data/WikiTableQuestions_TableInfo"
extracted_data_dir = Path("./wiki_data/WikiTableQuestions/csv/200-csv")
##                       
data_prep_obj = DataPreparation(url=url, data_dir=data_dir, tableinfo_dir=tableinfo_dir, extracted_data_dir=extracted_data_dir,)
data_prep_obj.prepare_data()
print("Data preparation - done - inside SQLModule")
##
sql_module_obj = SqlModule(data_prep_obj)
sql_module_obj.run()
# print(sql_module_obj.table_parser_component)
# print(sql_module_obj.sql_parser_component)
# print("DONE inside sql_module.py")