from typing import TypedDict, Annotated, NotRequired, Required


class ChatInput(TypedDict):
    question: Annotated[str, "ユーザーが入力した質問文"]


class ChatOutput(ChatInput):
    answer: Annotated[str, "AIが回答する文章"]


class ChatQA(TypedDict):
    question: Required[ChatInput]
    answer: Required[ChatOutput]


class ModelDef(TypedDict):
    model: str
    location: NotRequired[str]
    temperature: NotRequired[float]
    tokens: NotRequired[int]
