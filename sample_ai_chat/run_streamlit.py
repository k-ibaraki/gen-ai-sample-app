import sys
import asyncio
import logging
from collections import deque

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from google.cloud import aiplatform
from langchain_core.language_models.llms import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel

from sample_ai_chat.library.streamlit_google_oauth import google_oauth2_required
from sample_ai_chat.library.attach_decorator import attach_decorator
from sample_ai_chat.applications.app_chat_process import app_chat_process
from sample_ai_chat.applications.app_get_llm import app_get_llm
from sample_ai_chat.types.types import ChatOutput, ModelDef
from sample_ai_chat.env import UI_TITLE, GOOGLE_AUTH_ON, LOG_LEVEL, GOOGLE_CLOUD_QUOTA_PROJECT, GOOGLE_CLOUD_REGION

# ログの設定
_fmt: str = "%(asctime)s %(levelname)s %(name)s :%(message)s"
_log_level: int = logging.getLevelName(LOG_LEVEL)
logging.basicConfig(level=_log_level, format=_fmt)
logger: logging.Logger = logging.getLogger(__name__)


# GoogleCloudのAIプラットフォームを初期化
aiplatform.init(project=GOOGLE_CLOUD_QUOTA_PROJECT, location=GOOGLE_CLOUD_REGION)


# Chatの発言者
YOU = 'human'
AI = 'ai'

# チャットのカラム数
col_num: int = 2

# streamlitのページ設定
st.set_page_config(
    page_title=UI_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed",
)


async def main() -> None:
    logger.info(f"start: {sys._getframe().f_code.co_name}")

    # ユーザーIDを取得
    id: str = st.session_state['id'] if 'id' in st.session_state else 'unknown'

    # セッションストレージで過去の質問と回答を保持する
    if 'messages' not in st.session_state:
        st.session_state['messages']: deque[list[ChatOutput]] = deque()  # type: ignore
    messages: deque[list[ChatOutput]] = st.session_state['messages']

    # サイドバーの表示 #
    selected_model: list[str | None] = []
    selected_location: list[str | None] = []
    selected_temperature: list[float] = []
    selected_tokens: list[int] = []
    selected_template: list[str] = []
    with st.sidebar:
        for i in range(col_num):
            selected_model.append(st.selectbox(
                f"モデル{i+1}",
                ["gemini-1.5-pro-preview-0409", "claude-3-opus@20240229", "gemini-pro"],
                index=i
            ))
            selected_location.append(st.selectbox(
                f"ロケーション {i+1}",
                ["asia-northeast1", "us-east5"],
                index=i
            ))
            selected_temperature.append(st.number_input(
                f"Temperature {i+1}",
                value=0.5,
                min_value=0.0,
                max_value=1.0,
                step=0.1,
            ))
            selected_tokens.append(int(st.number_input(
                f"Tokens {i+1}",
                value=400,
                min_value=1,
                max_value=1000,
                step=50,
            )))
            selected_template.append(st.text_area(
                f"テンプレート {i+1}",
                value="{question}",
                height=100,
            ))
    # サイドバーここまで #

    # モデルの定義
    models: list[ModelDef] = [
        ModelDef(model=(m if m else ""), location=(l if l else ""), temperature=te, tokens=to)
        for m, l, te, to
        in zip(selected_model, selected_location, selected_temperature, selected_tokens)
    ]

    # LLMを取得
    llms: list[BaseLLM | BaseChatModel] = [await app_get_llm(**m) for m in models]

    # 初期メッセージを表示
    cols: list[DeltaGenerator] = st.columns(col_num)
    for col, model in zip(cols, models):
        col.chat_message(AI).json(model)

    # 画面の表示
    for message in messages:
        # 質問を表示
        st.chat_message(YOU).markdown(message[0].get('question'))
        # 回答を表示
        cols = st.columns(col_num)
        for col, m in zip(cols, message):
            col.chat_message(AI).markdown(m.get('answer'))

    # チャット入力フォーム
    question: str | None = None
    question = st.chat_input("質問を入力してください", key="question")
    if question:
        try:
            # チャット入力フォームを入力不可にする
            st.chat_input("回答をお待ち下さい...", key='disable', disabled=True)
            # 質問を表示
            st.chat_message(YOU).markdown(question)

            # AI Chatの処理を実行
            logger.info(f"start: app_chat_process:{id}")
            answers: list[ChatOutput] = [await app_chat_process(question, l, t) for l, t in zip(llms, selected_template)]
            logger.info(f"end: app_chat_process:{id}")

            messages.append(answers)
        except Exception as e:
            logger.error(f"Error:{str(e)}:{str(e.__class__)}")
            # エラーが発生したら、エラーをリストに追加する
            answer = ChatOutput(
                question=question,
                answer=f"エラーが発生しました:{str(e)}:{str(e.__class__)}",
            )
            messages.append([answer]*col_num)
        finally:
            # 画面の更新して結果を表示
            st.rerun()

if __name__ == '__main__':
    @ attach_decorator(google_oauth2_required, is_attached=GOOGLE_AUTH_ON)
    def start() -> None:
        asyncio.run(main())

    st.header(UI_TITLE)  # タイトルの表示
    start()  # type: ignore
