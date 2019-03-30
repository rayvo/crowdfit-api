from django.urls import path
from api.views import CrowdfitObtainAuthToken, CrowdfitRegisterView, UpdateUserAptView, PhoneVerificationView, \
    TokenVerificationView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('auth/', CrowdfitObtainAuthToken.as_view()),
    path('phone_verification/', PhoneVerificationView.as_view()),
    path('token_verification/', TokenVerificationView.as_view()),
    path('register/', CrowdfitRegisterView.as_view()),
    path('update_apt/', UpdateUserAptView.as_view()),
]
