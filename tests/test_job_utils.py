import sys
from pathlib import Path
LAMBDA_DIR = Path(__file__).resolve().parents[1] / "app" / "lambdas"
sys.path.insert(0, str(LAMBDA_DIR))
from job_utils import content_type_for_key, job_id_from_key

def test_job_id(): assert job_id_from_key("incoming/abc-123.jpg") == "abc-123"
def test_content_type():
    assert content_type_for_key("incoming/a.png") == "image/png"
    assert content_type_for_key("incoming/a.webp") == "image/webp"
    assert content_type_for_key("incoming/a.jpg") == "image/jpeg"
