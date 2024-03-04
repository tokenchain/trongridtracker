from lib.etherscan import TokenHolder, BscScan


def nova():
    pp = TokenHolder('NOVA')
    pp.setTargetAddress('0x5Ad080A6E129D62686eFE0D696B443cd43BeAC1d')
    pp.setEndpointBase(BscScan())
    pp.retrieve_pages_token_holders()


def did():
    pp = TokenHolder('DID')
    pp.setTargetAddress('0xF078d59Ae13cc3CC5448Eae06a691e5d66744DA8')
    pp.setEndpointBase(BscScan())
    pp.retrieve_pages_token_holders()


if __name__ == '__main__':
    pp = TokenHolder('DID')
    pp.setTargetAddress('0xF078d59Ae13cc3CC5448Eae06a691e5d66744DA8')
    pp.setEndpointBase(BscScan())
    pp.retrieve_pages_token_holders()
