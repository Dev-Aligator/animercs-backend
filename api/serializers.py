from django.core.exceptions import ValidationError
from rest_framework import serializers
from base.models import UserFeature
from django.contrib.auth import get_user_model, authenticate


UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = '__all__'
	def create(self, validated_data):
		user_obj = UserModel.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
		user_obj.save()
		return user_obj

class UserLoginSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField()

	def check_user(self, clean_data):
		user = authenticate(username=clean_data['email'], password=clean_data['password'])
		if not user:
			raise ValidationError('user not found')
		return user

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ('email', 'username')

class UserFeatureSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserFeature
		fields = '__all__'
