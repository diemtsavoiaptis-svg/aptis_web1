
from django.shortcuts import redirect
from django.http import HttpResponse


class LockPartOneTwoMiddleware:
    """
    Lock old Part 1/Part 2 routes only when needed.
    Part 2 Version A admin pages must stay editable because the answer-pool workflow is active.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ""

        # Always allow active editable Part 2 Version A routes
        allowed_paths = [
            "/dashboard/part-2/",
            "/dashboard/part-2/may-gioi/",
            "/dashboard/part-2/may-kem/",
            "/listening/part-2/",
            "/listening/part-2/may-gioi/",
            "/listening/part-2/may-kem/",
        ]

        if any(path.startswith(p) for p in allowed_paths):
            return self.get_response(request)

        return self.get_response(request)
