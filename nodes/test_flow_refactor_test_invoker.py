def test_flow_refactor_test_invoker_imports():
    import nodes.flow_refactor_test_invoker as m
    assert hasattr(m, "flow_refactor_test_invoker")
