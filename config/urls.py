"""django_basic_template URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from beekeeping_ecommerce.shop.views import select_country_view


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("", include("beekeeping_ecommerce.shop.urls", namespace="shop")),
    path(_("apiculture/"), include("beekeeping_ecommerce.blog.urls", namespace="blog")),
)

urlpatterns += [
    path("__debug__/", include("debug_toolbar.urls")),
    path('rosetta/', include('rosetta.urls')),
#   path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += [
    path(
        "select_country",
        select_country_view,
        name="select_country"
    )
]
