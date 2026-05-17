"""会话 Cookie 安全策略。"""


def should_secure_session_cookie(explicit_secure: bool | None, request_scheme: str) -> bool:
    """判断会话 Cookie 是否需要 Secure 标记。"""
    if explicit_secure is not None:
        return explicit_secure

    # 自动模式必须跟随当前请求协议；HTTP 下设置 Secure 会让浏览器拒绝回传登录 Cookie。
    return request_scheme.lower() == "https"
