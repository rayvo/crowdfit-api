""""
@author: moon
@date: 2019.02.27
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from api.views import CrowdfitObtainAuthToken, CrowdfitRegisterView, UploadUserDocumentFileView, PhoneVerificationView, \
    TokenVerificationView, DeleteUserDocumentFileView, UpdateUserDocumentFileView, \
    CrowdfitUpdateUserView, CEORegisterView, IsApartmentExistView, UpdateApartmentView, DeleteApartmentView, \
    UserRegisterView, StaffRegisterView, CreateDepartmentRoleView, DeleteDepartmentRoleView, ApproveCEOView, \
    ListUserRoleStatusView, ListUserByStatusView, RequestUserRoleStatusView, ListStaffByStatusView, ApproveUserView, \
    ApproveStaffView, ListAllDepartmentView, ListAllRoleOfDepartmentView, UpdateDepartmentRoleView, SearchUserView

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
    path('update_user/', CrowdfitUpdateUserView.as_view()),
    path('register_ceo/', CEORegisterView.as_view()),
    path('register_staff/', StaffRegisterView.as_view()),
    path('register_user/', UserRegisterView.as_view()),
    path('apartment_existed/', IsApartmentExistView.as_view()),
    path('update_apartment/', UpdateApartmentView.as_view()),
    path('delete_apartment/', DeleteApartmentView.as_view()),
    path('create_dep_role/', CreateDepartmentRoleView.as_view()),
    path('delete_dep_role/', DeleteDepartmentRoleView.as_view()),
    path('approve_ceo/', ApproveCEOView.as_view()),
    path('approve_staff/', ApproveStaffView.as_view()),
    path('approve_user/', ApproveUserView.as_view()),
    path('approve_user/', ApproveUserView.as_view()),
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    url(r'^list_user_role_status/(?P<user_id>\d+)/$', ListUserRoleStatusView.as_view()),
    url(r'^list_user_by_status/(?P<status_id>\d+)/$', ListUserByStatusView.as_view()),
    path('request_user_role_status/', RequestUserRoleStatusView.as_view()),
    url(r'^list_staff_by_status/(?P<status_id>\d+)/$', ListStaffByStatusView.as_view()),
    # url(r'^list_all_department/(?P<apt_id>\d*)/$', ListAllDepartmentView.as_view()),
    path('list_all_department/<int:apt_id>/', ListAllDepartmentView.as_view()),
    path('list_all_role_of_department/<int:department_id>/', ListAllRoleOfDepartmentView.as_view()),
    path('update_dep_role/<int:dep_role_id>/', UpdateDepartmentRoleView.as_view()),
    path('search_user/', SearchUserView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
