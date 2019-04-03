from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from api.views import CrowdfitObtainAuthToken, CrowdfitRegisterView, UploadUserDocumentFileView, PhoneVerificationView, \
    TokenVerificationView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('auth/', CrowdfitObtainAuthToken.as_view()),
    path('phone_verification/', PhoneVerificationView.as_view()),
    path('token_verification/', TokenVerificationView.as_view()),
    path('register/', CrowdfitRegisterView.as_view()),
    path('upload_doc_file/', UploadUserDocumentFileView.as_view()),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)