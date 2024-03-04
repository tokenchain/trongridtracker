# !/usr/bin/env python
# coding: utf-8
# it is a way to simply solve the call method of the functions

CONSTRUCTOR_3882991212 = """
    uint256 initAmount,
    address _receiver,
    address genesis,
    address _techAddress,
    address _sellCommunityAddress,
    address _buyCommunityAddress,
    address _relAddress,
    address bot
"""


def solve_constructor(payload_methods: str, inputs: str):
    h = [y.strip().replace(',', '') for y in payload_methods.split("\n")]
    h = list(filter(None, h))
    # check for arguement lengths
    if len(inputs) != len(h) * 64:
        print("argument length is not matched. go back and double check")
        exit(1)

    for i in range(len(h)):
        c = inputs[i * 64:(i + 1) * 64]
        # print(c)
        head = h[i].split(" ")
        parameter = head[1]
        paratype = head[0]
        if h[i].startswith("uint256"):
            c = int(c, 16)

        if h[i].startswith("address"):
            c = "0x" + c.lstrip("0")

        print(f"{paratype} {parameter}={c};")

def solve_memory_array(payload_type: str, inptx: str):
    kp = inptx.strip().split("\n")
    hk = []
    for y in kp:
        if y != "":
            hk.append(y)
    for v in hk:
        solve_memory_array_single(payload_type, v)


def solve_memory_array_single(payload_type: str, inptx_: str):
    inptx_ = inptx_.strip()
    print(f"Memory Array types: {payload_type}")
    value_call_ux = inptx_[2:len(inptx_)]
    x_inputs = len(value_call_ux) / 64

    if int(x_inputs) == 0:
        print("there is no input")
    else:
        print(f"There are possibly {x_inputs} inputs")
        for i in range(int(x_inputs)):
            c = value_call_ux[i * 64:(i + 1) * 64]
            print(f"slot #{i}")
            print(c)

            if len(c.lstrip("0")) <= 40 and len(c.lstrip("0")) > 35:
                c = "0x" + c[64 - 40: -1]
                print(f"possible address {c}")

            elif (len(c.lstrip("0")) == 1 and c.lstrip("0") == "1") or str(0).zfill(64) == c:
                if str(0).zfill(64) == c:
                    print(f"possible bool  = 0; // in value or zero or False")
                else:
                    f = c.lstrip("0")
                    print(f"possible bool  ={f}; // in True")
                print("------------")

            else:
                c = int(c, 16)
                c18 = c / 10 ** 18
                print(f" ={c}; // in value")
                print(f" ={c18}; // from 18 decimals")
                print("------------")


def solve_possible_call(payload_methods: str, inputhex: str):
    inputhex = inputhex.strip().replace("\n", "")
    name_call = inputhex[:10]
    print(f"Call Method Name: {name_call}")
    value_call_ux = inputhex[10:len(inputhex)]
    x_inputs = len(value_call_ux) / 64
    h = [y.strip().replace(',', '') for y in payload_methods.split("\n")]
    h = list(filter(None, h))
    if int(x_inputs) == 0:
        print("there is no input")
    else:
        print(f"There are possibly {x_inputs} inputs")
        for i in range(int(x_inputs)):
            c = value_call_ux[i * 64:(i + 1) * 64]
            head = h[i].split(" ")
            parameter = head[1]
            paratype = head[0]
            print(f"slot #{i}")
            print(c)

            if h[i].startswith("address") or len(c.lstrip("0")) <= 40 and len(c.lstrip("0")) > 35:
                c = "0x" + c[64 - 40: -1]
                print(f"possible address {c}")

            elif h[i].startswith("bool") or (len(c.lstrip("0")) == 1 and c.lstrip("0") == "1") or str(0).zfill(64) == c:
                if str(0).zfill(64) == c:
                    print(f"possible bool {parameter} = 0; // in value or zero or False")
                else:
                    f = c.lstrip("0")
                    print(f"possible bool {parameter} ={f}; // in True")
                print("------------")

            elif h[i].startswith("uint256"):
                c = int(c, 16)
                c18 = c / 10 ** 18
                print(f"{paratype} {parameter} ={c}; // in value")
                print(f"{paratype} {parameter} ={c18}; // from 18 decimals")
                print("------------")


template_calls = """
            uint256 unknown_try1,
            uint256 unknown_try2,
            uint256 unknown_try3,
            uint256 unknown_try4,
            uint256 unknown_try5,
        """


def list_solver_batch(inputs: list):
    for i in inputs:
        solve_possible_call(template_calls, i)


def single_x(checker_x: str = ""):
    checker_x = "0x5bfce4120000000000000000000000000929c88dc5497fc0967f147d7fee6d29f0b46b1d00000000000000000000000000000000000000000000002b505a3ab7711c00000000000000000000000000000000000000000000000000000000000000000000"
    solve_possible_call(template_calls, checker_x)


if __name__ == '__main__':
    # constargue = "0000000000000000000000000000000000000000000000000000000005f5e0ff000000000000000000000000136f346cfa61c6ba1da40f3cf8bf970f3cc5d114000000000000000000000000f18a21316862f2fda8d8065bed7a0f217039c7c30000000000000000000000002daaad8072c724955d1ba6e1c9b806f90d62b91a000000000000000000000000aca82065e2619de31efdccf73018df14b16e7dc900000000000000000000000076bc62147271265b122bb00facbde4abff65feca000000000000000000000000a6e434e17aac7284bfd177aaab7247e04999daae000000000000000000000000758996b77b34cc28fc67dfd930008b4ec34a270b"
    # solve_constructor(formats, constargue)
    list_ac = [
        "0x29cef4470000000000000000000000009f1476967a1c6ed1b1da7677247adef5632286560000000000000000000000000000000000000000000000000000000000000001",
        "0x29cef4470000000000000000000000009f1476967a1c6ed1b1da7677247adef5632286560000000000000000000000000000000000000000000000000000000000000001",
        "0x29cef447000000000000000000000000c23ec883a0966caeabdaecabd580c2c1de96b4310000000000000000000000000000000000000000000000000000000000000001",
        "0x29cef4470000000000000000000000009f1476967a1c6ed1b1da7677247adef5632286560000000000000000000000000000000000000000000000000000000000000000",
        "0x29cef447000000000000000000000000c23ec883a0966caeabdaecabd580c2c1de96b4310000000000000000000000000000000000000000000000000000000000000000",
        "0x5a0943a5"
    ]
    list_solver_batch(list_ac)
