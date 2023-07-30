from core.lib import GraphTron

if __name__ == '__main__':
    thread_hold = 10
    project_name = f"usdt-net-thread{thread_hold}"
    # dot.attr('node', shape='doublecircle')
    # dot.format = 'pdf'
    # dot.engine = 'dot'
    # dot.engine = 'neato'
    GraphTron().tron_analysis_read(project_name, thread_hold)
