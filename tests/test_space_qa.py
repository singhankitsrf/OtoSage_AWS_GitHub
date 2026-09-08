from PIL import Image
from hf_space.backend import inspect


def test_no_checkpoint_never_produces_disease_probabilities():
    stats, probabilities, result = inspect(Image.new("RGB", (32, 32), "black"))
    assert stats["dark_pixel_fraction"] == 1
    assert probabilities == {}
    assert result["status"] == "awaiting_checkpoint"


def test_white_image_statistics():
    stats, _, _ = inspect(Image.new("RGB", (32, 32), "white"))
    assert stats["bright_pixel_fraction"] == 1
    assert stats["gradient_energy"] == 0
