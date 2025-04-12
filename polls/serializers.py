from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from .models import Poll, PollOption, Vote
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PollOptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PollOption
        fields = ['id', 'text', 'vote_count']

    def get_vote_count(self, obj):
        return Vote.objects.filter(option=obj).count()

class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ['id', 'question', 'has_expiry', 'created_by', 'created_at', 'options']
        read_only_fields = ['id', 'created_by', 'created_at']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        for option_data in options_data:
            PollOption.objects.create(poll=poll, **option_data)
        return poll

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)

        # Update Poll fields
        instance.question = validated_data.get('question', instance.question)
        instance.has_expiry = validated_data.get('has_expiry', instance.has_expiry)
        instance.save()

        if options_data is not None:
            # Clear existing options
            instance.options.all().delete()

            # Add new options
            for option_data in options_data:
                PollOption.objects.create(poll=instance, **option_data)

        return instance 
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        data['user'] = user
        return data
    

class VoteSerializer(serializers.ModelSerializer):
    poll = serializers.UUIDField()  # Accepts UUID
    option = serializers.CharField()  # Accepts text

    class Meta:
        model = Vote
        fields = ['id', 'poll', 'option', 'voted_at']
        read_only_fields = ['id', 'voted_at']

    def validate(self, data):
        poll_id = data.get("poll")
        option_text = data.get("option")

        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            raise serializers.ValidationError("Poll not found.")

        try:
            option = PollOption.objects.get(poll=poll, text=option_text)
        except PollOption.DoesNotExist:
            raise serializers.ValidationError("Option not found in this poll.")

        data["poll"] = poll
        data["option"] = option
        return data

    def create(self, validated_data):
        option = validated_data['option']
        option.vote_count += 1
        option.save()  # Persist vote count change

        return Vote.objects.create(**validated_data)