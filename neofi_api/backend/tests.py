from django.test import TestCase
from django.contrib.auth.models import User
from .models import Note, SharedNoteUser
from .serializers import UserSerializer, NoteSerializer

class NoteTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='password1')
        self.user2 = User.objects.create_user(username='testuser2', password='password2')
        
        # Create test notes
        self.note1 = Note.objects.create(user=self.user1, title='Test Note 1', content='Content 1')
        self.note2 = Note.objects.create(user=self.user2, title='Test Note 2', content='Content 2')
    
    def test_note_creation(self):
        """Test if notes are created correctly."""
        # Check if notes are created with correct data
        self.assertEqual(self.note1.title, 'Test Note 1')
        self.assertEqual(self.note2.title, 'Test Note 2')
        self.assertEqual(self.note1.content, 'Content 1')
        self.assertEqual(self.note2.content, 'Content 2')
    
    def test_note_sharing(self):
        """Test if notes can be shared with other users."""
        # Share note1 with user2
        self.note1.shared_users.add(self.user2)
        
        # Check if note1 is shared with user2
        self.assertTrue(self.note1.shared_users.filter(id=self.user2.id).exists())
    
    def test_note_deletion(self):
        """Test if notes can be deleted."""
        # Delete note1
        self.note1.delete()
        
        # Check if note1 is deleted
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(pk=self.note1.pk)
    
    def test_note_content_update(self):
        """Test if note content can be updated."""
        # Update content of note2
        new_content = 'New content'
        self.note2.content = new_content
        self.note2.save()
        
        # Check if content is updated
        updated_note = Note.objects.get(pk=self.note2.pk)
        self.assertEqual(updated_note.content, new_content)
    
    def test_note_sharing(self):
        """Test if notes can be shared with other users."""
        # Create a SharedNoteUser instance and associate it with note1 and user2
        shared_user, _ = SharedNoteUser.objects.get_or_create(note=self.note1, user=self.user2)
        
        # Check if note1 is shared with user2
        self.assertTrue(self.note1.shared_users.filter(id=shared_user.id).exists())
    
    def test_note_sharing_permission(self):
        """Test if unauthorized users cannot access shared notes."""
        # Attempt to access note2 shared by user2 with user1
        with self.assertRaises(SharedNoteUser.DoesNotExist):
            self.note2.shared_users.get(user=self.user1)
    
    def test_note_timestamps(self):
        """Test if note timestamps are updated automatically."""
        # Create a new note
        new_note = Note.objects.create(user=self.user1, title='New Note', content='New Content')
        
        # Check if created_at and updated_at timestamps are different
        self.assertNotEqual(new_note.created_at, new_note.updated_at)
    
    def test_note_ordering(self):
        """Test if notes are ordered by creation timestamp."""
        # Create a new note
        new_note = Note.objects.create(user=self.user1, title='New Note', content='New Content')
        
        # Get the latest note
        latest_note = Note.objects.latest('created_at')
        
        # Check if the latest note is the same as the newly created note
        self.assertEqual(new_note, latest_note)

class SerializerTestCase(TestCase):
    def setUp(self):
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }
        self.valid_note_data = {
            'title': 'Test Note',
            'content': 'This is a test note.'
        }
    
    def test_user_serializer_validation(self):
        """Test user serializer validation."""
        # Test valid data
        serializer = UserSerializer(data=self.valid_user_data)
        self.assertTrue(serializer.is_valid())
        
        # Test missing required field
        invalid_data = self.valid_user_data.copy()
        del invalid_data['username']
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
