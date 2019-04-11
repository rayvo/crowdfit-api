""""
@author: moon
@date: 2019.02.27
"""

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
# for lazy text
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model

# for custom user
from django.conf import settings

from crowdfit_api.user.models import City

CustomUser = get_user_model()


class PhoneVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label=_("phone_number"))
    country_code = serializers.CharField(label=_("country_code"))

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        country_code = attrs.get('country_code')

        if phone_number and country_code:
            # phone = authy_api.phones.verification_start(phone_number=phone_number, country_code=country_code, via='sms',
            #                                             code_length=4)
            phone = {"success": True}
            if not phone:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='validate')
        else:
            msg = _('Must include "phone_number" and "country_code".')
            raise serializers.ValidationError(msg, code='validate')

        attrs['phone_verification'] = phone
        # phone = authy_api.phones.verification_start(phone_number=phone_number, country_code=country_code, via='sms',
        #                                             code_length=4)

        return attrs


class CrowdfitAuthTokenSerializer(serializers.Serializer):
    # username = serializers.CharField(label=_("Username"))
    email = serializers.CharField(label=_("email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            # The authenticate call simply returns None for is_active=False users.
            # (Assuming the default ModelBackend authentication backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        # owner=request.user get user from authenticated request
        # user = Token.objects.filter(*args, **kwargs)
        # if user.exists():
        #    user = user.last().user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    # validate_password = make_password  # for hashing password
    # Your validate_<field_name> methods should return the validated value or raise a serializers.ValidationError
    def validate_password(self, value):
        """
        return the validated password
        """
        value = make_password(value)
        return value

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return CustomUser.objects.create(**validated_data)

    # def validate(self, attrs):
    #     phone_number = attrs.get('phone_number')
    #     country_code = attrs.get('country_code')
    #
    #     if phone_number and country_code:
    #         # phone = authy_api.phones.verification_start(phone_number=phone_number, country_code=country_code, via='sms',
    #         #                                             code_length=4)
    #         phone = {"success": True}
    #         if not phone:
    #             msg = _('Unable to log in with provided credentials.')
    #             raise serializers.ValidationError(msg, code='validate')
    #     else:
    #         msg = _('Must include "phone_number" and "country_code".')
    #         raise serializers.ValidationError(msg, code='validate')
    #
    #     attrs['phone_verification'] = phone
    #     # phone = authy_api.phones.verification_start(phone_number=phone_number, country_code=country_code, via='sms',
    #     #                                             code_length=4)
    #
    #     return attrs

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'nickname', 'fullname', 'birthday', 'gender', 'phone', "blood_type")
        extra_kwargs = {'password': {'write_only': True, 'required': True}}


class UploadUserDocumentFileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)
    doc_file = serializers.FileField(allow_null=False)

    class Meta:
        fields = ('user_id', 'doc_file')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)


# class RequestUserRoleStatusSerializer(serializers.Serializer):
#     # "user_id: localStorage,
#     # department_role_id: null
#     # status_id: ***
#     # staff_id: null,
#     # document_file_id: null,
#     # is_active: false"
#     user_id = serializers.IntegerField(allow_null=False, required=True)
#     status_id = serializers.IntegerField(allow_null=False)
#     is_active = serializers.BooleanField(allow_null=False)
#
#     class Meta:
#         fields = ('user_id', 'status_id', 'is_active')
#
#     def create(self, validated_data):
#         return Response(data={}, status=status.HTTP_403_FORBIDDEN)


class DeleteUserDocumentFileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)
    doc_file_id = serializers.IntegerField(allow_null=False, required=True)

    class Meta:
        fields = ('user_id', 'doc_file_id')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)


class UpdateUserDocumentFileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)
    doc_file_id = serializers.IntegerField(allow_null=False, required=True)
    doc_file = serializers.FileField(allow_null=False)

    class Meta:
        fields = ('user_id', 'doc_file_id', 'doc_file')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)


class RequestUserRoleStatusSerializer(serializers.Serializer):
    # user_id = serializers.IntegerField(allow_null=False, required=True)
    document_file = serializers.FileField(allow_null=False, required=False)
    department_role_id = serializers.IntegerField(allow_null=False, required=True)

    class Meta:
        fields = ('document_file', 'department_role_id')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)


class UpdateUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)
    fullname = serializers.CharField(max_length=150, allow_null=True, required=False)
    nickname = serializers.CharField(max_length=50, allow_null=True, required=False)
    birthday = serializers.DateField(allow_null=True, required=False)
    phone = serializers.CharField(max_length=15, allow_null=True, required=False, validators=[settings.PHONE_REGEX])

    gender = serializers.ChoiceField(choices=settings.GENDER_CHOICES)
    blood_type = serializers.CharField(max_length=3, allow_null=True, required=False)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        fields = ('user_id', 'fullname', 'nickname', 'birthday', 'phone', 'gender', 'blood_type')


class CEORegisterSerializer(serializers.Serializer):
    # user_id = serializers.IntegerField(allow_null=False, required=True)
    # document_file_id = serializers.IntegerField(allow_null=True, required=False)
    document_file = serializers.FileField(allow_null=False, required=False)
    apt_name = serializers.CharField(max_length=150, allow_null=False, required=True)
    city_id = serializers.IntegerField(allow_null=False)
    address_gu = serializers.CharField(max_length=50, allow_null=False)
    address_dong = serializers.CharField(max_length=50, allow_null=False)
    address_road = serializers.CharField(max_length=250, allow_null=False)
    address_detail = serializers.CharField(max_length=100, allow_null=False)
    postcode = serializers.CharField(max_length=10, allow_null=False)
    # phone = serializers.CharField(max_length=15)
    phone = serializers.CharField(max_length=15, allow_null=False, required=False, validators=[settings.PHONE_REGEX])
    latitude = serializers.DecimalField(max_digits=11, decimal_places=8, default=0, allow_null=False)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8, default=0, allow_null=False)
    description = serializers.CharField(max_length=500, allow_null=False)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('document_file', 'apt_name', 'city_id', 'address_gu', 'address_dong', 'address_road',
                  'address_detail', 'postcode', 'phone', 'latitude', 'longitude', 'description')


class IsApartmentExistSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    postcode = serializers.CharField(max_length=10)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('name', 'postcode')


class UpdateApartmentSerializer(serializers.Serializer):
    # ID is by default
    # id = models.AutoField(primary_key=True)
    apt_id = serializers.IntegerField(required=True)
    city_id = serializers.IntegerField(allow_null=True, required=False)
    name = serializers.CharField(max_length=50, allow_null=False, required=False)
    # foreign key, auto generate db column: address_id
    address_gu = serializers.CharField(max_length=50, allow_null=False, required=False)
    address_dong = serializers.CharField(max_length=50, allow_null=False, required=False)
    address_road = serializers.CharField(max_length=250, allow_null=False, required=False)
    address_detail = serializers.CharField(max_length=100, allow_null=False, required=False)
    postcode = serializers.CharField(max_length=10, allow_null=False, required=False)
    phone = serializers.CharField(max_length=15, required=False)
    latitude = serializers.DecimalField(max_digits=11, decimal_places=8, allow_null=True, required=False)
    longtitude = serializers.DecimalField(max_digits=11, decimal_places=8, allow_null=True, required=False)
    description = serializers.CharField(max_length=500, allow_null=True, required=False)
    is_active = serializers.BooleanField(required=False)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        fields = ('apt_id', 'city_id', 'name', 'address_gu', 'address_dong', 'address_road', 'address_detail',
                  'postcode', 'phone', 'latitude', 'longtitude', 'description', 'is_active')


class DeleteApartmentSerializer(serializers.Serializer):
    # primary key
    apt_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('apt_id',)


class UserRegisterSerializer(serializers.Serializer):
    # user_id = serializers.IntegerField(allow_null=False, required=False)
    apt_id = serializers.IntegerField(allow_null=False, required=True)
    address_dong = serializers.CharField(max_length=150, allow_null=False, required=True)
    house_number = serializers.CharField(max_length=150, allow_null=False, required=True)
    document_file = serializers.FileField(allow_null=True, required=False)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('apt_id', 'address_dong', 'house_number', 'document_file_id')


class StaffRegisterSerializer(serializers.Serializer):
    """
    Request role staff for selected department of apt
    """
    # user_id = serializers.IntegerField(allow_null=False, required=True)
    apt_id = serializers.IntegerField(allow_null=False, required=True)
    department_id = serializers.IntegerField(allow_null=False, required=True)
    role_id = serializers.IntegerField(allow_null=False, required=True)
    document_file = serializers.FileField(allow_null=True, required=False)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('apt_id', 'department_id', 'role_id', 'document_file')


class CreateDepartmentRoleSerializer(serializers.Serializer):
    department_id = serializers.IntegerField(allow_null=False, required=True)
    role_id = serializers.IntegerField(allow_null=False, required=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('department_id', 'role_id')


class DeleteDepartmentRoleSerializer(serializers.Serializer):
    dep_role_id = serializers.IntegerField(allow_null=False, required=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('dep_role_id',)


class ApproveCEOSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('user_id',)


class ApproveStaffSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('user_id',)


class ApproveUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('user_id',)


class ListUserByStatusSerializer(serializers.Serializer):
    # (fullname, address_dong, household_number, phone, last_update, document_url)
    # { 'user': {fullname, phone}, 'household': {address_dong, household_number}, 'role_status': {document_url} }
    # for item in list_user_role_status:
    #     # 1. user-info
    #     user_info = {'fullname': item.user.fullname, 'phone': item.user.phone, 'user_id': item.user_id}
    #     # 2. house-hold info
    #     list_user_household = UserHousehold.objects.filter(user_id=item.user_id)
    #     household = {}
    #     if len(list_user_household) > 0:
    #         user_household = list_user_household[0]
    #         household = {'address_dong': user_household.household.address_dong,
    #                      'household_number': user_household.household.house_number}
    #     # 3. role-status
    #     role_status = {'document_url': item.document_file.file_url.url}
    #     # 4. insert
    #     list_user.append({'user': user_info, 'household': household, 'role_status': role_status})
    fullname = serializers.CharField(allow_null=True, required=True)
    address_dong = serializers.CharField(allow_null=True, required=True)
    household_number = serializers.CharField(allow_null=True, required=True)
    phone = serializers.CharField(allow_null=True, required=True)
    last_update = serializers.DateTimeField(allow_null=True, required=True)
    document_url = serializers.CharField(allow_null=True, required=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('fullname', 'address_dong', 'household_number', 'phone', 'last_update', 'document_url',)


class DepRoleStatusSerializer(serializers.Serializer):
    apartment_id = serializers.IntegerField(required=True)
    department_id = serializers.IntegerField(required=True)
    role_id = serializers.IntegerField(required=True)
    status_id = serializers.IntegerField(required=True)
    is_active = serializers.BooleanField(required=True)


class ListStaffByStatusSerializer(serializers.Serializer):
    """
    same as list user by status, 'cause staff is also user
    """
    user_id = serializers.IntegerField(allow_null=False, required=True)
    fullname = serializers.CharField(allow_null=False, required=True)
    list_dep_role_status = DepRoleStatusSerializer(many=True)

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)

    class Meta:
        fields = ('user_id', 'fullname', 'list_dep_role_status')
