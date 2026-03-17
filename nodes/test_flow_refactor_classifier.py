def test_flow_refactor_classifier_imports():
    import nodes.flow_refactor_classifier as m
    assert hasattr(m, "handle")
