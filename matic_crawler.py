from core.projects.work_7spring import ProjectPlan

if __name__ == '__main__':


    planner = ProjectPlan('sevenSpringsFinance')
    planner.setParams(
        target_address="0xD3C39cba6d3Afb3d304703F085Fc7A8249576C18",
        binding_tag="Register",
        bind_sig="0x4420e486"
    )
    # step 1, download the ledgers from the
    # planner.step1_scan_x()
    # step 2, download the ledgers from
    planner.step2()
