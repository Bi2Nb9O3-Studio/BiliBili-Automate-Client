
import os


def ensure_path(path):
    """
    确保指定的路径存在。如果路径不存在，则创建该路径。

    :param path: 要确保存在的路径，可以是相对路径或绝对路径。
    :return: 传入的路径，无论该路径是原本就存在还是新创建的。
    """
    # 检查指定的路径是否存在
    if not os.path.exists(path=path):
        # 若路径不存在，则递归创建该路径，exist_ok=True 表示如果目录已存在不会抛出异常
        os.makedirs(path, exist_ok=True)
    # 返回传入的路径
    return os.path.abspath(path)


def ensure_file(file):
    if not os.path.exists(file):
        f = open(file, "w")
        f.close()
    return os.path.abspath(file)

def setup_session():
    """
    创建并返回一个新的 requests.Session 对象。

    :return: 一个新的 requests.Session 对象。
    """
    import requests
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    })
    return session