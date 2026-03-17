from nodes.flow_refactor_analyser import flow_refactor_analyser


def test_flow_refactor_analyser_imports():
    assert callable(flow_refactor_analyser)
