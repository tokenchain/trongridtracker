from core.projects.work_lizfinance import ExcelGraphviz

if __name__ == '__main__':
    ma = ExcelGraphviz()
    # making the income list
    ma.start_chart("lizfinance.xlsx")
