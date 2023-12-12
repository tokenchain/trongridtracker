#!/usr/bin/python
import codecs
import os.path
import subprocess
from time import sleep
from typing import Union, Tuple
import requests

BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

from core.common.utils import folder_paths, JsonFileB


class SIGNATURE:
    first = "https://www.4byte.directory/api/v1/signatures/?ordering=created_at&format=json"
    page = "http://www.4byte.directory/api/v1/signatures/?format=json&ordering=created_at&page="
    status = "status.dat"
    content = "func_table.txt"


class EVENTS:
    first = "https://www.4byte.directory/api/v1/event-signatures/?ordering=created_at&format=json"
    page = "http://www.4byte.directory/api/v1/event-signatures/?format=json&ordering=created_at&page="
    status = "status_eve.dat"
    content = "event_table.txt"


def exitErr(message: str):
    print(message)
    exit(0)


def exitFinish():
    print("No new updates found.")
    exit(0)


class FourBytes:
    def __init__(self, base: Union[SIGNATURE, EVENTS]):
        self.status = base.status
        self.ftype = base
        self.folder = "data/hackdict"
        self.hashes = {}
        self.downloading = True
        self.session = requests.Session()
        self.start_page = self.page()

    def search(self, by_methods: str):
        print("from latest bank")
        self.sub_search(by_methods, self.ftype.content)
        # print("form archive bank")
        # self.sub_search(by_methods, "4bytes.txt")

    def sub_search(self, text: str, file: str):
        path = os.path.join(self.folder, file)
        result_index = []
        dumps = []
        print('... wait', end="\r")
        with open(path, 'r') as fp:
            # read all lines using readline()
            dumps = fp.readlines()
            for row in dumps:
                # check if string present on a current line
                # print(row.find(word))
                # find() method returns -1 if the value is not found,
                # if found it returns index of the first occurrence of the substring
                if row.find(text) != -1:
                    k = dumps.index(row)
                    print(f"Found: [{k}] <- {text}", end="\r")
                    result_index.append(k)
            fp.close()

        relist = [dumps[i].replace("\n", "") for i in result_index]
        print('Now this is the search result')
        print('=================================')
        for l in relist:
            print(l)

    def search_api(self, text: str) -> str:
        path = os.path.join(self.folder, self.ftype.content)
        result_index = -1
        dumps = []
        with open(path, 'r') as fp:
            dumps = fp.readlines()
            for row in dumps:
                if row.find(text) != -1:
                    result_index = dumps.index(row)
                    break
            fp.close()
        if result_index == -1:
            return ""
        detail = dumps[result_index].replace("\n", "")
        print(detail)
        detail_op = detail.split(" ")
        return detail_op[2]

    def last_id(self) -> int:
        path = os.path.join(self.folder, self.ftype.content)
        last = 0
        if os.path.isfile(path) is False:
            return last

        with open(path, 'r') as fp:
            dumps = fp.readlines()
            total = len(dumps)
            last = dumps[total - 1]
            last = last.split(" ")[0]
            fp.close()
        return int(last)

    def page(self) -> int:
        path = os.path.join(self.folder, self.status)
        f = open(path, 'r')
        page = f.read().strip()
        f.close()
        if page == "":
            return 0
        else:
            return int(page)

    def setpage(self, n: int):
        path = os.path.join(self.folder, self.status)
        f = open(path, 'w')
        f.write(str(n))
        f.close()

    def inc(self):
        h = self.page()
        if h == 0:
            self.setpage(1)
        else:
            self.setpage(h + 1)

    def prev(self):
        h = self.page()
        if h == 0:
            self.setpage(1)
        else:
            self.setpage(h - 1)

    def saveLine(self, line: str):
        path = os.path.join(self.folder, self.ftype.content)
        f = open(path, 'a')
        f.write(line)
        f.close()

    def scan(self):
        if self.start_page > 0:
            directory = f"{self.ftype.page}{self.start_page}"
        else:
            directory = self.ftype.first
        last_id = self.last_id()
        first_use = True
        while self.downloading:
            print(directory)
            try:
                r = self.session.get(
                    directory,
                    timeout=30,

                    proxies={
                        'http': 'http://127.0.0.1:7890',
                        'https': 'http://127.0.0.1:7890'
                    }

                )
                if r.status_code != 200:
                    print("try again since there are some errors")
                    continue
            except (
                    requests.ConnectionError,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectTimeout,
            ) as e:
                print(e)
                print("Try again since there are some errors in exception")
                sleep(3)
                continue

            response = r.json()
            contain = []
            first_id = 0
            p_last_id = 0
            for known_hash in response['results']:
                hex = known_hash['hex_signature']
                signature = known_hash['text_signature']
                id = known_hash['id']
                line = f"{id} {hex} {signature}\n"
                if first_use is True:
                    first_id = int(id)
                    first_use = False
                else:
                    p_last_id = int(id)

                contain.append(line)
            # print(f"last id: {last_id} , first id: {first_id}, p last id: {p_last_id}")
            # last id: 1080592 , first id: 1080567, p last id: 1080666
            if last_id >= p_last_id:
                exitFinish()

            for l in contain:
                id = int(l.split(" ")[0], 10)
                if id > last_id:
                    self.saveLine(l)

            directory = response['next']
            if directory is None:
                exitFinish()
            else:
                # the next loop here
                self.inc()


def massive_check(plist_op: list, n: str) -> bool:
    # print(plist_op)
    for lum_ling in plist_op:
        if n.find(lum_ling) > -1:
            return True
    return False


def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ.get("PATH", "").split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def errorStop(er: str):
    print(f"Error {er}")
    exit(9)


class heimdalldecompiler:
    """
    the full explanation in here https://github.com/Jon-Becker/heimdall-rs/wiki/modules
    you can add AI GPT to help as well.
    """

    def __init__(self):
        if which("heimdall") is None:
            errorStop("not exist, please install heimdall")
        self.sample_deployment_code = ""
        self.keyx = ""

    def setCode(self, txt_code: str, session_key: str = None):
        self.sample_deployment_code = txt_code.strip().replace("\n", "")
        if session_key is None:
            self.key = self.sample_deployment_code[44:70]
        else:
            self.key = session_key

    def disect(self):
        try:
            path = f"data/source/{self.key}"

            result = subprocess.run(
                f"heimdall decompile {self.sample_deployment_code} -vvv -d --include-sol --output {path}",
                shell=True, check=True, text=True, capture_output=True,
            )
            print(GREEN)
            print(result.stdout)
            print(WHITE)
            print("--------------------")
            print(path)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"heimdall decompile is failed: \n {exc.stderr}") from exc


class debubdecompiler:
    def __init__(self):
        self.api = "api.dedaub.com"
        self.session = requests.Session()
        self.sample_deployment_code = ""

    def set0xAddress(self, contract: str):
        print("this feature is not yet complete.")
        self.discovery_contract_address = contract
        exit(1)

    def setCode(self, txt_code: str):
        self.sample_deployment_code = txt_code.strip().replace("\n", "")

    def read_source(self, sourcecode: str) -> Tuple[list, list, list]:
        lines = sourcecode.split("\n")
        lines = [y.strip() for y in lines]
        unknown_func = []
        known_func = []
        storages = []
        for p in lines:
            if p.startswith("//"):
                continue
            if p.startswith("/*"):
                continue
            if "__function_selector__" in p:
                continue
            if "STORAGE[0x" in p:
                storages.append(p)

            if p.startswith("function"):
                words_list = p.split(" ")
                if "public" in words_list:
                    line = words_list[1]
                    if words_list[1].startswith("0x"):
                        removed = line.replace("()", "")
                        removed = removed.replace("(address", "")
                        removed = removed.replace("(uint256", "")
                        removed = removed.replace("(address[]", "")
                        line = removed.replace("(uint256[]", "")
                        unknown_func.append(line)
                    else:
                        public_index = p.index("public")
                        line = p[9:public_index]
                        line = line.strip()
                        if line == "()":
                            continue
                        c1 = p.index("(")
                        c2 = p.index(")")

                        list_y_cp = p[c1 + 1:c2]
                        func_call = p[0:c1].replace("function ", "")
                        p1 = [y.strip().split(" ")[0] for y in list_y_cp.split(",")]

                        resign = ",".join(p1)
                        line = f"{func_call}({resign})"
                        known_func.append(line)

        return (known_func, unknown_func, storages)

    def forfinalfunc(self, p1ist: list) -> list:
        newcapture = []
        for p in p1ist:
            c1 = p.index("(")
            c2 = p.index(")")
            list_y_cp = p[c1 + 1:c2]
            func_call = p[0:c1].replace("function ", "")
            p1 = [y.strip().split(" ")[0] for y in list_y_cp.split(",")]

            p2 = [f"{k} memory" if k[len(k) - 2:len(k)] == "[]" else k for k in p1]
            # print(p2)
            resign = ",".join(p2)
            line = f"{func_call}({resign})"
            newcapture.append(line)

        return newcapture

    def check_unknown_func(self, unknown_func: list) -> Tuple[list, list]:
        print("now hack on unknown func")
        unknown_func_explain = []

        for h in unknown_func:
            f = FourBytes(SIGNATURE())
            unknown_func_explain.append(f.search_api(h))

        lines = []
        lines.append("### The closed source code brief overview")
        lines.append("====================================")
        for u in range(len(unknown_func)):
            line = unknown_func[u] + " --> " + unknown_func_explain[u]
            lines.append(line)

        return (lines, unknown_func_explain)

    def add_explain_known_func(self, lines: list, known_func: list) -> list:
        for h in known_func:
            lines.append(h)
        lines.append("")
        return lines

    def write_storage_section(self, md: list, storage_lis: list) -> list:
        md.append("### Allocation of storage locations")
        md.append("====================================")
        md.append("")
        md.append("Data structures and variables inferred from the use of storage instructions")
        md.append("")
        for s in storage_lis:
            md.append(s)
        md.append("")
        return md

    def write_interface(self, md: list, key: str, known_func: list, explained: list) -> list:
        md.append("### to develop a hack interface please consider the below:")
        md.append("")
        md.append("====================================")
        md.append("")
        md.append("```solidity")
        md.append(f"interface I{key} {{")
        md.append("")

        both_func = []
        for y in known_func + explained:
            if y != "":
                both_func.append(y)
        both_func = self.forfinalfunc(both_func)
        # print(both_func)
        """for h in both_func:
            f = FourBytes(SIGNATURE())
            f.search_api(h)
            signer = f.search_api(h)
            print(signer)
        """

        for n in both_func:
            if massive_check([
                "totalSupply",
                "balanceOf",
                "decimals",
                "approv",
                "getPrice",
                "totalCommission",
            ], n) is True:
                md.append("   function " + n + " external view returns (uint256);")
            elif massive_check([
                "getPair",
                "owner",
                "uniswapV2Router",
                "tokenA(",
                "tokenB(",
                "tokenC(",
            ], n) is True:
                md.append("   function " + n + " external view returns (address);")
            elif massive_check([
                "isAdmin"
            ], n) is True:
                md.append("   function " + n + " external view returns (bool);")
            elif massive_check([
                "name()", "symbol()"
            ], n) is True:
                md.append("   function " + n + " external view returns (string memory);")
            else:
                md.append("   function " + n + " external;")

        md.append("")
        md.append("}")
        md.append("```")

        return md

    def save_files(self, key: str, payload: dict, mdlines: list):
        folder = f"data/source/{key}"
        folder_paths([folder])
        path_bytex = os.path.join(folder, "byte.txt")
        path_dis = os.path.join(folder, "disassembled.txt")
        path_tac = os.path.join(folder, "tac.txt")
        path_yul = os.path.join(folder, "yul.txt")
        path_src = os.path.join(folder, "source.txt")
        path_raw = os.path.join(folder, "raw.json")
        path_readme = os.path.join(folder, "Overview.md")

        self.writeto(path_bytex, payload.get("bytecode"))
        self.writeto(path_dis, payload.get("disassembled"))
        self.writeto(path_tac, payload.get("tac"))
        self.writeto(path_yul, payload.get("yul"))
        self.writeto(path_src, payload.get("source"))

        cache = JsonFileB(path_raw)
        cache.dumpdict(payload)

        self.writeMd(path_readme, mdlines)

    def writeto(self, path: str, content: str):
        file_object = open(path, 'w')
        file_object.write(content)
        file_object.close()

    def writeMd(self, path: str, mdlines: list):
        file_object = open(path, 'w')
        file_object.write("\n".join(mdlines))
        file_object.close()

    def disect(self) -> str:
        if self.sample_deployment_code == "":
            print("no op code set")
            exit(1)
        self.request_resourcecode_ready()
        key = self.request_resourcecode_request_key(self.sample_deployment_code)
        payload_done = self.request_sourcecode_payload(key)

        (kwn, unkwn, ss) = self.read_source(payload_done.get("source"))
        (md, expln) = self.check_unknown_func(unkwn)
        md = self.add_explain_known_func(md, kwn)
        md = self.write_storage_section(md, ss)
        md = self.write_interface(md, key, kwn, expln)
        self.save_files(key, payload_done, md)
        ddh = heimdalldecompiler()
        ddh.setCode(self.sample_deployment_code, key)
        ddh.disect()

        return key

    def request_resourcecode_ready(self):
        try:
            r = self.session.request(
                method="OPTIONS",
                url=f"https://{self.api}/api/on_demand/",
                headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip,deflate,br",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive",
                    "Origin": "https://library.dedaub.com/",
                    "Referer": "https://library.dedaub.com/",
                    "Access-Control-Request-Headers": "content-type",
                    "Access-Control-Request-Method": "POST",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0"
                }
            )

            if r.status_code != 200:
                print(f"check status is  {r.status_code}")
                sleep(3)
                isOk = str(r.content)
                if isOk == "OK":
                    print("the request is ready.")
                self.request_resourcecode_ready()

            if r.status_code == 200:
                isOk = str(r.content)
                if isOk == "OK":
                    print("the request is ready.")

        except (
                requests.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectTimeout,
        ) as e:
            print(e)
            print("Try again since there are some errors in exception")
            sleep(3)
            self.request_resourcecode_ready()

    def request_sourcecode_payload(self, req_token: str) -> dict:

        try:
            r = self.session.get(
                f"https://{self.api}/api/on_demand/decompilation/{req_token}",
                timeout=30,
                headers={
                    "Referer": "https://library.dedaub.com/"
                },

                proxies={
                    'http': 'http://127.0.0.1:7890',
                    'https': 'http://127.0.0.1:7890'
                }



            )

            if r.status_code != 200:
                if r.status_code == 404:
                    print(f"will need to wait for a while as the result is not ready yet. {req_token}")
                    sleep(5)
                else:
                    print(f"the decom is not ready... will try again {req_token} {r.status_code}")
                    sleep(3)
                    print(r.content)
                self.request_sourcecode_payload(req_token)

            if r.status_code == 200:
                if "bytecode" in r.json():
                    return r.json()
                else:
                    return self.request_sourcecode_payload(req_token)

        except (
                requests.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectTimeout,
        ) as e:
            print(e)
            print("Try again since there are some errors in exception")
            sleep(3)
            self.request_sourcecode_payload(req_token)

    def request_resourcecode_request_key(self, source_opcod: str) -> str:
        try:
            r = self.session.post(
                f"https://{self.api}/api/on_demand/",
                json={
                    "hex_bytecode": source_opcod
                },
                timeout=30,

                proxies={
                    'http': 'http://127.0.0.1:7890',
                    'https': 'http://127.0.0.1:7890'
                }


            )

            if r.status_code != 200:
                sleep(3)
                print(f"try again since there are some errors {r.status_code}")
                print(r.content)
                return self.request_resourcecode_request_key(source_opcod)

            if r.status_code == 200:
                return codecs.decode(r.content, 'utf-8').replace("\"", "")

        except (
                requests.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectTimeout,
        ) as e:
            print(e)
            print("Try again since there are some errors in exception")
            sleep(3)
            self.request_resourcecode_request_key(source_opcod)
