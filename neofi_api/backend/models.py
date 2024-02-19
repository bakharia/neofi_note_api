from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    """
    Model representing a note created by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who created the note
    title = models.CharField(max_length=100)  # Title of the note
    content = models.TextField()  # Content of the note
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp indicating when the note was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp indicating when the note was last updated

    class Meta:
        app_label = 'backend'  # Define the app label for the model

class SharedNoteUser(models.Model):
    """
    Model representing a shared note between users.
    """
    note = models.ForeignKey(Note, related_name='shared_users', on_delete=models.CASCADE)  # The note being shared
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user with whom the note is shared

    class Meta:
        app_label = 'backend'  # Define the app label for the model

class NoteVersion(models.Model):
    """
    Model representing a version of a note.
    """
    note = models.ForeignKey(Note, related_name='versions', on_delete=models.CASCADE)  # The note associated with this version
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp indicating when the version was created
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who created this version
    changes = models.TextField()  # Changes made in this version

    class Meta:
        app_label = 'backend'  # Define the app label for the model
