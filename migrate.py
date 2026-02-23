import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yubutb.settings")

# Initialize Django
django.setup()

# Now you can import and use your Django models and other components
from app.models import Video, Post, VideoComment, PostComment
from django.contrib.auth import get_user_model

User = get_user_model()

# Your script logic goes here
def videoMigrate():
    videoCount = Video.objects.count()
    videos = Video.objects.all()
    videoAuthors = []

    for i in range(videoCount):
        video = videos[i]
        videoAuthors.append(video.author)
    print(videoAuthors)

    videoAuthorID = []
    
    for i in videoAuthors:
        videoAuthorID.append(User.objects.get(username=i).id)

    print(videoAuthorID)

    for i in range(videoCount):
        video = videos[i]
        video.author=videoAuthorID[i]
        video.save()

def postMigrate():
    postCount = Post.objects.count()
    posts = Post.objects.all()
    postAuthors = []

    for i in range(postCount):
        post = posts[i]
        postAuthors.append(post.author)
    print(postAuthors)

    postAuthorID = []

    for i in postAuthors:
        postAuthorID.append(User.objects.get(username=i).id)

    print(postAuthorID)

    for i in range(postCount):
        post = posts[i]
        post.author=postAuthorID[i]
        post.save()



if __name__ == "__main__":
    videoMigrate()
    postMigrate()
