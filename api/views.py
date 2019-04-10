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

from api import utils
from api.permissions import IsCrowdfitCEOUser, IsCrowdfitAuthenticated
from api.serializers import CrowdfitAuthTokenSerializer, PhoneVerificationSerializer, RegisterSerializer, \
    UploadUserDocumentFileSerializer, DeleteUserDocumentFileSerializer, UpdateUserDocumentFileSerializer, \
    UpdateUserSerializer, CEORegisterSerializer, IsApartmentExistSerializer, UpdateApartmentSerializer, \
    DeleteApartmentSerializer, UserRegisterSerializer, StaffRegisterSerializer, CreateDepartmentRoleSerializer
from crowdfit_api.user.models import DocumentFile, UserRoleStatus, Login, Apartment, DepartmentIndex, Department, \
    DepartmentRole, Role, Status, Household, UserHousehold

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


# class RequestUserRoleStatusView(GenericAPIView):
#     serializer_class = RequestUserRoleStatusSerializer
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         # save data
#         user_role_status = UserRoleStatus(serializer.validated_data)
#         user_role_status.save()
#         return Response(data={'id': user_role_status.id}, status=status.HTTP_201_CREATED)


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


# class RequestUserRoleStatusView(GenericAPIView):
#     throttle_classes = ()
#     permission_classes = ()
#     parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
#     renderer_classes = (renderers.JSONRenderer,)
#     #
#     serializer_class = RequestUserRoleStatusSerializer
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         # 1. save file to table
#         # instance = UserRoleStatus(serializer.validated_data)
#         # instance = serializer.create(serializer.validated_data)
#         # instance = serializer.save()
#         instance = UserRoleStatus()
#         instance.user_id = serializer.validated_data['user_id']
#         instance.department_role_id = serializer.validated_data['department_role_id']
#         instance.document_file_id = serializer.validated_data['document_file_id']
#         instance.status_id = settings.CROWDFIT_API_USER_ROLE_STATUS_MEMBER
#         instance.is_active = False
#         if instance:
#             instance.save()
#             return Response(data={'id': instance.id, 'is_active': instance.is_active, 'status': instance.status_id},
#                             status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CEORegisterView(GenericAPIView):
    permission_classes = ()
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
        document_file_id = serializer.validated_data.get('document_file_id', None)
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

            # 2.4 Insert a new row into UserRoleStatus with is_active = FALSE
            new_user_role_status = UserRoleStatus(user=user,
                                                  department_role=dep_role,
                                                  staff=None,
                                                  status_id=settings.CROWDFIT_API_ROLE_WAITING_FOR_APPROVAL_ID,
                                                  document_file_id=document_file_id,
                                                  is_active=False)
            new_user_role_status.save()
        # 5. return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 1, 'res_message': 'success', 'fullname': user.fullname, 'apt_id': apt.id},
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
        document_file_id = serializer.validated_data.get('document_file_id', None)
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
                 # ,'department_id': department.id, 'role_resident_id': role_resident.id
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
            # 3.1.3 Insert a new row into UserRoleStatus with is_active = FALSE
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
        # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_list')
        # household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='households')
        # is_owner = models.BooleanField(default=False)
        # is_active = models.BooleanField(default=True)

        user_household = UserHousehold(user=user, household=household, is_active=False, is_owner=is_owner)
        user_household.save()
        # 5. return res_code = 1, res_message: SUCCESS
        return Response({'res_code': 1, 'res_message': 'success', 'fullname': user.fullname,
                         'household': {'id': household.id, 'is_owner': is_owner, 'is_empty': household.is_empty}},
                        status=status.HTTP_200_OK)


class StaffRegisterView(GenericAPIView):
    permission_classes = ()
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
        # document_file_id: INT/NULL
        # 1. check apt exist or not
        apt_id = serializer.validated_data['apt_id']
        department_id = serializer.validated_data['department_id']
        role_id = serializer.validated_data['role_id']
        document_file_id = serializer.validated_data.get('document_file_id', None)
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
            # 2.2 Insert a new row into UserRoleStatus with is_active = FALSE
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
                         'role_id': role.id, 'role_name': role.role,
                         'status': status_waiting_for_approval.name},
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
