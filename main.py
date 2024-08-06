
# AGENT 1
# text2sql using llama-index 
from agent1.def_pipeline import QueryPipeline
class text2sql():
    def __init__(self):
        query_pipeline = QueryPipeline()
        self.qp = query_pipeline.create_query_pipeline()
        # query_pipeline.visualize_query_pipeline(self.qp)
        # print("Pipeline visualized")

    def text2sql_chat(self):
        while True:
            query_str = input("Enter your query: ")
            if query_str == "quit":
                break

            response = self.qp.run(query=query_str,)
            # print(str(response))
            print(response.message.content)
            # return response.message.content



text2sql_obj = text2sql()
text2sql_obj.text2sql_chat()