from core.projects.did import ProjectPlan

if __name__ == '__main__':
    pp = ProjectPlan('DID')
    pp.setParams(
        target_address="0xc63c76e846d1a1d37415db4472cf3ae59a47090b",
        binding_tag="Set Referrer",
        bind_sig="0xa18a7bfc"
    )
    pp.count_involves()
