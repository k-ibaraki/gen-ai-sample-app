import logging
import langchain
from langchain_core.language_models.llms import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.cache import InMemoryCache
from langchain_core.runnables.base import Runnable
from sample_ai_chat.types.types import ChatInput, ChatOutput
from sample_ai_chat.chains.get_chat_chain import get_chat_chain
from sample_ai_chat.env import DEBUG

logger: logging.Logger = logging.getLogger(__name__)

# デバッグモードの設定
langchain.debug = DEBUG
# Cacheの設定
langchain.llm_cache = InMemoryCache()


# チャットのテンプレートの初期値
chat_template = """\
{question}
"""


async def app_chat_process(
        question: str,
        llm: BaseLLM | BaseChatModel,
        chat_template: str = chat_template
) -> ChatOutput:

    ## LangChainのChainを作成 ##

    # キーワード抽出のChainを作成
    keyword_chain: Runnable[ChatInput, ChatOutput] = get_chat_chain(
        llm=llm,
        chat_template=chat_template
    )

    ## Chainを実行 ##
    result: ChatOutput
    try:
        result = await keyword_chain.ainvoke(
            ChatInput(question=question)
        )
    except Exception as e:
        logger.error(f"Error:{str(e)}:{str(e.__class__)}")
        result = ChatOutput(
            question=question,
            answer=f"エラーが発生しました:{str(e)}:{str(e.__class__)}",
        )
    ## 結果を返す ##
    return result
