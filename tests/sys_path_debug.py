def test_sys_path():
    import sys
    print('PYTHON:', sys.executable)
    print('SYSPATH:', sys.path)
    assert sys.executable
    assert isinstance(sys.path, list)
