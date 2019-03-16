from crowdfit_api.user import views
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import ObtainAuthToken

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('country', views.CountryViewSet)
router.register('city', views.CityViewSet)
router.register('addr', views.AddressViewSet)
router.register('apt', views.AptViewSet)
router.register('household', views.HouseholdViewSet)
router.register('status', views.StatusViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', ObtainAuthToken.as_view()),
    # path('aptdata/', views.AptDataRequest, name='aptdatarequest'),
]
