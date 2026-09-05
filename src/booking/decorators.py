from functools import wraps

from django.http import JsonResponse


def require_json_methods(methods):
    allowed_methods = tuple(method.upper() for method in methods)

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method not in allowed_methods:
                response = JsonResponse(
                    {"error": "Method not allowed."},
                    status=405,
                )
                response["Allow"] = ", ".join(allowed_methods)
                return response

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
