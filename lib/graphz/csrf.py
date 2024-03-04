import requests
import tls_client
from requests import Response

from lib.common.cookie import CookieExt
from lib.metamask import AppMetamask

verification_req = "https://sso.slowmist.com/en/web3_verification/?eth_address="
verification_verify = "https://sso.slowmist.com/en/web3_verification/"
login_page = "https://sso.slowmist.com/en/login/"


def mist_header(cookie: CookieExt = None, doc: bool = False):
    basic = {
        'Host': 'sso.slowmist.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0'

    }
    if doc is False:
        basic.update({
            'Content-Type': 'application/json',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://sso.slowmist.com/en/login/',
        })
    else:
        basic.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Upgrade-Insecure-Requests': '1',
        })

    if cookie is not None:
        basic.update({
            "Cookie": cookie.read_cookie()
        })

    basic.update({
        "TE": "trailers",
    })

    return basic


def post_doc_header(cookie: CookieExt):
    h = mist_header(cookie, doc=True)
    h.update({
        "Origin": "https://sso.slowmist.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "TE": "trailers",
    })

    print("========header debug")
    print(h)
    return h


def handle_res(r: Response):
    try:
        f = r.json()
        r.close()
        if "success" in f:
            if f["success"] is False:
                print(f["msg"])
                return False

        if "data" in f:
            return f["data"]

    except Exception as e:
        print(e)
        exit(0)


def init_mist(q: any, c: CookieExt = None):
    try:
        if isinstance(q, requests.Session):
            response = q.get(
                login_page,
                headers=mist_header(doc=True, cookie=c)
            )
        elif isinstance(q, tls_client.Session):
            response = q.get(login_page, headers=mist_header(doc=True, cookie=c))
        else:
            raise Exception("on client")
    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
    ) as e:
        print(f"req timeout. try again.")
        return False

    if response.status_code != 200:
        print(f"ERROR from server. got {response.status_code}")
        return False

    return response


def extract_value_html(line: str):
    key = 'value="'
    u = line.index(key)
    L = 0
    start = u + len(key)
    end = len(line)
    for L in range(start, end):
        if line[L:L] == '"':
            break

    return line[u + len(key): L - 1]


def get_csrfmiddlewaretoken(e: Response) -> str:
    lines = e.text.split("\n")
    res = ""
    for n in lines:
        if "csrfmiddlewaretoken" in n:
            res = extract_value_html(n)
            break
    return res


def request_nonce(q, address: str, cookie_mgm: CookieExt):
    try:

        if isinstance(q, requests.Session):
            response = q.get(
                f"{verification_req}{address}",
                headers=mist_header(cookie=cookie_mgm)
            )
        elif isinstance(q, tls_client.Session):
            response = q.get(
                f"{verification_req}{address}",
                headers=mist_header(cookie=cookie_mgm)
            )
        else:
            raise Exception("on client")

    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
    ) as e:
        print(f"req timeout. try again.")
        return False

    if response.status_code != 200:
        print(f"ERROR from server. got {response.status_code}")
        return False

    ok = handle_res(response)
    if isinstance(ok, bool):
        return False
    cookie_mgm.patch_cookie(response)
    return ok


def mist_get_key(q: requests.Session, cookie_mgm: CookieExt, key_dict: dict):
    try:

        if isinstance(q, requests.Session):
            response = q.post(
                verification_verify,
                data=key_dict,
                headers=post_doc_header(cookie=cookie_mgm),
                allow_redirects=False,
                verify=False
            )
        elif isinstance(q, tls_client.Session):
            response = q.post(
                verification_verify,
                data=key_dict,
                headers=post_doc_header(cookie=cookie_mgm),
                allow_redirects=False,

            )
        else:
            raise Exception("on client")

    except (
            requests.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
    ) as e:
        print(f"req timeout. try again.")
        return False

    if response.status_code == 302:
        print(f"SUCCESS and REDIRECT {response.status_code}")
        cookie_mgm.patch_cookie(response)
        return True
    elif response.status_code == 200:
        print(f"ERROR from server. got {response.status_code}")
        ok = handle_res(response)
        if isinstance(ok, bool):
            return False
        cookie_mgm.patch_cookie(response)
        return ok
    else:

        print("=======error=====")
        print(response.status_code)

        if "CSRF verification failed" in response.text:
            print("CSRF verification failed")
        else:
            print("=======unknown=====")
            print(response.content)
            print("=======unknown=====")
        return False


def get_cookie_token():
    # ss = requests.Session()
    ss = tls_client.Session(
        client_identifier="firefox_104",
        supported_signature_algorithms=[
            "ECDSAWithSHA256",
            "SHA256",
            "SHA384",
            "SHA512",
            "SHA256WithRSAEncryption",
            "SHA384WithRSAEncryption",
            "SHA512WithRSAEncryption",
            "ECDSAWithSHA384"
        ],
        supported_versions=["GREASE", "1.3", "1.2"],
        key_share_curves=["GREASE", "X25519"],
        cert_compression_algo="brotli",
        pseudo_header_order=[
            ":method",
            ":authority",
            ":scheme",
            ":path"
        ],
        connection_flow=15663105,
        header_order=[
            "accept",
            "user-agent",
            "accept-encoding",
            "accept-language"
        ]
    )
    ext_cookie = CookieExt("./data/mistcookie2")
    wallet = AppMetamask()
    wallet.from_new_random_private_key()
    init_res = init_mist(requests.Session())
    ext_cookie.new_cookie(init_res)

    init_res = init_mist(requests.Session(), ext_cookie)
    ext_cookie.patch_cookie(init_res)

    ext_cookie.cookie.put("RT",
                          '"sl=0&ss=lt8slbv2&tt=0&bcn=//684d0d45.akstat.io/&z=1&dm=slowmist.com&si=f4e62171-2837-421a-857c-eee5333bbd10"')
    csrf_middleware_token = get_csrfmiddlewaretoken(init_res)
    ok = request_nonce(requests.Session(), wallet.address, ext_cookie)
    if isinstance(ok, bool):
        return
    sign_message = ok["message"]
    print(sign_message)
    (signature, dic) = wallet.sign_message_test5(sign_message)
    if ext_cookie.has("csrftoken") is False:
        print("cookie has no csrftoken")
        return
    mist_get_key(ss, ext_cookie, {
        "signature": signature,
        "csrfmiddlewaretoken": csrf_middleware_token,
        "eth_address": wallet.address,
        "email": "",
        "code": "",
        "service": "",
    })
