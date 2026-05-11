
from django.http import HttpResponse

class LockPartOneTwoMiddleware:
    """
    Kh?a s?a dli?u Part 1 vPart 2.
    Cho ph?p xem GET/HEAD/OPTIONS.
    Ch?n POST/PUT/PATCH/DELETE  tr?nh thay i dli?u.
    """

    LOCKED_PREFIXES = (
        "/dashboard/part-1",
        "/dashboard/part-2",
    )

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/")

        if request.method not in self.SAFE_METHODS:
            for prefix in self.LOCKED_PREFIXES:
                if path.startswith(prefix):
                    return HttpResponse(
                        """
                        <!DOCTYPE html>
                        <html lang="vi">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title> kh?a dli?u</title>
                            <style>
                                body {
                                    margin: 0;
                                    min-height: 100vh;
                                    display: grid;
                                    place-items: center;
                                    font-family: Segoe UI, Arial, sans-serif;
                                    background: linear-gradient(180deg, #fff7f9, #ffffff);
                                    color: #3b0010;
                                }

                                .box {
                                    width: min(680px, calc(100% - 32px));
                                    padding: 36px;
                                    border: 1px solid #ffd0d8;
                                    border-radius: 28px;
                                    background: #ffffff;
                                    box-shadow: 0 18px 45px rgba(239, 35, 60, .12);
                                    text-align: center;
                                }

                                h1 {
                                    margin: 0 0 12px;
                                    font-size: 34px;
                                }

                                p {
                                    margin: 0 0 24px;
                                    color: #667085;
                                    font-weight: 650;
                                    line-height: 1.6;
                                }

                                a {
                                    display: inline-flex;
                                    align-items: center;
                                    justify-content: center;
                                    min-height: 46px;
                                    padding: 0 22px;
                                    border-radius: 999px;
                                    background: #ef233c;
                                    color: #ffffff;
                                    font-weight: 900;
                                    text-decoration: none;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="box">
                                <h1>Dli?u Part 1 vPart 2  ?c kh?a</h1>
                                <p>
                                    B?n v?n cthxem dli?u, nh?ng hi?n t?i hth?ng ?ang ch?n thao t?c l?u/s?a/x?a
                                     tr?nh m?t dli?u quan tr?ng.
                                </p>
                                <a href="/dashboard/listening-parts/">Quay l?i ch?n Part</a>
                            </div>
                        </body>
                        </html>
                        """,
                        status=423,
                        content_type="text/html; charset=utf-8",
                    )

        return self.get_response(request)
