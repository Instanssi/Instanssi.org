from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from Instanssi.sceneid.provider import SceneIDProvider

urlpatterns = default_urlpatterns(SceneIDProvider)
