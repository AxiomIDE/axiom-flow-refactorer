from nodes.graph_fetcher import graph_fetcher


def test_graph_fetcher_imports():
    assert callable(graph_fetcher)
