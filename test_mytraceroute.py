from mytraceroute_udp import traceroute


def test_func1(capsys):
    traceroute('www.google.com', 5.0, 64)
    captured = capsys.readouterr()
    assert "ms" in captured.out


def test_func2(capsys):
    traceroute('o2.de', 5.0, 64)
    captured = capsys.readouterr()
    assert "Slowest" in captured.out
