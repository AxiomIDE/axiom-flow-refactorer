def test_flow_refactor_analyser_imports():
    import nodes.flow_refactor_analyser as m
    assert hasattr(m, "flow_refactor_analyser")
