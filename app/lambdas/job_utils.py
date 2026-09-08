def job_id_from_key(key: str) -> str:
    return key.rsplit("/", 1)[-1].rsplit(".", 1)[0]


def content_type_for_key(key: str) -> str:
    low = key.lower()
    if low.endswith(".png"):
        return "image/png"
    if low.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"
