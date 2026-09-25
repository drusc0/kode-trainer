from app.main import app


def test_every_json_response_has_a_schema() -> None:
    untyped = []
    for path, methods in app.openapi()["paths"].items():
        for method, op in methods.items():
            for code, resp in op["responses"].items():
                if code.startswith("2") and code != "204":
                    schema = resp.get("content", {}).get("application/json", {}).get("schema")
                    if not schema:
                        untyped.append(f"{method.upper()} {path} -> {code}")
    assert untyped == []
