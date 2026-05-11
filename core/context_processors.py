def active_background(request):
    try:
        from .models import SiteBackground
        bg = SiteBackground.objects.filter(is_active=True).order_by("-id").first()
        if bg and bg.display_url:
            return {"active_background_url": bg.display_url}
    except Exception:
        pass
    return {"active_background_url": ""}


def active_login_thumbnail(request):
    try:
        from .models import LoginThumbnail
        thumb = LoginThumbnail.objects.filter(is_active=True).order_by("-id").first()
        if thumb:
            return {
                "active_login_thumbnail_url": thumb.display_url or "",
                "login_ticker_texts": [
                    thumb.ticker_text_1 or "18 HỌC VIÊN ĐÃ ĐĂNG KÝ",
                    thumb.ticker_text_2 or "CAM KẾT B1+ APTIS",
                    thumb.ticker_text_3 or "30 NGÀY TĂNG TỐC",
                    thumb.ticker_text_4 or "KÈM 1:1 LINH HOẠT",
                    thumb.ticker_text_5 or "LUYỆN NGHE 4 PART",
                ],
            }
    except Exception:
        pass

    return {
        "active_login_thumbnail_url": "",
        "login_ticker_texts": [
            "18 HỌC VIÊN ĐÃ ĐĂNG KÝ",
            "CAM KẾT B1+ APTIS",
            "30 NGÀY TĂNG TỐC",
            "KÈM 1:1 LINH HOẠT",
            "LUYỆN NGHE 4 PART",
        ],
    }


