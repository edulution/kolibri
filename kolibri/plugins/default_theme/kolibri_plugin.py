from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from django.templatetags.static import static
from kolibri.core import theme_hook
from kolibri.plugins import KolibriPluginBase
from kolibri.plugins.hooks import register_hook
import random


class DefaultThemePlugin(KolibriPluginBase):
    pass


@register_hook
class DefaultThemeHook(theme_hook.ThemeHook):
    @property
    def theme(self):
        # Get a random image of the 31 available images
        random_image = random.randint(1, 31)

        # Generate the background image filename based on the random number between 1 and 31
        background_image = static(f"assets/default_theme/background{random_image}.jpg")

        return {
            "signIn": {
                "background": background_image,
                "backgroundImgCredit": "Edulution",
                "topLogo": {
                    "style": "padding-left: 64px; padding-right: 64px; margin-bottom: 8px; margin-top: 8px",
                },
            },
            "logos": [
                {
                    "src": static("assets/default_theme/logo.ico"),
                    "content_type": "image/vnd.microsoft.icon",
                    "size": "32x32",
                },
                {
                    "src": static("assets/default_theme/kolibri-logo.svg"),
                    "content_type": "image/svg+xml",
                    "maskable": False,
                    "size": "any",
                },
                {
                    "src": static("assets/default_theme/kolibri-logo-192.png"),
                    "content_type": "image/png",
                    "size": "192x192",
                },
                {
                    "src": static("assets/default_theme/kolibri-logo-512.png"),
                    "content_type": "image/png",
                    "size": "512x512",
                },
            ],
        }
