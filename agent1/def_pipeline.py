from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
    CustomQueryComponent,
)
from llama_index.core.prompts import PromptTemplate
import llms
import agent1.prompts as prompts
from agent1.sql_module import sql_module_obj
from pyvis.network import Network

class QueryPipeline:
    def __init__(self):
        self.llm = llms.selected_llm
        self.response_synthesis_prompt = PromptTemplate(prompts.response_synthesis_prompt_str)
        self.SqlModule_obj = sql_module_obj
        self.obj_retriever = self.SqlModule_obj.obj_retriever
        self.table_parser_component = self.SqlModule_obj.table_parser_component
        self.text2sql_prompt = self.SqlModule_obj.text2sql_prompt
        self.sql_parser_component = self.SqlModule_obj.sql_parser_component
        self.sql_retriever = self.SqlModule_obj.sql_retriever

        # print(f"obj_retriever: {self.obj_retriever}")
        # print(f"table_parser_component: {self.table_parser_component}")
        # print(f"text2sql_prompt: {self.text2sql_prompt}")
        # print(f"sql_parser_component: {self.sql_parser_component}")
        # print(f"sql_retriever: {self.sql_retriever}")
        # print(self.text2sql_prompt.template)


    def create_query_pipeline(self):
        qp = QP(
            modules={
                "input": InputComponent(),
                "table_retriever": self.obj_retriever,
                "table_output_parser": self.table_parser_component,
                "text2sql_prompt": self.text2sql_prompt,
                "text2sql_llm": self.llm,
                "sql_output_parser": self.sql_parser_component,
                "sql_retriever": self.sql_retriever,
                "response_synthesis_prompt": self.response_synthesis_prompt,
                "response_synthesis_llm": self.llm,
            },
            verbose=True,
        )

        qp.add_chain(["input", "table_retriever", "table_output_parser"])
        qp.add_link("input", "text2sql_prompt", dest_key="query_str")
        qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
        qp.add_chain(["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"])
        qp.add_link("sql_output_parser", "response_synthesis_prompt", dest_key="sql_query")
        qp.add_link("sql_retriever", "response_synthesis_prompt", dest_key="context_str")
        qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
        qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

        return qp

    def visualize_query_pipeline(self, qp):
        net = Network(notebook=True, cdn_resources="in_line", directed=True)
        net.from_nx(qp.dag)
        net.show("text2sql_dag.html")

# query_pipeline = QueryPipeline()
# qp = query_pipeline.create_query_pipeline()
# query_pipeline.visualize_query_pipeline(qp)