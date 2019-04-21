""""
@author: moon
@date: 2019.02.27
"""

from authy.api import AuthyApiClient
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import parsers, renderers, status, filters
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.compat import coreapi, coreschema
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from django.utils import timezone

from api import utils
from api.pagination import CustomPagination
from api.permissions import IsCrowdfitCEOUser, IsCrowdfitAuthenticated, IsCrowdfitSuperUser, IsCrowdfitAdminUser
from api.serializers import CrowdfitAuthTokenSerializer, PhoneVerificationSerializer, RegisterSerializer, \
    UploadUserDocumentFileSerializer, DeleteUserDocumentFileSerializer, UpdateUserDocumentFileSerializer, \
    UpdateUserSerializer, CEORegisterSerializer, IsApartmentExistSerializer, UpdateApartmentSerializer, \
    DeleteApartmentSerializer, UserRegisterSerializer, StaffRegisterSerializer, CreateDepartmentRoleSerializer, \
    DeleteDepartmentRoleSerializer, ApproveCEOSerializer, ListUserByStatusSerializer, RequestUserRoleStatusSerializer, \
    ListStaffByStatusSerializer, ApproveStaffSerializer, ApproveUserSerializer, UpdateDepartmentRoleSerializer, \
    DisapproveSerializer, InvitedUserSerializer
from crowdfit_api.user.models import DocumentFile, UserRoleStatus, Login, Apartment, DepartmentIndex, Department, \
    DepartmentRole, Role, Status, Household, UserHousehold, InvitedUser
from crowdfit_api.user.serializers import UserRoleStatusSerializers, UserSerializer, DepartmentSerializers, \
    RoleSerializers, InvitedUserSerializers

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
            return Response(data={'res_code': 0, 'res_msg': 'success', 'user_id': user_id}, status=status.HTTP_200_OK)
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
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    #
    serializer_class = RequestUserRoleStatusSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user:
            # return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
            return Response({'res_code': 0, 'res_message': serializer.errors, 'fullname': None},
                            status=status.HTTP_403_FORBIDDEN)
        # 1. get input
        document_file = serializer.validated_data.get('document_file', None)  # allow null
        department_role_id = serializer.validated_data.get('department_role_id')  # not null
        # 2. pre-check input
        # check existing department_role_id
        try:
            department_role = DepartmentRole.objects.get(id=department_role_id)
        except DepartmentRole.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'Department role does not exist', 'fullname': user.fullname},
                            status=status.HTTP_400_BAD_REQUEST)
        # 2.1 check same apartment
        apt = utils.get_apartment(user=user)
        if not apt:
            return Response({'res_code': 0, 'res_message': 'Can not find apartment for user', 'fullname': user.fullname,
                             'user_id': user.id},
                            status=status.HTTP_400_BAD_REQUEST)
        if apt.id != department_role.department.apartment.id:
            return Response(
                {'res_code': 0, 'res_message': 'APT of user and APT of dep-role mismatch', 'fullname': user.fullname,
                 'user_id': user.id, 'user_apt_id': apt.id,
                 'dep_role_apt_id': department_role.department.apartment.id},
                status=status.HTTP_400_BAD_REQUEST)
        # 2.2 check existing status id: Waiting for approval
        try:
            _ = Status.objects.get(id=settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID)
        except Status.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'status (Waiting for Approval) not found'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 2.3 check exist user-role-status
        try:
            current_user_role_status = UserRoleStatus.objects.get(user=user, department_role_id=department_role_id)
            return Response({'res_code': 0, 'res_message': 'Department role duplicated', 'fullname': user.fullname,
                             'is_active': current_user_role_status.is_active,
                             'current_user_role_status_id': current_user_role_status.id,
                             'status_id': current_user_role_status.status.id,
                             'status_name': current_user_role_status.status.name
                             },
                            status=status.HTTP_409_CONFLICT)
        except UserRoleStatus.DoesNotExist:
            # return in try block so just continue
            pass
        # 3. do processing
        # 3.1 save document-file to table document-file
        document_file_id = None
        document_file_url = None
        document_file_name = None
        doc_file = DocumentFile()
        if document_file:
            doc_file.file_url = serializer.validated_data['document_file']
            doc_file.user = user
            doc_file.file_name = doc_file.file_url.name
            doc_file.file_size = doc_file.file_url.size
            doc_file.file_type = doc_file.file_url.file.content_type;
            doc_file.user_id = user.id
            doc_file.save()
            document_file_id = doc_file.id
            document_file_url = doc_file.file_url.url
            document_file_name = doc_file.file_name
        # 2.4 Insert a new row into UserRoleStatus with is_active = FALSE
        new_user_role_status = UserRoleStatus(user=user,
                                              department_role_id=department_role_id,
                                              staff=None,
                                              status_id=settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID,
                                              document_file_id=document_file_id,
                                              is_active=False)
        new_user_role_status.save()
        # 4. send response
        return Response({'res_code': 1, 'res_message': 'success', 'fullname': user.fullname,
                         'user_role_status_id': new_user_role_status.id,
                         'document_file_id': document_file_id, 'document_file_url': document_file_url,
                         'document_file_name': document_file_name,
                         'status_id': new_user_role_status.status.id,
                         'status_name': new_user_role_status.status.name
                         },
                        status=status.HTTP_200_OK)


class CEORegisterView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = CEORegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        user = request.user
        if not user:
            # return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
            return Response({'res_code': 0, 'res_message': serializer.errors, 'fullname': None},
                            status=status.HTTP_403_FORBIDDEN)
        # 1. check apt exist or not
        apt_name = serializer.validated_data['apt_name']
        # document_file_id = serializer.validated_data.get('document_file_id', None)
        document_file = serializer.validated_data.get('document_file', None)
        try:
            # 1. apt existed -> error duplicated apartment
            apt = Apartment.objects.get(name=apt_name)
            return Response({'res_code': 0, 'res_message': 'APT is  duplicated', 'fullname': user.fullname},
                            status=status.HTTP_409_CONFLICT)
        except Apartment.DoesNotExist:
            # 2.0 pre-check data
            # check existing role name=ceo
            try:
                role_ceo = Role.objects.get(id=settings.CROWDFIT_API_ROLE_NAME_CEO_ID)
            except Role.DoesNotExist:
                return Response({'res_code': 0, 'res_message': 'role ceo not found', 'fullname': None},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # check existing department index admin id
            try:
                _ = DepartmentIndex.objects.get(id=settings.CROWDFIT_API_DEPARTMENT_INDEX_ADMIN_ID)
            except DepartmentIndex.DoesNotExist:
                return Response({'res_code': 0, 'res_message': 'department index admin id not found', 'fullname': None},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # check existing status id: 회원가입중 (Becoming a member)
            try:
                _ = Status.objects.get(id=settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID)
            except Status.DoesNotExist:
                return Response(
                    {'res_code': 0, 'res_message': 'status (Waiting for Approval) not found', 'fullname': None},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 2.1 create new apt
            apt_data = dict(serializer.validated_data)
            #
            apt = Apartment(city_id=apt_data['city_id'],
                            name=apt_data['apt_name'],
                            address_gu=apt_data['address_gu'],
                            address_dong=apt_data['address_dong'],
                            address_road=apt_data['address_road'],
                            address_detail=apt_data['address_detail'],
                            postcode=apt_data['postcode'],
                            phone=apt_data['phone'],
                            latitude=apt_data['latitude'],
                            longtitude=apt_data['longitude'],
                            description=apt_data['description'],
                            is_active=False
                            )
            apt.save()
            # 2.2  get all dep-index and for each dep-idex -> insert department
            list_dep_idx = DepartmentIndex.objects.all()
            admin_department = None
            for department_index in list_dep_idx:
                new_dep = Department(apartment=apt, department_index=department_index)
                new_dep.save()
                if department_index.id == settings.CROWDFIT_API_DEPARTMENT_INDEX_ADMIN_ID:
                    admin_department = new_dep

            # 2.3 Insert  a new row into  DepartmentRole with department_id is Adminstration ID,
            # and role_id is the ceo id (in table role)
            # 2.3.1 get admin role
            # 2.3.2 create and insert department-role
            dep_role = DepartmentRole()
            dep_role.department = admin_department
            dep_role.role = role_ceo
            dep_role.is_active = True
            dep_role.save()
            # 2.3.3. save file to table documentfile
            doc_file = DocumentFile()
            document_file_id = None
            document_file_url = None
            document_file_name = None
            if document_file:
                doc_file.file_url = serializer.validated_data['document_file']
                doc_file.user = user
                doc_file.file_name = doc_file.file_url.name
                doc_file.file_size = doc_file.file_url.size
                doc_file.file_type = doc_file.file_url.file.content_type;
                doc_file.user_id = user.id
                doc_file.save()
                document_file_id = doc_file.id
                document_file_url = doc_file.file_url.url
                document_file_name = doc_file.file_name
            # 2.4 Insert a new row into UserRoleStatus with is_active = FALSE
            new_user_role_status = UserRoleStatus(user=user,
                                                  department_role=dep_role,
                                                  staff=None,
                                                  status_id=settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID,
                                                  document_file_id=document_file_id,
                                                  is_active=False)
            new_user_role_status.save()
        # 5. return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 1, 'res_message': 'success', 'fullname': user.fullname, 'apt_id': apt.id,
                         'document_file_id': document_file_id, 'document_file_url': document_file_url,
                         'document_file_name': document_file_name},
                        status=status.HTTP_200_OK)


class IsApartmentExistView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = IsApartmentExistSerializer

    def post(self, request):
        user = request.user
        if not utils.is_staff_user(user):
            return Response({'res_code': 0, 'res_message': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)
        # validate data
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        apt_name = serializer.validated_data['name']
        apt_postcode = serializer.validated_data['postcode']
        try:
            apt = Apartment.objects.get(name=apt_name, postcode=apt_postcode)
            return Response({'res_code': 1, 'res_message': 'APT exists in the database', 'apt_id': apt.id},
                            status=status.HTTP_200_OK)
        except Apartment.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'APT does not exist in the database', 'apt_id': None},
                            status=status.HTTP_200_OK)


class UpdateApartmentView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = UpdateApartmentSerializer
    queryset = Apartment.objects.all()

    def put(self, request):
        # 1. check permission
        if not utils.is_staff_user(request.user):
            return Response({'res_code': 0, 'res_message': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)
        # 2. valid data
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 3. execute
        apt_id = serializer.validated_data['apt_id']
        try:
            current_instance = Apartment.objects.get(id=apt_id)
            serializer.update(current_instance, serializer.validated_data)
            return Response({'res_code': 1, 'res_msg': 'success'}, status=status.HTTP_200_OK)
        except Apartment.DoesNotExist:
            return Response({'res_code': 0, 'res_msg': 'APT does not exist'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            return Response({'res_code': 0, 'res_msg': str(exc)}, status=status.HTTP_204_NO_CONTENT)


class DeleteApartmentView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = DeleteApartmentSerializer

    def put(self, request):
        # 1. check permission
        if not utils.is_staff_user(request.user):
            return Response({'res_code': 0, 'res_message': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)
        # 2. valid data
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 3. execute
        apt_id = serializer.validated_data['apt_id']
        try:
            current_instance = Apartment.objects.get(id=apt_id)
            current_instance.delete()
            return Response({'res_code': 1, 'res_msg': 'success'}, status=status.HTTP_200_OK)
        except Apartment.DoesNotExist:
            return Response({'res_code': 0, 'res_msg': 'APT does not exist'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            return Response({'res_code': 0, 'res_msg': str(exc)}, status=status.HTTP_204_NO_CONTENT)


class UserRegisterView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        user = request.user
        if not user:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        # user_id: INT
        # apt_id: INT
        # address_dong: TEXT
        # house_number: TEXT
        # document_file_id: INT/NULL
        # 1. check apt exist or not
        apt_id = serializer.validated_data['apt_id']
        document_file = serializer.validated_data.get('document_file', None)
        address_dong = serializer.validated_data.get('address_dong')
        house_number = serializer.validated_data.get('house_number')
        try:
            # 1. apt existed -> error duplicated apartment
            apt = Apartment.objects.get(id=apt_id)
        except Apartment.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'APT not found', 'fullname': user.fullname},
                            status=status.HTTP_204_NO_CONTENT)
        # 2.0 pre-check data
        # check existing role name=resident
        try:
            # role_resident = Role.objects.get(role=settings.CROWDFIT_API_ROLE_NAME_RESIDENT)
            role_resident = Role.objects.get(id=settings.CROWDFIT_API_ROLE_NAME_RESIDENT_ID)
        except Role.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'role resident not found', 'fullname': user.fullname},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # check existing department index community id
        try:
            dep_index_community = DepartmentIndex.objects.get(id=settings.CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID)
        except DepartmentIndex.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'department community not found', 'fullname': user.fullname},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # check existing status id: (Waiting for approval)
        try:
            status_waiting_for_approval = Status.objects.get(id=settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID)
        except Status.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'status Waiting for approval not found', 'fullname': user.fullname},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 3. get community department role resident
        # 3.1 get dep-role as community-resident
        # 3.1.1 from apt get department has dep-idx-id = 'community'
        try:
            department = Department.objects.get(apartment=apt, department_index=dep_index_community)
        except Department.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'Department community not found', 'fullname': user.fullname},
                status=status.HTTP_204_NO_CONTENT)
        try:
            dep_role = DepartmentRole.objects.get(department=department, role=role_resident)
        except DepartmentRole.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'Department community has no role resident', 'fullname': user.fullname
                    , 'department_id': department.id, 'role_resident_id': role_resident.id
                 },
                status=status.HTTP_204_NO_CONTENT)
        # 3.1.2 check exist user-role-status
        try:
            current_user_role_status = UserRoleStatus.objects.get(user=user, department_role=dep_role)
            return Response(
                {'res_code': 0, 'res_message': 'Role duplicated', 'fullname': user.fullname,
                 'is_active': current_user_role_status.is_active, 'status': current_user_role_status.status.name},
                status=status.HTTP_409_CONFLICT)
        except UserRoleStatus.DoesNotExist:
            # return in try block so just continue
            pass
        # 3.1.3. save file to table documentfile
        document_file_id = None
        document_file_url = None
        document_file_name = None
        doc_file = DocumentFile()
        if document_file:
            doc_file.file_url = serializer.validated_data['document_file']
            doc_file.user = user
            doc_file.file_name = doc_file.file_url.name
            doc_file.file_size = doc_file.file_url.size
            doc_file.file_type = doc_file.file_url.file.content_type;
            doc_file.user_id = user.id
            doc_file.save()
            #
            document_file_id = doc_file.id
            document_file_url = doc_file.file_url.url
            document_file_name = doc_file.file_name
        # 3.1.4 Insert a new row into UserRoleStatus with is_active = FALSE
        new_user_role_status = UserRoleStatus(user=user,
                                              department_role=dep_role,
                                              staff=None,
                                              status=status_waiting_for_approval,
                                              document_file_id=document_file_id,
                                              is_active=False)
        new_user_role_status.save()
        # 4. for Household
        # 4.1 table household: Check if the house_number with dept_id and address_dong exists in the table Household or not
        is_owner = False
        try:
            household = Household.objects.get(apartment=apt, address_dong=address_dong)
        except Household.DoesNotExist:
            # insert new and user is owner of this household
            household = Household(apartment=apt, address_dong=address_dong, house_number=house_number, is_empty=True)
            household.save()
            is_owner = True
        # 4.2 userhousehold
        user_household = UserHousehold(user=user, household=household, is_active=False, is_owner=is_owner)
        user_household.save()
        # 5. return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 1, 'res_message': 'success', 'fullname': user.fullname,
                         'household': {'id': household.id, 'is_owner': is_owner, 'is_empty': household.is_empty}},
                        status=status.HTTP_200_OK)


class StaffRegisterView(GenericAPIView):
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = StaffRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        user = request.user
        if not user:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        # user_id: INT
        # apt_id: INT
        # department_id: INT
        # role_id: INT
        # document_file: File/NULL
        # 1. check apt exist or not
        apt_id = serializer.validated_data['apt_id']
        department_id = serializer.validated_data['department_id']
        role_id = serializer.validated_data['role_id']
        document_file = serializer.validated_data.get('document_file', None)
        # 1. pre-check data
        # 1.1. check apt exist
        try:
            apt = Apartment.objects.get(id=apt_id)
        except Apartment.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'APT not found', 'fullname': user.fullname},
                            status=status.HTTP_204_NO_CONTENT)
        # 1.2. check department exist. department must have dep.apt_id = apt.id
        try:
            department = Department.objects.get(id=department_id, apartment=apt)
        except Department.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'Department not found', 'fullname': user.fullname},
                            status=status.HTTP_204_NO_CONTENT)
        # check existing role by id
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'role not found', 'fullname': user.fullname},
                            status=status.HTTP_204_NO_CONTENT)
        # 1.3 check department has this role
        try:
            dep_role = DepartmentRole.objects.get(department=department, role=role)
        except DepartmentRole.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'Department has no request role', 'fullname': user.fullname,
                 'department_id': department.id, 'department_name': department.department_index.name,
                 'role_id': role.id, 'role_name': role.role
                 },
                status=status.HTTP_204_NO_CONTENT)
        # check existing status id: (Waiting for approval)
        try:
            status_waiting_for_approval = Status.objects.get(id=settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID)
        except Status.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'status Waiting for approval not found', 'fullname': user.fullname},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2.1 check exist user-role-status
        try:
            current_user_role_status = UserRoleStatus.objects.get(user=user, department_role=dep_role)
            return Response(
                {'res_code': 0, 'res_message': 'Role duplicated', 'fullname': user.fullname,
                 'is_active': current_user_role_status.is_active, 'status': current_user_role_status.status.name},
                status=status.HTTP_409_CONFLICT)
        except UserRoleStatus.DoesNotExist:
            pass
        # 2.3.3. save file to table documentfile
        doc_file = DocumentFile()
        document_file_id = None
        document_file_url = None
        document_file_name = None
        if document_file:
            doc_file.file_url = serializer.validated_data['document_file']
            doc_file.user = user
            doc_file.file_name = doc_file.file_url.name
            doc_file.file_size = doc_file.file_url.size
            doc_file.file_type = doc_file.file_url.file.content_type;
            doc_file.user_id = user.id
            doc_file.save()
            #
            document_file_id = doc_file.id
            document_file_url = doc_file.file_url.url
            document_file_name = doc_file.file_name
        # 2.3.4 Insert a new row into UserRoleStatus with is_active = FALSE
        new_user_role_status = UserRoleStatus(user=user,
                                              department_role=dep_role,
                                              staff=None,
                                              status=status_waiting_for_approval,
                                              document_file_id=document_file_id,
                                              is_active=False)
        new_user_role_status.save()
        # 3. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 1, 'res_message': 'success', 'fullname': user.fullname,
                         'department_id': department.id, 'department_name': department.department_index.name,
                         'role_id': role.id, 'role_name': role.role, 'status': status_waiting_for_approval.name,
                         'document_file_id': document_file_id, 'document_file_url': document_file_url,
                         'document_file_name': document_file_name},
                        status=status.HTTP_200_OK)


class CreateDepartmentRoleView(GenericAPIView):
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = CreateDepartmentRoleSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        # department_id: INT
        # role_id: INT
        # 1. check apt exist or not
        user = request.user
        department_id = serializer.validated_data['department_id']
        role_id = serializer.validated_data['role_id']
        # 1. pre-check data
        # 1.1. check apt exist
        apt = utils.get_apartment(user)
        if not apt:
            return Response({'res_code': 0, 'res_message': 'Can not find your APT', 'fullname': user.fullname},
                            status=status.HTTP_204_NO_CONTENT)
        # 1.2. check department exist. department must have dep.apt_id = apt.id
        try:
            department = Department.objects.get(id=department_id, apartment=apt)
        except Department.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'Department not in your apartment', 'fullname': user.fullname,
                 'apt_id': apt.id},
                status=status.HTTP_204_NO_CONTENT)
        # 1.3 check existing role by id
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'role not found', 'fullname': user.fullname, 'apt_id': apt.id},
                status=status.HTTP_204_NO_CONTENT)
        # 1.4 check department has this role
        dep_name = utils.get_department_name(department)
        try:
            exist_dep_role = DepartmentRole.objects.get(department=department, role=role)
            return Response(
                {'res_code': 0, 'res_message': 'Department has role', 'fullname': user.fullname,
                 'department_id': department.id, 'department_name': dep_name,
                 'role_id': role.id, 'role_name': role.role, 'apt_id': apt.id, 'is_active': exist_dep_role.is_active
                 },
                status=status.HTTP_204_NO_CONTENT)
        except DepartmentRole.DoesNotExist:
            pass
        # 2. create data
        dep_role = DepartmentRole(department=department, role=role, is_active=True)
        dep_role.save()
        res_msg = 'Assign role: ' + role.role + ' to department: ' + dep_name
        # 3. final return res_code = 1, res_message: SUCCESS
        return Response(
            {'res_code': 1, 'res_message': 'success', 'fullname': user.fullname, 'id': dep_role.id, 'apt_id': apt.id,
             'is_active': dep_role.is_active, 'desc': res_msg},
            status=status.HTTP_200_OK)


class DeleteDepartmentRoleView(GenericAPIView):
    """
    superuser: need not check is owner of apt or not
    ceo: user must be creator of apt
    """
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = DeleteDepartmentRoleSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        # department_id: INT
        # role_id: INT
        # 1. check apt exist or not
        user = request.user
        # dep_role_id = serializer.validated_data['dep_role_id']
        dep_role_id = kwargs['dep_role_id']
        # 1. pre-check data
        try:
            dep_role = DepartmentRole.objects.get(id=dep_role_id)
        except DepartmentRole.DoesNotExist:
            return Response(
                {'res_code': 0, 'res_message': 'Department role does not exist', 'fullname': user.fullname,
                 'dep_role_id': dep_role_id}, status=status.HTTP_204_NO_CONTENT)
        # 1.1 check permission. if superuser -> allow, ceo-> check same apt
        if not utils.is_superuser(user):
            apt = utils.get_apartment(user)
            if apt.id != dep_role.department.apartment.id:
                return Response(
                    {'res_code': 0, 'res_message': 'Difference APT', 'fullname': user.fullname,
                     'dep_role_id': dep_role_id}, status=status.HTTP_204_NO_CONTENT)
        apt_id = dep_role.department.apartment_id
        department_id = dep_role.department_id
        department_name = utils.get_department_name(dep_role.department)
        role_id = dep_role.role_id
        role_name = dep_role.role.role
        desc = 'delete role: ' + role_name + ' for department: ' + department_name
        # 2. execute delete
        dep_role.delete()
        # 3. final return res_code = 1, res_message: SUCCESS
        return Response(
            {'res_code': 1, 'res_message': 'success', 'fullname': user.fullname,
             'dep_role_id': dep_role_id,
             'apt_id': apt_id,
             'department_id': department_id,
             'department_name': department_name,
             'role_id': role_id,
             'role_name': role_name,
             'is_active': dep_role.is_active, 'desc': desc},
            status=status.HTTP_200_OK)


class ApproveCEOView(GenericAPIView):
    """
    only superuser can do this action
    approve role ceo for user
    """
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitSuperUser)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = ApproveCEOSerializer

    def is_valid_user_role_status(self, data):
        """
        department = CROWDFIT_API_DEPARTMENT_INDEX_ADMIN_ID = 1
        role = CROWDFIT_API_ROLE_NAME_CEO_ID = 15
        approve role ceo for user
        1. Check if the staff_id has an authority to approve user register or not.
        1.1 YES: Update status_id to APPROVED and is_active = TRUE in table UserRoleStatus
        1.2 NO: return res_code = 0/ res_msg = ""STAFF DOES NOT HAVE AUTHORITY""
        2. Check if Insert new row into Househole with is_empty = FALSE
        3. Insert new row into Userhousehole with is_owner = TRUE, is_active = TRUE
        4. return res_code = 1/ return res_msg=""REQUEST SUCCESS)
        """
        return data.department_role.department_id == settings.CROWDFIT_API_DEPARTMENT_INDEX_ADMIN_ID \
               and data.department_role.role_id == settings.CROWDFIT_API_ROLE_NAME_CEO_ID

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        # department_id: INT
        # role_id: INT
        # 1. check apt exist or not
        user = request.user
        ceo_id = serializer.validated_data['user_id']
        # 1. pre-check data
        try:
            ceo_user = CustomUser.objects.get(id=ceo_id)
        except CustomUser.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'User not found',
                             'user_id': ceo_id}, status=status.HTTP_204_NO_CONTENT)
        # check existing status id: Approve
        try:
            status_approve = Status.objects.get(id=settings.CROWDFIT_API_STATUS_APPROVE)
        except Status.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'status: Approve not found',
                             'status_id': settings.CROWDFIT_API_STATUS_APPROVE},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # get role ceo
        list_user_role_status = UserRoleStatus.objects.filter(user_id=ceo_id)
        for user_role_status in list_user_role_status:
            if self.is_valid_user_role_status(user_role_status):
                # 2.1 if is_active == True means approved -> send error
                if user_role_status.is_active:
                    return Response({'res_code': 0, 'res_message': 'approved'},
                                    status=status.HTTP_409_CONFLICT)
                # 2.2 is_active == False: do approve
                user_role_status.is_active = True
                user_role_status.staff = user
                user_role_status.status = status_approve
                user_role_status.save()
                return Response({'res_code': 1, 'res_message': 'success'},
                                status=status.HTTP_200_OK)

        # 3. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 0, 'res_message': 'role ceo not found'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApproveStaffView(GenericAPIView):
    """
    role: (ceo, superuser)
    approve role staff for user
    """
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = ApproveStaffSerializer

    def is_valid_user_role_status(self, data):
        """
        department != CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID = 2
        role != CROWDFIT_API_ROLE_NAME_RESIDENT_ID = 16
        """
        return data.department_role.department.department_index_id != settings.CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID \
               and data.department_role.role_id != settings.CROWDFIT_API_ROLE_NAME_RESIDENT_ID

    def is_staff_has_permission(self, staff, user_role_status):
        """
        dep-role has dep-idx-id = admin
        """
        if not staff:
            return False
        # 1. if staff is superuser, return True
        if utils.is_superuser(staff):
            return True
        # 2. check same apt
        apt_staff = utils.get_apartment(staff)
        if not apt_staff:
            return False
        apt_user = user_role_status.department_role.department.apartment
        # 2.1 not same apt return False
        if apt_staff.id != apt_user.id:
            return False
        # 2.2 same apt, check role
        # 2.2.1 get all staff role in dep=admin-dep-idx(id=1)
        require_dep_idx_id = settings.CROWDFIT_API_DEPARTMENT_INDEX_ADMIN_ID
        require_role_id = settings.CROWDFIT_API_ROLE_NAME_CEO_ID
        list_active_staff_role = UserRoleStatus.objects.filter(user_id=staff.id, is_active=True,
                                                               # dep =admin
                                                               department_role__department__department_index=require_dep_idx_id,
                                                               # role=admin
                                                               department_role__role_id=require_role_id
                                                               )
        return len(list_active_staff_role) > 0
        # for active_staff_role in list_active_staff_role:
        #     dep_idx_id = active_staff_role.department_role.department.department_index_id
        #     if dep_idx_id == require_dep_idx_id:
        #         return True
        # return False

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        # department_id: INT
        # role_id: INT
        # 1. check apt exist or not
        staff = request.user
        user_id = serializer.validated_data['user_id']
        # 1. pre-check data
        try:
            waiting_approve_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'User not found',
                             'user_id': user_id}, status=status.HTTP_204_NO_CONTENT)
        # check existing status id: Approve(3)
        try:
            status_approve = Status.objects.get(id=settings.CROWDFIT_API_STATUS_APPROVE)
        except Status.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'status: Approve not found',
                             'status_id': settings.CROWDFIT_API_STATUS_APPROVE},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # get all role of user
        list_user_role_status = UserRoleStatus.objects.filter(user_id=user_id, is_active=False)
        for user_role_status in list_user_role_status:
            # kiem tra xem thang nay co dang request quyen staff nao khong
            if self.is_valid_user_role_status(user_role_status):
                # 2.2 is_active == False: do approve
                user_role_status.is_active = True
                user_role_status.staff = staff
                user_role_status.status = status_approve
                user_role_status.save()
                # 3. response success
                role_name = 'Approve role: ' + user_role_status.department_role.role.role
                dep_name = utils.get_department_name(user_role_status.department_role.department)
                return Response({'res_code': 1, 'res_message': 'success', 'user_role_status_id': user_role_status.id,
                                 'staff_fullname': staff.fullname, 'user_id': user_id,
                                 'role_name': role_name, 'dep_name': dep_name},
                                status=status.HTTP_200_OK)
        # 4. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 0, 'res_message': 'User wait for approve role staff not found'},
                        status=status.HTTP_400_BAD_REQUEST)


class ApproveUserView(GenericAPIView):
    """
    ceo, superuser, ﻿staff of administration department can do this action
    approve role resident for user
    """
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = ApproveUserSerializer

    def is_valid_user_role_status(self, data):
        """
        department = CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID = 2
        role = CROWDFIT_API_ROLE_NAME_RESIDENT_ID = 16
        approve role ceo for user
        """
        return data.department_role.department.department_index_id == settings.CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID \
               and data.department_role.role_id == settings.CROWDFIT_API_ROLE_NAME_RESIDENT_ID

    def is_staff_has_permission(self, staff, user_role_status):
        """
        dep-role has dep-idx-id = admin
        """
        if not staff:
            return False
        # 1. if staff is superuser, return True
        if utils.is_superuser(staff):
            return True
        # 2. check same apt
        apt_staff = utils.get_apartment(staff)
        if not apt_staff:
            return False
        apt_user = user_role_status.department_role.department.apartment
        # 2.1 not same apt return False
        if apt_staff.id != apt_user.id:
            return False
        # 2.2 same apt, check role
        # 2.2.1 get all staff role in dep=admin-dep-idx(id=1)
        require_dep_idx_id = settings.CROWDFIT_API_DEPARTMENT_INDEX_ADMIN_ID
        list_active_staff_role = UserRoleStatus.objects.filter(user_id=staff.id, is_active=True,
                                                               department_role__department__department_index=require_dep_idx_id)
        return len(list_active_staff_role) > 0
        # for active_staff_role in list_active_staff_role:
        #     dep_idx_id = active_staff_role.department_role.department.department_index_id
        #     if dep_idx_id == require_dep_idx_id:
        #         return True
        # return False

    def accept_invited_user(self, user):
        # search
        list_invited_user = InvitedUser.objects.filter(phone=user.phone, fullname=user.fullname)
        if len(list_invited_user) == 1:
            invited_user = list_invited_user[0]
            invited_user.status = settings.INVITATION_STATUS_ACCEPTED
            invited_user.save()
            return True
        return False

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        # department_id: INT
        # role_id: INT
        # 1. check apt exist or not
        staff = request.user
        user_id = serializer.validated_data['user_id']
        # 1. pre-check data
        try:
            waiting_approve_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'User not found',
                             'user_id': user_id}, status=status.HTTP_204_NO_CONTENT)
        # check existing status id: Approve(3)
        try:
            status_approve = Status.objects.get(id=settings.CROWDFIT_API_STATUS_APPROVE)
        except Status.DoesNotExist:
            return Response({'res_code': 0, 'res_message': 'status: Approve not found',
                             'status_id': settings.CROWDFIT_API_STATUS_APPROVE},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # get all role of user
        list_user_role_status = UserRoleStatus.objects.filter(user_id=user_id)
        for user_role_status in list_user_role_status:
            if self.is_valid_user_role_status(user_role_status):
                # 2.1 if is_active == True means approved -> send error
                if user_role_status.is_active:
                    return Response({'res_code': 0, 'res_message': 'approved'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # 2.2 is_active == False: do approve
                user_role_status.is_active = True
                user_role_status.staff = staff
                user_role_status.status = status_approve
                user_role_status.save()
                # 2.3 for household
                # 2.3.2 userhousehold -> set is_active = True
                user_household = UserHousehold.objects.get(user_id=user_id)
                user_household.is_active = True
                user_household.save()
                # 2.3.1 table household: Check if the house_number with dept_id and address_dong exists in the table Household or not
                if user_household.is_owner:
                    household = Household.objects.get(id=user_household.household_id)
                    household.is_empty = False
                    household.save()
                # change status if exist in table invited-user
                is_in_invited_user = self.accept_invited_user(waiting_approve_user)
                # 3. response success
                return Response({'res_code': 1, 'res_message': 'success', 'user_role_status_id': user_role_status.id,
                                 'user_household_is_owner': user_household.is_owner,
                                 'household_addr_dong': user_household.household.address_dong,
                                 'household_house_number': user_household.household.house_number,
                                 'staff_fullname': staff.fullname, 'user_id': user_id,
                                 'is_in_invited_user': is_in_invited_user},
                                status=status.HTTP_200_OK)
        # 4. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 0, 'res_message': 'User wait for approve role resident not found'},
                        status=status.HTTP_400_BAD_REQUEST)


class ListUserRoleStatusView(ListAPIView):
    """
    list all role status of user
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = UserRoleStatusSerializers
    model = serializer_class.Meta.model

    # paginate_by = 100
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = self.model.objects.filter(user_id=user_id)
        return queryset.order_by('-id')


class ListUserByStatusView(ListAPIView):
    """
    list all user by status
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = ListUserByStatusSerializer

    # paginate_by = 100
    def is_valid_user_role_status(self, data):
        """
        department = CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID = 2
        role = CROWDFIT_API_ROLE_NAME_RESIDENT_ID = 16
        """
        return utils.is_valid_user_role_status(data, settings.CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID,
                                               settings.CROWDFIT_API_ROLE_NAME_RESIDENT_ID)

    def get_queryset(self):
        status_id = self.kwargs['status_id']
        list_user_role_status = UserRoleStatus.objects.filter(status=status_id).order_by('-id')
        list_user = []
        # (fullname, address_dong, household_number, phone, last_update, document_url)
        # { 'user': {fullname, phone}, 'household': {address_dong, household_number}, 'role_status': {document_url} }
        # department : Community, Role: Resident
        for item in list_user_role_status:
            if self.is_valid_user_role_status(item):
                # 1. user-info
                tmp = {'fullname': item.user.fullname, 'phone': item.user.phone, 'user_id': item.user_id, 'create_date': item.user.create_date}
                # 2. house-hold info
                list_user_household = UserHousehold.objects.filter(user_id=item.user_id)
                if len(list_user_household) > 0:
                    user_household = list_user_household[0]
                    tmp['address_dong'] = user_household.household.address_dong
                    tmp['household_number'] = user_household.household.house_number
                else:
                    tmp['address_dong'] = None
                    tmp['household_number'] = None
                # 3. role-status
                if item.document_file:
                    tmp['document_url'] = item.document_file.file_url.url
                else:
                    tmp['document_url'] = None
                tmp['last_update'] = item.last_update
                # 4. for staff-id
                if item.staff:
                    tmp['staff_id'] = item.staff_id
                else:
                    tmp['staff_id'] = None
                # 5. insert
                # list_user.append({'user': user_info, 'household': household, 'role_status': role_status})
                list_user.append(tmp)
        queryset = list_user
        return queryset


class ListStaffByStatusView(ListAPIView):
    """
    list all staff by status. department: All, except community
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = ListStaffByStatusSerializer

    def is_valid_user_role_status(self, user_role_status):
        """
        department: All, except community
        """
        return user_role_status.department_role.department.department_index_id != settings.CROWDFIT_API_DEPARTMENT_INDEX_COMMUNITY_ID

    # paginate_by = 100
    def get_queryset(self):
        status_id = self.kwargs['status_id']
        list_user_role_status = UserRoleStatus.objects.filter(status=status_id).order_by('-user_id')
        # [ { 'user_id':1, 'roles': [ {dep_id, role_id} ]} ]
        list_staff = []
        # (fullname, address_dong, household_number, phone, last_update, document_url)
        # { 'user': {fullname, phone}, 'household': {address_dong, household_number}, 'role_status': {document_url} }
        # department : Community, Role: Resident
        current_user_id = 0
        staff_data = None
        for item in list_user_role_status:
            if self.is_valid_user_role_status(item):
                # department: All, except community
                apt_id = item.department_role.department.apartment_id
                dep_id = item.department_role.department_id
                role_id = item.department_role.role_id
                role_name = item.department_role.role.role
                last_update = item.department_role.last_update
                status_id = item.status_id
                is_active = item.is_active
                staff_id = None
                if item.staff:
                    staff_id = item.staff_id
                document_url = None
                if item.document_file:
                    document_url = item.document_file.file_url.url
                if current_user_id == item.user_id:
                    pass
                else:
                    # new staff data -> append old
                    if staff_data:
                        list_staff.append(staff_data)
                    # reset data
                    staff_data = {'user_id': item.user.id, 'fullname': item.user.fullname, 'phone': item.user.phone,
                                  'last_update': item.user.last_update,
                                  'create_date': item.user.create_date,
                                  'list_dep_role_status': []}
                    current_user_id = item.user_id
                # append dep-role data for current user
                staff_data['list_dep_role_status'].append({'apartment_id': apt_id, 'department_id': dep_id,
                                                           'role_id': role_id,
                                                           'role_name': role_name,
                                                           'last_update': last_update,
                                                           'staff_id': staff_id,
                                                           'document_url': document_url,
                                                           'status_id': status_id, 'is_active': is_active})
        if staff_data:
            list_staff.append(staff_data)
        queryset = list_staff
        return queryset


class ListAllDepartmentView(ListAPIView):
    """
    list all department.
    if user is superuser -> api_id not NULL
    if user is ceo(superadmin, admin) -> apt_id = apt of request.user
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitAdminUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = DepartmentSerializers

    # paginate_by = 100
    def set_extra_data_for_paginator(self, extra_data):
        if self.paginator and hasattr(self.paginator, 'set_extra_attributes'):
            self.paginator.set_extra_attributes(extra_data)

    def get_queryset(self):
        apt_id = self.kwargs.get('apt_id')
        extra_data = {}
        if not utils.is_superuser(self.request.user):
            # if not same apt -> return empty
            user_apt = utils.get_apartment(self.request.user)
            extra_data['apt_name'] = user_apt.name
            extra_data['is_superuser'] = False
            if user_apt.id != apt_id:
                queryset = []
                self.set_extra_data_for_paginator(extra_data)
                return queryset
        else:
            list_apt = Apartment.objects.filter(id=apt_id)
            extra_data['is_superuser'] = True
            if len(list_apt) == 1:
                extra_data['apt_name'] = list_apt[0].name
            else:
                # apt not found
                queryset = []
                self.set_extra_data_for_paginator(extra_data)
                return queryset

        # same apt
        list_department = Department.objects.filter(apartment_id=apt_id).order_by('id')
        queryset = list_department
        self.set_extra_data_for_paginator(extra_data)
        return queryset


class ListAllRoleOfDepartmentView(ListAPIView):
    """
    list all role of department.
    if user is superuser -> not check department in apt
    others check whether in apt or not
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitAdminUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = RoleSerializers

    # paginate_by = 100
    def set_extra_data_for_paginator(self, extra_data):
        if self.paginator and hasattr(self.paginator, 'set_extra_attributes'):
            self.paginator.set_extra_attributes(extra_data)

    def get_queryset(self):
        department_id = self.kwargs.get('department_id')
        extra_data = {}
        # check exist department_id
        list_dep = Department.objects.filter(id=department_id)
        if len(list_dep) == 1:
            department = list_dep[0]
        else:
            queryset = []
            extra_data['is_valid_department_id'] = False
            self.set_extra_data_for_paginator(extra_data)
            return queryset
        extra_data['is_valid_department_id'] = True
        extra_data['dep_name'] = utils.get_department_name(department)
        extra_data['apt_id'] = department.apartment_id
        extra_data['apt_name'] = department.apartment.name
        # check role
        if not utils.is_superuser(self.request.user):
            # if not same apt -> return empty
            user_apt = utils.get_apartment(self.request.user)
            extra_data['is_superuser'] = False
            extra_data['admin_apt_id'] = user_apt.id
            if user_apt.id != department.apartment_id:
                self.set_extra_data_for_paginator(extra_data)
                queryset = []
                return queryset
        #
        list_dep_role = DepartmentRole.objects.filter(department_id=department_id).order_by('role_id')
        queryset = []
        for dep_role in list_dep_role:
            queryset.append(dep_role.role)
        self.set_extra_data_for_paginator(extra_data)
        return queryset


class UpdateDepartmentRoleView(GenericAPIView):
    permission_classes = (IsAuthenticated, IsCrowdfitAdminUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = UpdateDepartmentRoleSerializer

    # queryset = Apartment.objects.all()

    def put(self, request, *args, **kwargs):
        # 1. check permission
        dep_role_id = kwargs['dep_role_id']
        list_instance = DepartmentRole.objects.filter(id=dep_role_id)
        if len(list_instance) != 1:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_msg': 'item not found'},
                            status=status.HTTP_400_BAD_REQUEST)
        current_instance = list_instance[0]
        # 2. valid data
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # 3. execute
        role_id = serializer.validated_data.get('role_id', None)
        if role_id:
            list_role = Role.objects.filter(id=role_id)
            if len(list_role) != 1:
                return Response({'res_code': 0, 'res_msg': 'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            # check duplicate
            list_role = DepartmentRole.objects.filter(department_id=current_instance.department_id, role_id=role_id)
            if len(list_role) > 0:
                return Response({'res_code': 0, 'res_msg': 'Duplicate department-role'},
                                status=status.HTTP_400_BAD_REQUEST)
        serializer.update(current_instance, serializer.validated_data)
        instance_data = {'id': dep_role_id, 'department_id': current_instance.department_id,
                         'role_id': current_instance.role_id,
                         'is_active': current_instance.is_active}
        return Response({'res_code': 1, 'res_msg': 'success', 'data': instance_data}, status=status.HTTP_200_OK)


class SearchUserView(ListAPIView):
    """
    list all staff by status. department: All, except community
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated, IsCrowdfitCEOUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = UserSerializer
    search_fields = ('username', 'email', 'fullname', 'phone', 'nickname')
    filter_backends = (filters.SearchFilter,)
    queryset = CustomUser.objects.all()

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        return queryset


class DisapproveView(GenericAPIView):
    """
    disapprove
    need check permission
    superuser/superadmin/admin for staff
    superuser/superadmin/admin/staff for user
    """
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = DisapproveSerializer

    def check_crowdfit_permission(self, staff, user_role_status):
        # 1. if staff is superuser -> return True
        if utils.is_superuser(staff):
            return True
        # if request ceo -> return false
        user_request_role_id = user_role_status.department_role.role_id
        if user_request_role_id == settings.CROWDFIT_API_ROLE_NAME_CEO_ID:
            return False
        # 2. get apt-id
        staff_apt = utils.get_apartment(staff)
        user_apt = utils.get_apartment(user_role_status.user)
        if staff_apt.id != user_apt.id:
            return False
        # 3. only request role: admin/staff or resident
        # check one-by-one
        list_staff_role_id = utils.get_all_user_role_id(staff)
        # 3.1 request-role: admin -> staff-role: superadmin
        if user_request_role_id == settings.CROWDFIT_API_ROLE_NAME_ADMIN_ID:
            return settings.CROWDFIT_API_ROLE_NAME_CEO_ID in list_staff_role_id

        # 3.3 resident: superadmin/admin/staff
        if user_request_role_id == settings.CROWDFIT_API_ROLE_NAME_RESIDENT_ID:
            return utils.is_staff_user(staff)
        # 3.2 request-role: staff, staff-role: superadmin/admin
        return settings.CROWDFIT_API_ROLE_NAME_CEO_ID in list_staff_role_id \
               or settings.CROWDFIT_API_ROLE_NAME_ADMIN_ID in list_staff_role_id

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        user_role_status_id = kwargs['id']
        # user_role_status_id = serializer.validated_data['id']
        reason = serializer.validated_data.get('reason', None)
        # 1. pre-check data
        try:
            user_role_status = UserRoleStatus.objects.get(id=user_role_status_id)
        except UserRoleStatus.DoesNotExist:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_message': 'Item not found',
                             'id': user_role_status_id}, status=status.HTTP_400_BAD_REQUEST)
        # check existing status id: Approve
        try:
            status_rejected = Status.objects.get(id=settings.CROWDFIT_API_STATUS_REJECTED)
        except Status.DoesNotExist:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_message': 'status: Rejected not found',
                             'status_id': settings.CROWDFIT_API_STATUS_REJECTED},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # check permission
        staff = request.user
        if not self.check_crowdfit_permission(staff, user_role_status):
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_message': 'Permission denied',
                             'fullname': staff.fullname,
                             'id': user_role_status_id, 'reason': reason},
                            status=status.HTTP_403_FORBIDDEN)
        # check status: must be status = Waiting for approval (2)
        if user_role_status.status_id != settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID:
            return Response({'res_code': settings.RES_CODE_FAIL,
                             'res_message': 'Wrong status. Status must be: Waiting for Approval',
                             'fullname': staff.fullname,
                             'status': user_role_status.status_id, 'status_name': user_role_status.status.name,
                             'id': user_role_status_id, 'reason': reason},
                            status=status.HTTP_400_BAD_REQUEST)
        # 2. do update
        user_role_status.staff = request.user
        user_role_status.status = status_rejected
        user_role_status.reason = reason
        user_role_status.save()

        # 3. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': settings.RES_CODE_SUCCESS, 'res_message': 'success',
                         'fullname': staff.fullname,
                         'status': status_rejected.id, 'status_name': status_rejected.name,
                         'id': user_role_status_id, 'reason': reason},
                        status=status.HTTP_200_OK)


class InvitedUserView(GenericAPIView):
    """
    invite user
    """
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = InvitedUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        validated_data = serializer.validated_data
        # 1. check apartment exist
        len_apt = len(Apartment.objects.filter(id=validated_data['apartment_id']))
        if len_apt != 1:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_message': 'APT not found',
                             'data': None},
                            status=status.HTTP_400_BAD_REQUEST)
        # 2. check (fullname, phone exist)
        list_invited_user = InvitedUser.objects.filter(fullname=validated_data['fullname'],
                                                       phone=validated_data['phone'])
        if len(list_invited_user) != 0:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_message': 'User with (fullname, phone) exist',
                             'data': {'id': list_invited_user[0].id, 'status': list_invited_user[0].status}},
                            status=status.HTTP_400_BAD_REQUEST)
        # 3. create instance
        instance = serializer.create(serializer.validated_data)
        instance.save()
        # 3. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': settings.RES_CODE_SUCCESS, 'res_message': 'success',
                         'data': {'id': instance.id, 'status': instance.status}},
                        status=status.HTTP_200_OK)


class InvitedUserView(GenericAPIView):
    """
    invite user
    """
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = InvitedUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # if validate fail, exception will raise, below code is not reached
        validated_data = serializer.validated_data
        # 1. check apartment exist
        len_apt = len(Apartment.objects.filter(id=validated_data['apartment_id']))
        if len_apt != 1:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_message': 'APT not found',
                             'data': None},
                            status=status.HTTP_400_BAD_REQUEST)
        # 2. check (fullname, phone exist)
        list_invited_user = InvitedUser.objects.filter(fullname=validated_data['fullname'],
                                                       phone=validated_data['phone'])
        if len(list_invited_user) != 0:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_message': 'User with (fullname, phone) exist',
                             'data': {'id': list_invited_user[0].id, 'status': list_invited_user[0].status}},
                            status=status.HTTP_400_BAD_REQUEST)
        # 3. create instance
        instance = serializer.create(serializer.validated_data)
        instance.save()
        # 3. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': settings.RES_CODE_SUCCESS, 'res_message': 'success',
                         'data': {'id': instance.id, 'status': instance.status}},
                        status=status.HTTP_200_OK)


class ReinviteUserView(GenericAPIView):
    """
    invite user
    """
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def put(self, request, *args, **kwargs):
        invite_id = kwargs['invite_id']
        list_instance = InvitedUser.objects.filter(id=invite_id)
        if len(list_instance) != 1:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_msg': 'item not found'},
                            status=status.HTTP_400_BAD_REQUEST)
        # if user status is accepted -> error
        instance = list_instance[0]
        if instance.status == settings.INVITATION_STATUS_ACCEPTED:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_msg': 'Cannot re-invite accepted user'},
                            status=status.HTTP_400_BAD_REQUEST)
        instance.status = settings.INVITATION_STATUS_REINVITED
        instance.save()
        # 3. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': settings.RES_CODE_SUCCESS, 'res_message': 'success',
                         'data': {'id': instance.id, 'status': instance.status}},
                        status=status.HTTP_200_OK)


class CancelInviteUserView(GenericAPIView):
    """
    invite user
    """
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def put(self, request, *args, **kwargs):
        invite_id = kwargs['invite_id']
        list_instance = InvitedUser.objects.filter(id=invite_id)
        if len(list_instance) != 1:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_msg': 'item not found'},
                            status=status.HTTP_400_BAD_REQUEST)
        # if user status is accepted -> error
        instance = list_instance[0]
        if instance.status == settings.INVITATION_STATUS_ACCEPTED:
            return Response({'res_code': settings.RES_CODE_FAIL, 'res_msg': 'Cannot cancel accepted user'},
                            status=status.HTTP_400_BAD_REQUEST)
        instance.status = settings.INVITATION_STATUS_CANCELED
        instance.save()
        # 3. final return res_code = 1, res_message: SUCCESS
        return Response({'res_code': settings.RES_CODE_SUCCESS, 'res_message': 'success',
                         'data': {'id': instance.id, 'status': instance.status}},
                        status=status.HTTP_200_OK)


class ListInvitedUserView(ListAPIView):
    """
    list all department.
    if user is superuser -> api_id not NULL
    if user is ceo(superadmin, admin) -> apt_id = apt of request.user
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = InvitedUserSerializers

    # paginate_by = 100
    def set_extra_data_for_paginator(self, extra_data):
        if self.paginator and hasattr(self.paginator, 'set_extra_attributes'):
            self.paginator.set_extra_attributes(extra_data)

    def get_queryset(self):
        extra_data = {}
        queryset = []
        staff = self.request.user
        if not utils.is_superuser(self.request.user):
            # only same apartment
            apartment = utils.get_apartment(staff)
            extra_data['apt_id'] = apartment.id
            extra_data['apt_name'] = apartment.name
            extra_data['is_superuser'] = False
            list_item = InvitedUser.objects.filter(apartment_id=apartment.id) \
                .exclude(status=settings.INVITATION_STATUS_ACCEPTED).order_by('id')
            queryset = list_item
        else:
            extra_data['is_superuser'] = True
            extra_data['apt_id'] = None
            extra_data['apt_name'] = None
            #
            list_apt = InvitedUser.objects.filter().exclude(status=settings.INVITATION_STATUS_ACCEPTED).order_by('id')
            queryset = list_apt

        self.set_extra_data_for_paginator(extra_data)
        return queryset


class ListAcceptedUserView(ListAPIView):
    """
    list all accepted user
    """
    pagination_class = CustomPagination
    permission_classes = (IsCrowdfitAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-the-url
    serializer_class = InvitedUserSerializers

    # paginate_by = 100
    def set_extra_data_for_paginator(self, extra_data):
        if self.paginator and hasattr(self.paginator, 'set_extra_attributes'):
            self.paginator.set_extra_attributes(extra_data)

    def get_queryset(self):
        extra_data = {}
        queryset = []
        staff = self.request.user
        if not utils.is_superuser(self.request.user):
            # only same apartment
            apartment = utils.get_apartment(staff)
            extra_data['apt_id'] = apartment.id
            extra_data['apt_name'] = apartment.name
            extra_data['is_superuser'] = False
            list_item = InvitedUser.objects.filter(apartment_id=apartment.id,
                                                   status=settings.INVITATION_STATUS_ACCEPTED).order_by('id')
            queryset = list_item
        else:
            extra_data['is_superuser'] = True
            extra_data['apt_id'] = None
            extra_data['apt_name'] = None
            #
            list_item = InvitedUser.objects.filter(status=settings.INVITATION_STATUS_ACCEPTED).order_by('id')
            queryset = list_item

        self.set_extra_data_for_paginator(extra_data)
        return queryset
