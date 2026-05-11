
class LocalCSRFFixMiddleware:
    """
    Local development CSRF helper.
    Some browser submissions can send Origin: null.
    For local 127.0.0.1 / localhost development, normalize it before CsrfViewMiddleware checks it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]

        if host in ["127.0.0.1", "localhost"]:
            origin = request.META.get("HTTP_ORIGIN")
            if origin == "null":
                request.META["HTTP_ORIGIN"] = f"http://{request.get_host()}"

        return self.get_response(request)
