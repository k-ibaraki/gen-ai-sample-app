from typing import Any, Callable


def attach_decorator(
    decorator: Callable[..., Callable[..., Any]],
    is_attached: bool = True
) -> Callable[..., Callable[..., Any]]:
    '''デコレータを付与するかどうかを切り替えるデコレータ'''
    no_decorator: Callable[..., Any] = lambda x: x  # mypyのバグ(#10740)回避で変数に代入
    return decorator if is_attached else no_decorator
