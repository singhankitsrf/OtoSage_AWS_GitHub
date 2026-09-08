import pandas as pd
import pytest
from ml.src.preprocess import prepare


def test_cross_label_duplicate_fails():
    frame = pd.DataFrame(
        [
            {
                "path": "a.jpg",
                "filename": "a.jpg",
                "class_name": "A",
                "sha256": "same",
                "readable": True,
                "width": 1,
                "height": 1,
                "mode": "RGB",
            },
            {
                "path": "b.jpg",
                "filename": "b.jpg",
                "class_name": "B",
                "sha256": "same",
                "readable": True,
                "width": 1,
                "height": 1,
                "mode": "RGB",
            },
        ]
    )
    with pytest.raises(RuntimeError):
        prepare(frame, seed=42)
