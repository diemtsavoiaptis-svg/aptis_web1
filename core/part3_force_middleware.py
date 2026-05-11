
from django.shortcuts import render

class ForcePart3Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/")

        if path == "/dashboard/part-3":
            return render(request, "part3_force_admin.html")

        if path == "/part-3":
            return render(request, "part3_force_student.html")

        return self.get_response(request)
