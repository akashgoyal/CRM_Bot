from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main_agent1 import text2sql

app = FastAPI()

# Initialize the text2sql object
text2sql_obj = text2sql()

class Query(BaseModel):
    query: str

@app.post("/text2sql")
async def get_sql_response(query: Query):
    try:
        response = text2sql_obj.text2sql_response(query.query)
        return {"result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Text2SQL API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)