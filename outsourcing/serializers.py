from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from .models import Order, Organization, OrderRequest, Tag, Review

from django.core.mail import send_mail

from .tokens import account_activation_token

from django.conf import settings


class OrganizationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Organization
        fields = ('id', 'email', 'name', 'description', 'first_name', 'last_name', 'patronymic', 'itn', 'position',
                  'website', 'address', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        model: Organization = super().create(validated_data)
        model.is_active = False
        model.save()
        send_mail('Confirmation token', 'Token: ' + account_activation_token.make_token(model),
                  settings.EMAIL_HOST_USER, [model.email])
        return model


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', )


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        # customer is always current user, when created performer is null, status == STATUS_NOT_ACCEPTED
        read_only_fields = ('customer', 'performer', 'status', 'date_created', 'date_completed', 'tags')

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        print('Creating')
        return super().create(validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['customer'] = {
            "id": OrganizationSerializer(instance.customer).data['id'],
            "name": OrganizationSerializer(instance.customer).data['name']
        }
        if instance.performer:
            response['performer'] = {
                "id": OrganizationSerializer(instance.performer).data['id'],
                "name": OrganizationSerializer(instance.performer).data['name']
            }
        return response

    # def save(self, **kwargs):
    #     print('beginning')
    #     super(OrderSerializer, self).save()
    #     print('hi')
    #     tags = self.validated_data['tags']
    #     print(tags)
    #     for tag in tags:
    #         print("Tag: %s" % tag)
    #         if tag not in self.instance.tags.all():
    #             print("tag is not in instance.tags")
    #             if Tag.objects.filter(name=tag):
    #                 print("it's an existing tag")
    #                 tag = Tag.objects.get(name=tag)
    #             else:
    #                 print("it's a new tag")
    #                 tag = Tag.objects.create(name=tag)
    #             self.instance.tags.add(tag)
    #             print(self.instance.tags)
    #     return self.instance


class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRequest
        fields = '__all__'
        read_only_fields = ('performer', 'order',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['performer'] = {
            "id": OrganizationSerializer(instance.performer).data['id'],
            "name": OrganizationSerializer(instance.performer).data['name']
        }
        return response


class AcceptOrderRequestSerializer(serializers.Serializer):
    order_request_id = serializers.IntegerField()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('reviewer', 'date_created', 'organization', )

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        org_pk = self.context['view'].kwargs.get('pk')
        validated_data['organization'] = Organization.objects.get(pk=org_pk)
        return super().create(validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['reviewer'] = OrganizationSerializer(instance.reviewer).data['name']
        return response


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    email = serializers.EmailField()