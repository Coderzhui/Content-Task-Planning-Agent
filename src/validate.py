"""输入校验。"""
REQUIRED = ("topic", "budget", "deadline_hours")


def validate(request):
    """返回 (normalized, missing)；格式/类型错误抛 ValueError。"""
    if not isinstance(request, dict):
        raise ValueError("input must be a JSON object")

    missing = [k for k in REQUIRED if request.get(k) in (None, "")]
    if missing:
        return None, missing

    topic = request["topic"]
    budget = request["budget"]
    deadline_hours = request["deadline_hours"]

    if not isinstance(topic, str):
        raise ValueError("topic must be a string")
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget <= 0:
        raise ValueError("budget must be a positive number")
    if isinstance(deadline_hours, bool) or not isinstance(deadline_hours, (int, float)) or deadline_hours <= 0:
        raise ValueError("deadline_hours must be a positive number")

    fail_injections = request.get("fail_injections", [])
    if not isinstance(fail_injections, list):
        raise ValueError("fail_injections must be a list")

    normalized = {
        "topic": topic,
        "budget": budget,
        "deadline_hours": deadline_hours,
        "fail_injections": fail_injections,
    }
    return normalized, None
