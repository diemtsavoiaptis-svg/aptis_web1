from pathlib import Path

p = Path("templates/admin/base_site.html")
p.parent.mkdir(parents=True, exist_ok=True)

p.write_text("""{% extends "admin/base.html" %}
{% load i18n static %}

{% block title %}
{% if subtitle %}{{ subtitle }} | {% endif %}{{ title }} | Quản trị TSA Aptis
{% endblock %}

{% block branding %}
<div id="site-name">
    <a href="{% url 'admin:index' %}">Quản trị TSA Aptis</a>
</div>
{% endblock %}

{% block extrastyle %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">
<style>
    :root {
        --primary: #e60023;
        --secondary: #8a0015;
        --accent: #ff5f76;
        --primary-fg: #fff;
        --body-bg: #fff7f9;
        --body-fg: #3f0011;
        --header-color: #fff;
        --breadcrumbs-bg: #fff1f4;
        --breadcrumbs-fg: #7a0010;
    }

    #header {
        background: linear-gradient(135deg, #e60023, #ff5f76);
        color: white;
    }

    #site-name a {
        color: white !important;
        font-weight: 900;
    }

    .module h2,
    .module caption,
    .inline-group h2 {
        background: linear-gradient(135deg, #e60023, #ff5f76);
        color: white;
    }

    div.breadcrumbs {
        background: #fff1f4;
        color: #7a0010;
    }

    div.breadcrumbs a {
        color: #7a0010;
        font-weight: 700;
    }

    a:link,
    a:visited {
        color: #8a0015;
    }

    input[type=submit],
    input[type=button],
    .submit-row input,
    a.button {
        background: #e60023;
        border-radius: 10px;
        font-weight: 800;
    }

    input[type=submit]:hover,
    input[type=button]:hover,
    .submit-row input:hover,
    a.button:hover {
        background: #b8001c;
    }
</style>
{% endblock %}
""", encoding="utf-8")

print("DA_GHI_LAI_ADMIN_BASE_SITE_SACH")
