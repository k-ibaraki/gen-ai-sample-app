import asyncio
import logging
import streamlit as st
from typing import Callable, Any
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import OAuth2Token

from sample_ai_chat.library.check_user_group_membership import check_user_group_membership
from sample_ai_chat.env import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_GROUP_ID

# ログの設定
logger: logging.Logger = logging.getLogger(__name__)


async def __get_authorization_url(client: GoogleOAuth2, redirect_uri: str) -> str:
    """
    Google OAuth2クライアントとリダイレクトURIを受け取り、認証URLを取得します。

    Parameters:
        client (GoogleOAuth2): Google OAuth2クライアント
        redirect_uri (str): リダイレクトURI

    Returns:
        str: 認証URL
    """
    authorization_url: str = await client.get_authorization_url(
        redirect_uri,
        scope=[
            "profile",
            "email",
            "https://www.googleapis.com/auth/cloud-identity.groups.readonly"
        ],
        extras_params={"access_type": "offline"},
    )
    return authorization_url


async def __get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str) -> OAuth2Token:
    token: OAuth2Token = await client.get_access_token(code, redirect_uri)
    return token


async def __get_user_mail(client: GoogleOAuth2, access_token: OAuth2Token) -> tuple[str, str]:
    id, mail = await client.get_id_email(access_token)  # type: ignore
    mail = mail if mail else ""
    return id, mail


def google_oauth2_required(func: Callable) -> Callable[[Any, Any], None]:
    """
    Google OAuth2認証を付与する関数デコレータです。

    Parameters:
        func (Callable): デコレートする関数

    Returns:
        Callable: デコレートされた関数
    """

    def wrapper(*args: Any, **kwargs: Any) -> None:
        client_id: str = GOOGLE_CLIENT_ID
        client_secret: str = GOOGLE_CLIENT_SECRET
        redirect_uri: str = GOOGLE_REDIRECT_URI

        client: GoogleOAuth2 = GoogleOAuth2(client_id, client_secret)
        authorization_url: str = asyncio.run(__get_authorization_url(
            client=client, redirect_uri=redirect_uri))

        if "token" not in st.session_state:
            st.session_state.token: OAuth2Token | None = None  # type: ignore

        if (st.session_state.token is not None) and \
                (not st.session_state.token.is_expired()):
            # tokenが存在して期限切れでない場合は処理を実行する
            func(*args, **kwargs)
            return

        try:
            # codeをクエリから取得する
            code: str = st.experimental_get_query_params()["code"]  # type: ignore
            # tokenを取得する
            token: OAuth2Token = asyncio.run(__get_access_token(
                client=client, redirect_uri=redirect_uri, code=code
            ))
            # tokenが期限切れの場合はエラーを出す
            if token.is_expired():
                st.error("Auth token is expired!!")
                raise RuntimeError("token expired!!")

            # ユーザーidとメールアドレスを取得する
            access_token: str = token['access_token']
            id, mail = asyncio.run(__get_user_mail(client=client, access_token=access_token))  # type: ignore

            # ユーザーが指定したグループに所属しているかどうかを確認する
            is_member: bool = check_user_group_membership(
                group_id=GOOGLE_GROUP_ID, mail=mail, access_token=access_token
            ) if GOOGLE_GROUP_ID else True

            if not is_member:
                st.error("You are not member!!")
                raise RuntimeError("token expired!!")

            # tokenをsessionに保存する
            st.session_state["token"] = token
            st.session_state["id"] = id
            func(*args, **kwargs)
        except:
            # tokenが取得できなかった場合はログイン画面を表示する
            st.markdown(
                f'## <a href="{authorization_url}" target="_self">Login</a>', unsafe_allow_html=True
            )

    return wrapper
