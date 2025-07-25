from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adicione claims extras se quiser
        token['matricula'] = user.matricula
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Substitui username por matrícula
        attrs['username'] = attrs.get('matricula')
        return super().validate(attrs)
