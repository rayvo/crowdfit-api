""""
@author: moon
@date: 2019.02.27
"""

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
# for lazy text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model

# for custom user
from crowdfit_api.user.models import UserRoleStatus
from crowdfit_api.user.serializers import UserSerializer, DepartmentRoleSerializers, StatusSerializers, \
    DocumentFileSerializers

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
    doc_file = serializers.FileField(allow_null=False, use_url=True)

    class Meta:
        fields = ('user_id', 'doc_file')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)


class RequestUserRoleStatusSerializer(serializers.Serializer):
    # "user_id: localStorage,
    # department_role_id: null
    # status_id: ***
    # staff_id: null,
    # document_file_id: null,
    # is_active: false"
    user_id = serializers.IntegerField(allow_null=False, required=True)
    status_id = serializers.IntegerField(allow_null=False)
    is_active = serializers.BooleanField(allow_null=False)

    class Meta:
        fields = ('user_id', 'status_id', 'is_active')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)


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
    doc_file = serializers.FileField(allow_null=False, use_url=True)

    class Meta:
        fields = ('user_id', 'doc_file_id', 'doc_file')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)


class RequestUserRoleStatusSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=False, required=True)
    document_file_id = serializers.IntegerField(allow_null=False, required=True)
    department_role_id = serializers.IntegerField(allow_null=False, required=True)

    class Meta:
        fields = ('user_id', 'doc_file_id', 'department_role_id')

    def create(self, validated_data):
        return Response(data={}, status=status.HTTP_403_FORBIDDEN)
