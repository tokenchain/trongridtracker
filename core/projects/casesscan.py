from core.graphz.mistapi import enable_USDT_BEP20, enable_USDT_TRC20, enable_DAI_POLYGON, enable_USDT_ERC20, \
    enable_TRX_TRON
from core.graphz.mistgraph import MistAnalysis


def blockgpt():
    ma = MistAnalysis("blockgpt")
    # making the income list
    # ma.setThreadHoldUSD(100).setUseTo().start_develop_source_sheet()
    # make the chart only
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0xae6fb728791fc453d2ad44c7533e57bac313aa51",
        "0x31414636b1ba7be4928b48df23678e769d9a5319",
        "0xa6ade9dfa3245b0790747b4f98cfef1e6c6f25c9",
        "0xe756eb7cce2b5957716740937107439cbf2726fd",
        "0xe0c9e9a8887f918f7adca40048e46cdb64bff03f",
    ])
    ma.setName("blgpt")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def blockgpt02():
    ma = MistAnalysis("blockgpt")
    # making the income list
    # ma.setThreadHoldUSD(100).setUseTo().start_develop_source_sheet()
    # make the chart only
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0x68e8974C03e10DEd9112f1C82553dEC4b73F3366",
        "0x92bA5e411fe6b6667A8870549d0A6692d815ED20",
        "0xC6E19707DFB139591628B28b3cd06D778bFf9eFE",
        "0x70CAb6e899997573838aefac4e164F7F17f9D076",
        "0x1b2E442A72632E2b5Cbb9fC795e0C3740397e0Bd",
        "0xce980670ab22A68949b36b9B8Af03Cd5724908Bb",
        "0x87f19dEE1378fB43deE1c6414dbEaaE50198E1c2",
        "0x7923AC375f674Ab888996607eEd74237a0a329b8",
        "0x984CD6f3C1D43fAf2aB2F454adD44Ff0b3B5398c",
        "0xD320a27128571a0ee849d93F471799056e5C4f54",
        "0x27a180f842397D94EDB77467464D3ef5B112364C",
        "0x31414636b1ba7be4928b48df23678e769d9a5319",
        "0x3F2A792A74d990ad7Fc3dE075B4de4153DF11fd4",
        "0x792e26AF14f0024eC3d9EC9D8A8DDc753B9A94ba",
        "0x30fa7D521CB933550DEf22c6daDE605ff24b3724",
        "0x8f06F9246bA384fC585782a00172BAA10d9B185b",
        "0xf57C6AbbF6F186e807DA8Fe4c5EB30452FA92Fc0",
        "0xa6ade9dfa3245b0790747b4f98cfef1e6c6f25c9",
        "0x88a5B68B7eae6522fF65853F0486D36A65E3B9d6",
        "0xCF9FC77C63E97970e1E23c83111050C99f9eF21C",
        "0x48A88555Cb8C6B2e659D47583205f84c95a6C9b2",
        "0x41F824f08Fb64EcCcb166595789Eb41F6A40177F",
        "0xe756eb7cce2b5957716740937107439cbf2726fd",
        "0x1854494543ade343485f8c17672b13e5dd07b40e",
        "0x897d523dF6EBa1266977c7621C395c786E764BDd",
        "0x5970fe404a0cb225f598305f6fe71988b6c45a51",
        "0x528c9D485F8DbBa74B70EFa8f77fdc9c8bB800a5",
        "0x0b9336e896a91a7368efc1f5c545200e48b4af1a",
        "0x20e18107183527DaCfEF435976A1fa066036686e",
        "0xD78dA5EB7021557e7c1C21b9F03B14659D67B068",
        "0x10d5705D9849bADF4FF33C9cC676e309e48dDAdA",
        "0x823E7C6D1354216cBe8A45755265f8438054a922",
        "0x3AF9980246bB00CbFf49C89245Cb96E1a0c764b6",
        "0xEE8B097714aBAdB599F6859cB595F124eC95e735"

    ])
    ma.setName("bosskeep_shown")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().doIndependChart().startPlot()


def blockgpt03():
    enable_USDT_TRC20()
    ma = MistAnalysis("blockgpt")
    bar_small = 1
    ma.acquireFromAddress([
        "TNhm6PKJe18h4XLRXvPtkcuZ9Ne89zhAD7"
    ])
    ma.setName("trc20chase")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _7spring_bsc1():
    enable_USDT_BEP20()
    # /Users/hesdx/Documents/b95/trackerfactory/data/sevenSpringsFinance
    ma = MistAnalysis("sevenSpringsFinance")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0x07971aD8891d85cdb0a98EB68bf48250135FB21b",
        "0xD3C39cba6d3Afb3d304703F085Fc7A8249576C18",
        "0x063A3e51A1c2237B26977EBA1f15Ed786D1e7b44"
    ])
    ma.setName("7spr")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _why_bsc1():
    enable_USDT_BEP20()
    # /Users/hesdx/Documents/b95/trackerfactory/data/sevenSpringsFinance
    ma = MistAnalysis("WHY")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0x2d6D06Fba0b2250f34a34b40492b08828B519618"
    ])
    ma.setName("whyfund")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _7spring_tron():
    enable_USDT_TRC20()
    ma = MistAnalysis("sevenSpringsFinance")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "TGUELnHnGKUVXcDKWfWJ3hnY9iurnNqW1f",
        "TEorZTZ5MHx8SrvsYs1R3Ds5WvY1pVoMSA"
    ])
    ma.setName("7sprtron")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _xpersonal():
    enable_USDT_TRC20()
    ma = MistAnalysis("BRCLIFE")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "TSttziLWumMhGrWiT4AVUXNWQ1i6sx2epb"
    ])
    ma.setName("wallet1")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _xpersonal2():
    enable_USDT_BEP20()
    ma = MistAnalysis("BRCLIFE")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0xb61beac6ba7edc69a28ef1b7ada8bd0f7787f36f",
        "0xa0bbf54e9de4246d70671d8365442729906bb5a4",
    ])
    ma.setName("wallet2")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _utok():
    enable_USDT_TRC20()
    ma = MistAnalysis("UTOK")
    bar = 10000
    bar_small = 1000
    ma.acquireFromAddress([
        "TEvZrANgMc6zED7Ypvu6EcWGyDqwCzKrNF",
        "TBeNRNTwhtQyUHFgNuBFKhMDGqkpwb2GjU",
        "TATgZCTEQspxnBamyM191SMorJprc5UXwW",

        "TJB5MhgwLpXwyTD3UEFKoCfk13EBdZncnL",
        "TM1swJFciwtpvhGbLVHMmMvnsXnHiqq6yn",
        "TCXFxvduZYhFqVWvXYTdZdh8dGSERzAxC8",
        "TYQiu3JArb8ceNVes67WJX1wZorLq4DrM7",
        "TEs9djP5KTnCBTB47VTTfADbtxc6AYr2no",
        "TMR5xsP5ruTjtyqqWyktCAuo71wGELcfgF",
        "TMDg4APkbURr89tcUrcj3HMXJxqELy3XSW",
        "TMn4NKUsRPk3vKca3nZ4oPEipRSSepnEGx",
        "TSeqZ8jWbzEoSLFUt9abbKnoMbs5atvg61",
        "TEaeWA1Az5eQcxPQt4GbbdBpAbJRGSRLWf",
        "TTUvY93dpyJ5sbpywYphgYpJs71mQ5XRCW",
        "TLWkXyy7Q9TJ1YcxqUyAB8V1ntbX6tiZYS",
        "TQUL6dZtUccmV6Zo8crT3zgifSgU3g1JQu",
        "TXX7nWxXVwtsEBXiVPfUdvDrPnNfTSc9YV",
        "TUpHuDkiCCmwaTZBHZvQdwWzGNm5t8J2b9",
        "TU9SL2uYiSwhimGtsatjmFM8bVuNn3nxy9",
        "TXX7nWxXVwtsEBXiVPfUdvDrPnNfTSc9YV",
        "TYhLXsK5mdwG7FfjpiDEFdRpDeGtSUWorA",
        "TPGarpAXcA1RyS9Bz85LFQW2G6tFpX658v",
        "TUL66ct2N5tZAWWRsHHqthJQ6s7C37hjbV",
        "TCH1hgmtErjC9YDvQq7yzPnATcH21HQNiC",
        "TEkEuVUUxMAWz9R5hFHnpYzChBdYiS5Qps",
        "TY9PZ1j37Xo5k1xp2nToicpwC9fr53Nyic",
        "TXqg8fCWfrsU9SBgLerCAjCds8QXCUk777",
        "THGjrRXR9nfyS9r3wrvLq8D3MZi4x4BYbY",
        "TCQn14Ew3EzTn7E4nQYXUR9knS9KeTszB8",
        "TGaBYhP5kJfjTzBPWiXZKeceBoeyGSEfCn"

    ])
    ma.setName("market2")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _utok_21():
    enable_USDT_TRC20()
    # /Users/hesdx/Documents/b95/trackerfactory/data/sevenSpringsFinance
    ma = MistAnalysis("UTOK")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0x5FAC9F405f651609FEb36C3602D8cc0718784544"
    ])
    ma.setName("_liuxing")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def _utok_22():
    enable_USDT_TRC20()
    # /Users/hesdx/Documents/b95/trackerfactory/data/sevenSpringsFinance
    ma = MistAnalysis("UTOK")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "TH7LRJqbF83AGjQLKuqmu2SyFBW4hmmU4o"
    ])
    ma.setName("_liuxing4o")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def thief_001():
    enable_USDT_TRC20()
    ma = MistAnalysis("thief_001")
    bar = 10000
    bar_small = 10
    ma.acquireFromAddress([
        "TRdcYFtX3CSoxiNWrrP9jyse7EhLW18HdE",
        "TJcf5AankrN2DXBMSv8XYGUnHVW6EkYerM",
        "TKdoaSZd4oMN2Mytx4fw73oiwjBv9ssdLW"
    ])
    ma.setName("theif_wallet_x")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def nancahngnew():
    enable_USDT_BEP20()
    ma = MistAnalysis("南昌新项目")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0x6E11a6A9eBfd87f7168CAB4DcD360270919CF4B7"
    ])
    ma.setName("nanchangenew1")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def xpansion_1():
    enable_USDT_BEP20()
    ma = MistAnalysis("XChain")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0xA0c44d4D0bAB0b5d48DE09e1F82365c4227Fa8dd"
    ])
    ma.setName("xpansion")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def tankecloud01():
    enable_USDT_BEP20()
    ma = MistAnalysis("TANKECLOUD")
    bar = 10000
    bar_small = 100
    ma.acquireFromAddress([
        "0x1eD5685F345b2fa564Ea4a670dE1Fde39e484751"
    ])
    ma.setName("swft")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def v8gameble1():
    enable_USDT_BEP20()
    ma = MistAnalysis("V8")
    bar = 10000
    bar_small = 10
    ma.acquireFromAddress([
        "0xa95df9c5bDE70D062639c88939c4542f2CF79608"
    ])
    ma.setName("deposit_check")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def keepswap01():
    enable_USDT_BEP20()
    ma = MistAnalysis("KEEPSWAP")
    bar = 10000
    bar_small = 10
    ma.acquireFromAddress([
        "0xd85d2A0223820358527Cde74e2a454F2265f612e",
        "0x3fb90fd41fdaad32950ed9ef896e170b68fb3911",
        "0xb7F98fd9BC813cd0BDcfef089eEd75AF510B7d53",
        "0xf417d085FdF9CfAfA9Ab92ae68bFC1e22f534B7F",
        "0x84484C28Cd1318B3e25d24fd9A0610286291Ed2D",
        "0x3223667748f89819C431563a0D61bB84c16Cbb73",
        "0x871ea22ad5888B05c94D18c651b18a19bF33A575",
        "0x9eCea686B4E103Fb244DeF7391f8A4A7284Ba5EF",
        "0x5d8E7699A09C1716a9Fe822c172bA2797AF03F85",
        "0x1E9339Ac16B613a69118368d8655F5F31626ec43",
        "0x96d6bf90f2478080B68c994a8AF4f12541CA4Ec0",
    ])
    ma.setName("deposit_flow")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def aveBSC():
    enable_USDT_BEP20()
    ma = MistAnalysis("AVE.SOURCE")
    bar_small = 299
    ma.acquireFromAddress([
        "0xBe88292826d0d763423195688bdE1AAdCeAf8c25"
    ])
    ma.setName("cases_oct")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def bh_tang():
    enable_USDT_BEP20()
    ma = MistAnalysis("BH")
    bar_small = 100
    ma.acquireFromAddress([
        "0x651FDBa9dA543d139b6a901626d7D634EAaf7581",
        "0xcb376a6468cbf7d7b0291a1c63acd132c829fe89",
        "0x5a5dfe88345851628ed633dd3121fbcd7a99c4e8",
        "0xbf3881df0167e0d0845203e16e9ede8e433fd973",
        "0xdbc27f2e9a2532b15c848f4ae408cfe8beb14959"
    ])
    ma.setName("tang_payment")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def bh_tang1():
    enable_USDT_BEP20()
    ma = MistAnalysis("BH")
    bar_small = 100
    ma.acquireFromAddress([
        "0xcb376a6468cbf7d7b0291a1c63acd132c829fe89",
        "0xa3b80674B2fBaD3005a0Aa89EA15525B31897918",
        "0xa1119d8518f5f399790DB4C5cC65353A4765B054",
        "0x5B1Fa4D010f7f24E05A989EE1d98a88Cd64867c9",
        "0x5521636D1D42f9635eA80c56b40295DA1A7E30BF",
        "0xde93d042A7B7459163D93A76Ddc05046a67750e9"
    ])
    ma.setName("tang_collection1")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def bh_sun1():
    enable_USDT_BEP20()
    ma = MistAnalysis("BH")
    bar_small = 10
    ma.acquireByFile("sun.md")
    ma.setName("sun_collection")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def bh_holders_attack():
    enable_USDT_BEP20()
    ma = MistAnalysis("BH")
    bar_small = 10
    ma.acquireByFile("bh_holders.md")
    ma.setName("bh_holders")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def DGEX01():
    enable_USDT_BEP20()
    ma = MistAnalysis("DGEX")
    bar = 10000
    bar_small = 299
    ma.acquireFromAddress([
        "0x52cc1824d875eb2bba60c819d65d947889d5390e",
        "0xb17cdad08adb732f2fdb3b185c6e4c2c552a0f53"
    ])
    ma.setName("first_one")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def aveETH():
    enable_USDT_ERC20()
    ma = MistAnalysis("AVE.SOURCE")
    bar = 10000
    bar_small = 299
    ma.acquireFromAddress([
        "0xBe88292826d0d763423195688bdE1AAdCeAf8c25"
    ])
    ma.setName("cases_erc20")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def ptahdao():
    enable_USDT_TRC20()
    ma = MistAnalysis("PTAHDAO")
    bar_small = 100
    ma.acquireFromAddress([
        "TTN8MWwBoJ8c9fnBHLjEncmRp6vuGedpvs"
    ])
    ma.setName("general-A")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()


def laos_targets():
    enable_TRX_TRON()
    ma = MistAnalysis("LAOS")
    bar_small = 100
    ma.acquireFromAddress([
        "TRWkuqvtjc6FXsbJhpnJNG7bB6CAwu6dfM",
        "TLX8rraf9ewiMMkjcUmAfnRFmhWDz5qcLi",
        "TM1zzNDZD2DPASbKcgdVoTYhfmYgtfwx9R",
        "TWVzdmHWPVB4GZYFToJybN4NnbVTXqjYSc",
        "TQdASQpvLcp7Z2sFUiRbcw3sN2ajn8CVBz",
        "TSXJB795JfL4FdFvUQEcF3TDxhq3yYjhiH",
        "TQdASQpvLcp7Z2sFUiRbcw3sN2ajn8CVBz",
        "TE4czw9BDjXHpafQbK6TKS5X4uRR1FeJti",
        "TTkuswejGCWEQzUeRDJ5vekD8yww3JxWyd",
        "TGEWqYgmAChQkER4HsPZkPKt5ER4kBmqgy"
    ])
    ma.setName("uid-55821814")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()

def laos_usdt_targets():
    enable_USDT_TRC20()
    ma = MistAnalysis("LAOS")
    bar_small = 100
    ma.acquireFromAddress([
        "TRWkuqvtjc6FXsbJhpnJNG7bB6CAwu6dfM",
        "TLX8rraf9ewiMMkjcUmAfnRFmhWDz5qcLi",
        "TM1zzNDZD2DPASbKcgdVoTYhfmYgtfwx9R",
        "TWVzdmHWPVB4GZYFToJybN4NnbVTXqjYSc",
        "TQdASQpvLcp7Z2sFUiRbcw3sN2ajn8CVBz",
        "TSXJB795JfL4FdFvUQEcF3TDxhq3yYjhiH",
        "TQdASQpvLcp7Z2sFUiRbcw3sN2ajn8CVBz",
        "TE4czw9BDjXHpafQbK6TKS5X4uRR1FeJti",
        "TTkuswejGCWEQzUeRDJ5vekD8yww3JxWyd",
        "TGEWqYgmAChQkER4HsPZkPKt5ER4kBmqgy"
    ])
    ma.setName("uid-usdt-55821814")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()

def ppd_analysis():
    enable_USDT_TRC20()
    ma = MistAnalysis("PDD")
    bar_small = 100
    ma.acquireFromAddress([
        "TEZVBjomubVSn41hvenJ8KyHEzEZCeuC7B"
    ])
    ma.setName("firstblood-pdd")
    ma.setThreadHoldUSD(bar_small).setEnableSideNote().startPlot()
