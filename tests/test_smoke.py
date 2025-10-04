def test_imports():
    import pcloud
    assert hasattr(pcloud, "PCloud")
    assert isinstance(pcloud.__version__, str)
