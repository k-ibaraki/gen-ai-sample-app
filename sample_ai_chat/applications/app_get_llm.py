from langchain_core.language_models.llms import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel
from sample_ai_chat.env import GOOGLE_CLOUD_PROJECT
from langchain_google_vertexai import VertexAI
from langchain_google_vertexai.model_garden import ChatAnthropicVertex


async def app_get_llm(
    model: str = "gemini-pro",
    location: str = "asia-northeast1",
    temperature: float = 0.5,
    tokens: int = 1000
) -> BaseLLM | BaseChatModel:

    llm: BaseLLM | BaseChatModel
    if model.startswith("claude-3"):
        llm = ChatAnthropicVertex(
            model_name=model,
            location=location,
            temperature=temperature,
            max_output_tokens=tokens,
            project=GOOGLE_CLOUD_PROJECT,
        )
    else:
        llm = VertexAI(
            model_name=model,
            location=location,
            temperature=temperature,
            max_output_tokens=tokens,
        )
    return llm
