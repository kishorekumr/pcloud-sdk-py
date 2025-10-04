def test_files_namespace_exists():
    import pcloud
    pc = pcloud.PCloud()
    assert hasattr(pc, "files")
