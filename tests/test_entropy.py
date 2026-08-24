from ml.src.inference import _normalized_entropy

def test_entropy_extremes():
    assert _normalized_entropy([1,0,0,0,0]) < 0.01
    assert _normalized_entropy([0.2,0.2,0.2,0.2,0.2]) > 0.99
