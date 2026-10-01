def test_web3_api(w3):
    assert w3.api.startswith("8")
