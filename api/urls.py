""""
@author: moon
@date: 2019.02.27
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from api.views import CrowdfitObtainAuthToken, CrowdfitRegisterView, UploadUserDocumentFileView, PhoneVerificationView, \
    TokenVerificationView, DeleteUserDocumentFileView, UpdateUserDocumentFileView, \
    CrowdfitUpdateUserView, CEORegisterView, IsApartmentExistView, UpdateApartmentView, DeleteApartmentView, \
    UserRegisterView, StaffRegisterView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from crowdfit_api.user.views import ApartmentViewSet, DepartmentViewSet

router = routers.DefaultRouter()
router.register('apartment', ApartmentViewSet)
router.register('department', DepartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('phone_verification/', PhoneVerificationView.as_view()),
    path('token_verification/', TokenVerificationView.as_view()),
    path('auth/', CrowdfitObtainAuthToken.as_view()),
    path('register/', CrowdfitRegisterView.as_view()),
    path('create_user/', CrowdfitRegisterView.as_view()),
    path('upload_doc_file/', UploadUserDocumentFileView.as_view()),
    path('delete_doc_file/', DeleteUserDocumentFileView.as_view()),
    path('update_doc_file/', UpdateUserDocumentFileView.as_view()),
    # path('request_user_role_status/', RequestUserRoleStatusView.as_view()),
    path('update_user/', CrowdfitUpdateUserView.as_view()),
    path('register_ceo/', CEORegisterView.as_view()),
    path('apartment_existed/', IsApartmentExistView.as_view()),
    path('update_apartment/', UpdateApartmentView.as_view()),
    path('delete_apartment/', DeleteApartmentView.as_view()),
    path('register_user/', UserRegisterView.as_view()),
    path('register_staff/', StaffRegisterView.as_view()),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
