from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    # 필요하다면 여기에 추가 필드 작성
    pass
# 프로필, 프로필 사진 함께 나오는 class
class Profile(models.Model):
    # User 모델과 1:1 관계를 설정합니다. 사용자가 삭제되면 프로필도 삭제됩니다.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # 프로필 이미지를 저장하는 필드입니다.
    # upload_to='profile_pics'는 이미지가 'media/profile_pics' 폴더에 저장되도록 합니다.
    # default='default.jpg'는 사용자가 사진을 올리지 않았을 때 보여줄 기본 이미지입니다.
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

