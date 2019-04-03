from rest_framework import parsers, renderers, status
from rest_framework.authtoken.models import Token
from rest_framework.compat import coreapi, coreschema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView
from api.serializers import CrowdfitAuthTokenSerializer, PhoneVerificationSerializer, RegisterSerializer, \
    UploadUserDocumentFileSerializer

from authy.api import AuthyApiClient
from django.conf import settings
from rest_framework import serializers

from django.contrib.auth import get_user_model

from crowdfit_api.user.models import  Status, UserRoleStatus, DocumentFile

CustomUser = get_user_model()

authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)


class CrowdfitObtainAuthToken(APIView):
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
        # 2. get status of user
        user_status_role = UserStatusRole.objects.get(user_id=user.id)
        # 3. get list of role of user
        list_user_role = UserRole.objects.filter(user_id=user.id, is_active=True)
        pickup_records = []
        for tmp_user_role in list_user_role:
            pickup_records.append({'department_id': tmp_user_role.department_role.department_id,
                                   'role_id': tmp_user_role.department_role.role_id})
        return Response({'token': token.key,
                         'user_id': user.id,
                         'fullname': user.fullname,
                         'status_role': user_status_role.status_id,
                         'roles': pickup_records
                         })
        # if serializer.errors is None:
        #     user = serializer.validated_data['user']
        #     token, created = Token.objects.get_or_create(user=user)
        #     #quser = Token.objects.get(key=token)
        #     return Response({'token': token.key, 'user_id': user.id})
        # return Response({'token': '', 'user_id': 0})


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


class CrowdfitRegisterView(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all().order_by('-id')

    def post(self, request):
        init_status_id = 1
        #
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        # user = serializer.validated_data['user']
        # user = serializer.create(serializer.validated_data)
        user = serializer.save()
        if user:
            # create user_status
            # 1. get status
            status_init = Status.objects.get(id=init_status_id)
            # 2. update user status
            UserStatusRole.objects.create(user=user, status=status_init)
            # return success
            # retdict = OrderedDict(serializer.data)
            # retdict['status'] = init_status_id
            return Response(data={'id': user.id, 'status': init_status_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        doc_file.file_name = doc_file.file_url.name
        doc_file.file_size = doc_file.file_url.size
        doc_file.file_type = doc_file.file_url.file.content_type;
        doc_file.save()
        if doc_file:
            return Response(data={'id': doc_file.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
