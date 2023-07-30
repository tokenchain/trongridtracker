from core.mistgraph import MistAnalysis

if __name__ == '__main__':
    ma = MistAnalysis()
    # making the income list
    # ma.setThreadHoldUSD(100).setUseTo().start_define_incoming_people()
    # make the chart only
    bar = 10000
    bar_small = 100
    ma.setThreadHoldUSD(bar).startPlot()