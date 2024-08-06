
get_tablename_summary_str = (
    "Give me a summary of the table in the following JSON format.\n"
    "- The table name must be unique to the table and describe it while being concise.\n"
    "- Do NOT output a generic table name (e.g. table, my_table).\n"
    "Do NOT make the table name one of the following: {exclude_table_name_list}\n"
    "Table:\n{table_str}\n"
    "Summary: "
)

response_synthesis_prompt_str = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n"
    "SQL: {sql_query}\n"
    "SQL Response: {context_str}\n"
    "Response: "
)