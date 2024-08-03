from def_pipeline import QueryPipeline

query_pipeline = QueryPipeline()
qp = query_pipeline.create_query_pipeline()
query_pipeline.visualize_query_pipeline(qp)
print("Pipeline visualized")

# execute 
while True:
    query_str = input("Enter your query: ")
    if query_str == "quit":
        break
    # query="What was the year that The Notorious B.I.G was signed to Bad Boy?"
    # query="Who won best director in the 1972 academy awards"
    # query="What was the term of Pasquale Preziosa?"
    response = qp.run(query=query_str,)
    # print(str(response))
    print(response.message.content)
