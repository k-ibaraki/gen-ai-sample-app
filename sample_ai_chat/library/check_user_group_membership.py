import logging
from urllib.parse import urlencode
import google.oauth2.credentials
import googleapiclient.discovery


# ログの設定
logger: logging.Logger = logging.getLogger(__name__)


def check_user_group_membership(group_id: str, mail: str, access_token: str) -> bool:
    """
    指定したユーザーが指定したグループに所属しているかどうかを確認する
    :param group_id: グループID
    :param mail: メールアドレス
    :param access_token: アクセストークン
    :return: 所属しているかどうか
    """
    try:
        # 認証情報を作成
        credentials = google.oauth2.credentials.Credentials(
            access_token,
        )
        service = googleapiclient.discovery.build(
            'cloudidentity', 'v1', credentials=credentials
        )
        query_params: str = urlencode(
            {"query": f"member_key_id == '{mail}'"}
        )

        request = service.groups().memberships().checkTransitiveMembership(
            parent=f"groups/{group_id}",
            query=query_params,
        )
        request.uri += "&" + query_params
        response = request.execute()
        return response['hasMembership']
    except Exception as e:
        logger.error(e)
        return False
