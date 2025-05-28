from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rec_core.recommender import recommend_for

User = get_user_model()

class Command(BaseCommand):
    help = 'Test recommender system for a user'

    def handle(self, *args, **options):
        username = 'schdo21u925'  # можно сделать параметром команды

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            return

        recommendations = recommend_for(user, top_k=5)

        self.stdout.write(f'Recommended books for user "{username}":')
        for book in recommendations:
            self.stdout.write(f'- {book.title} (id={book.id})')
