from flask import jsonify

def success_response(data=None, message="Operation successful", status_code=200, meta=None):
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code


def error_response(code="SYS_ERROR", message="An error occurred", status_code=400, details=None):
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details if details is not None else {}
        }
    }
    return jsonify(payload), status_code


def paginated_response(items, page, per_page, total, message="Operation successful"):
    import math
    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": math.ceil(total / per_page) if per_page > 0 else 1
    }
    return success_response(data=items, message=message, meta=meta)
