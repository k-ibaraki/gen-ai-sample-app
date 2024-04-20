import sys
import logging

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.base import Runnable, RunnableSerializable
from langchain.schema.runnable import RunnableLambda
from langchain_core.language_models.llms import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel


from sample_ai_chat.types.types import ChatInput, ChatOutput

logger: logging.Logger = logging.getLogger(__name__)


def get_chat_chain(
    llm: BaseLLM | BaseChatModel,
    chat_template: str = "{question}",
) -> Runnable[ChatInput, ChatOutput]:

    async def _get_chat_chain(input: ChatInput) -> ChatOutput:
        logger.info(f"start: {sys._getframe().f_code.co_name}")
        # OutputParserを作成
        output_parser: StrOutputParser = StrOutputParser()
        # 入力の質問文と出力のフォーマットを指定してPromptを作成
        prompt = PromptTemplate(
            template=chat_template,
            input_variables=['question'],
        )
        chain: RunnableSerializable[dict, str] = prompt | llm | output_parser
        result: ChatOutput = ChatOutput(
            **input,
            answer=chain.invoke({'question': input.get('question')}),
        )
        logger.info(f"end: {sys._getframe().f_code.co_name}")
        return result

    return RunnableLambda(_get_chat_chain)
