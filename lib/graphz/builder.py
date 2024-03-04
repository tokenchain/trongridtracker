import graphviz


def build_bot_tpl(name: str, iter: int):
    dot = graphviz.Digraph(
        f"{name}-{iter}",
        comment='Blockchain address tracking',
        engine='dot',
        format='pdf'
    )
    dot.attr(
        ordering='out',
        showboxes='true',
        concentrate='true',
        compound='true',
        rankdir='LR',
        searchsize='10',
        ranksep='4.2 equally',
        size='1000,925'
    )
    return dot
