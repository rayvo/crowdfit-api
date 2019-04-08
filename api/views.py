""""
@author: moon
@date: 2019.02.27
"""

from authy.api import AuthyApiClient
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import parsers, renderers, status
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.compat import coreapi, coreschema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from django.utils import timezone

from api.serializers import CrowdfitAuthTokenSerializer, PhoneVerificationSerializer, RegisterSerializer, \
    UploadUserDocumentFileSerializer, RequestUserRoleStatusSerializer, DeleteUserDocumentFileSerializer, \
    UpdateUserDocumentFileSerializer, UpdateUserSerializer
from crowdfit_api.user.models import DocumentFile, UserRoleStatus, Login

CustomUser = get_user_model()

authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)


class PhoneVerificationView(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = PhoneVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        phone = serializer.validated_data['phone_verification']
        # return Response({'phone_verification': phone})
        return Response(data=phone, status=status.HTTP_200_OK)
        # return Response(data=phone,status=status.HTTP_204_NO_CONTENT)

    def post_old(self, request, *args, **kwargs):
        phone_number = request.data['phone_number']
        country_code = request.data['country_code']
        # phone = authy_api.phones.verification_start(phone_number=phone_number, country_code=country_code, via='sms',
        #                                             code_length=4)
        return Response({'token': 'phone.content'})


class TokenVerificationView(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = serializers.Serializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        verification_code = request.data['verification_code']
        phone_number = request.data['phone_number']
        country_code = request.data['country_code']
        #
        verification = authy_api.phones.info(phone_number=phone_number, country_code=country_code)
        # verification = authy_api.phones.verification_check(phone_number=phone_number, country_code=country_code,
        #                                                    verification_code=verification_code)
        if verification.ok():
            return Response({'is_ok': verification.content})
        return Response({'is_fail': verification.content})

    def info(self, phone_number, country_code):
        phone = authy_api.phones(phone_number, country_code)
        return Response({'is_verified': phone.content})


class CrowdfitObtainAuthToken(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = CrowdfitAuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        # 2. insert log login to table user_login
        login = Login()
        login.user = user
        login.last_app_feature = None
        login.login_time = timezone.now()
        login.logout_time = None
        login.save()
        # 3. get list of role of user
        list_user_role = UserRoleStatus.objects.filter(user_id=user.id, is_active=True)
        pickup_records = []
        apartment_id = None
        apartment_name = None
        first_loop = True
        for tmp_user_role in list_user_role:
            pickup_records.append({'department_id': tmp_user_role.department_role.department_id,
                                   'role_id': tmp_user_role.department_role.role_id
                                   })
            if first_loop:
                first_loop = False
                apartment_id = tmp_user_role.department_role.department.apartment_id
                apartment_name = tmp_user_role.department_role.department.apartment.name
                # get apt-id from role

        # 4. get 'last_app_feature_id'
        last_app_features = []
        return Response({'token': token.key,
                         'user_id': user.id,
                         'fullname': user.fullname,
                         'roles': pickup_records,
                         'last_app_features': last_app_features,
                         'apartment_id': apartment_id,
                         'apartment_name': apartment_name
                         }, status=status.HTTP_200_OK)


class CrowdfitRegisterView(GenericAPIView):
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all().order_by('-id')

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        # user = serializer.validated_data['user']
        # user = serializer.create(serializer.validated_data)
        user = serializer.save()
        if user:
            # return data as login data
            # 1. generate token
            token, created = Token.objects.get_or_create(user=user)
            # 2. insert log login to table user_login
            login = Login()
            login.user = user
            login.last_app_feature = None
            login.login_time = timezone.now()
            login.logout_time = None
            login.save()
            # 3. get list of role of user, already registered user has no role
            user_roles = []
            # 4. get 'last_app_feature_id'
            last_app_features = []
            return Response({'token': token.key,
                             'user_id': user.id,
                             'fullname': user.fullname,
                             'userrolestatus': user_roles,
                             'last_app_features': last_app_features,
                             'apartment_id': None,
                             'apartment_name': None
                             }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrowdfitUpdateUserView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = UpdateUserSerializer
    queryset = CustomUser.objects.all().order_by('-id')

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 1. update
        # user_id = serializer.validated_data['user_id']
        user_id = request.user.id
        current_user = CustomUser.objects.get(id=user_id)
        if current_user:
            serializer.update(current_user, serializer.validated_data)
            return Response(data={'res_code': 0, 'res_msg' : 'success', 'user_id': user_id}, status=status.HTTP_200_OK)
        return Response({'res_code': 1, 'res_msg': serializer.errors}, status=status.HTTP_204_NO_CONTENT)


class UploadUserDocumentFileView(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    #
    serializer_class = UploadUserDocumentFileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 1. save file to table documentfile
        doc_file = DocumentFile()

        doc_file.file_url = serializer.validated_data['doc_file']
        # TODO: get user_id from token: user_id = request.user.id <-- right code
        doc_file.user_id = serializer.validated_data['user_id']
        doc_file.file_name = doc_file.file_url.name
        doc_file.file_size = doc_file.file_url.size
        doc_file.file_type = doc_file.file_url.file.content_type;
        doc_file.save()
        if doc_file:
            data = {
                'user_id': doc_file.user_id,
                'id': doc_file.id,
                'url': doc_file.file_url.url
            }
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestUserRoleStatusView(GenericAPIView):
    serializer_class = RequestUserRoleStatusSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # save data
        user_role_status = UserRoleStatus(serializer.validated_data)
        user_role_status.save()
        return Response(data={'id': user_role_status.id}, status=status.HTTP_201_CREATED)


class DeleteUserDocumentFileView(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    #
    serializer_class = DeleteUserDocumentFileSerializer

    def post(self, request):
        pass

    def delete(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 1. save file to table documentfile
        del_id = serializer.validated_data['doc_file_id']
        doc_file = DocumentFile.objects.get(id=del_id)
        if not doc_file is None:
            doc_file.delete()
            return Response(data={'id': del_id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)


class UpdateUserDocumentFileView(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    #
    serializer_class = UpdateUserDocumentFileSerializer

    def post(self, request):
        pass

    def put(self, request):
        # uid = request.user.id
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 1. save file to table documentfile
        update_doc_file_id = serializer.validated_data['doc_file_id']
        new_doc_file = serializer.validated_data['doc_file']
        current_doc_file = DocumentFile.objects.get(id=update_doc_file_id)
        if current_doc_file:
            current_doc_file.file_url = new_doc_file
            current_doc_file.file_name = current_doc_file.file_url.name
            current_doc_file.file_size = current_doc_file.file_url.size
            current_doc_file.file_type = current_doc_file.file_url.file.content_type;
            current_doc_file.save()
            data = {
                'user_id': current_doc_file.user_id,
                'id': current_doc_file.id,
                'url': current_doc_file.file_url.url
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)


class RequestUserRoleStatusView(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    #
    serializer_class = RequestUserRoleStatusSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 1. save file to table
        # instance = UserRoleStatus(serializer.validated_data)
        # instance = serializer.create(serializer.validated_data)
        # instance = serializer.save()
        instance = UserRoleStatus()
        instance.user_id = serializer.validated_data['user_id']
        instance.department_role_id = serializer.validated_data['department_role_id']
        instance.document_file_id = serializer.validated_data['document_file_id']
        instance.status_id = settings.CROWDFIT_API_USER_ROLE_STATUS_MEMBER
        instance.is_active = False
        if instance:
            instance.save()
            return Response(data={'id': instance.id, 'is_active': instance.is_active, 'status': instance.status_id},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
