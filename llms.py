import os
from dotenv import load_dotenv
load_dotenv('.env')
ai71_api_key = os.getenv("AI71_API_KEY", None)
##
from typing import Any, Optional
from llama_index.llms.openai_like import OpenAILike

class AI71LLM(OpenAILike):
    def __init__(
        self, model: str, api_key: Optional[str] = None,
        api_base: str = "https://api.ai71.ai/v1",
        is_chat_model: bool = True,
        **kwargs: Any,
    ) -> None:
        api_key = api_key or os.environ.get("AI71_API_KEY", None)
        super().__init__(model=model, api_key=api_key, api_base=api_base, is_chat_model=is_chat_model, **kwargs,)

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "AI71LLM"
##


def ai71_falcon_11b_init():
    llm = AI71LLM(api_key=ai71_api_key, model="tiiuae/falcon-11b")
    return llm

def ai71_falcon_180b_init():
    llm = AI71LLM(api_key=ai71_api_key, model="tiiuae/falcon-180b-chat")
    return llm

my_llm = ai71_falcon_11b_init()
selected_llm = ai71_falcon_11b_init()

# response = my_llm.stream_complete("Write a song about a ginger-colored fish on the moon.")
# for r in response:
#     print(r.delta, end="")

# response = my_llm.complete("Write a song about a ginger-colored fish on the moon.")
# print(response)


from llama_index.embeddings.huggingface import HuggingFaceEmbedding
def hf_baai_bge_small_init():
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return embed_model

from llama_index.core import Settings
Settings.embed_model = hf_baai_bge_small_init()
# Settings.model = ai71_falcon_11b_init()
