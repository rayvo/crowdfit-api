from crowdfit_api.user import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('country', views.CountryViewSet)
router.register('city', views.CityViewSet)
router.register('address', views.AddressViewSet)
router.register('apartment', views.ApartmentViewSet)
router.register('household', views.HouseholdViewSet)
router.register('imagefile', views.ImageFileViewSet)
router.register('useravatar', views.UserAvatarViewSet)
router.register('status', views.StatusViewSet)
router.register('documentfile', views.DocumentFileViewSet)
router.register('userstatus', views.UserStatusViewSet)
router.register('userhousehold', views.UserHouseholdViewSet)
router.register('department', views.DepartmentViewSet)
router.register('role', views.RoleViewSet)
router.register('departmentrole', views.DepartmentRoleViewSet)
router.register('userrole', views.UserRoleViewSet)
router.register('permission', views.PermissionViewSet)
router.register('appfeature', views.AppFeatureViewSet)
router.register('rolefeaturepermission', views.RoleFeaturePermissionViewSet)
router.register('login', views.LoginViewSet)
router.register('userbodyinfo', views.UserBodyInfoViewSet)
router.register('club', views.ClubViewSet)




# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]
