from django.test import TestCase, Client
from django.urls import reverse
from .models import Note
from .forms import NoteForm

# Create your tests here.


class NoteModelTest(TestCase):
    """Essential model tests."""
    
    def setUp(self):
        self.note = Note.objects.create(
            title='Test Note',
            content='Test content'
        )
    
    def test_note_creation(self):
        """Test basic note creation."""
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(self.note.title, 'Test Note')
        self.assertEqual(self.note.content, 'Test content')
    
    def test_note_str_method(self):
        """Test string representation."""
        self.assertEqual(str(self.note), 'Test Note')


class NoteViewTest(TestCase):
    """Essential view tests."""
    
    def setUp(self):
        self.client = Client()
        self.note = Note.objects.create(
            title='View Test Note',
            content='Content for view test'
        )
    
    def test_note_list_view(self):
        """Test that note list page loads."""
        response = self.client.get(reverse('note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Test Note')
    
    def test_note_detail_view(self):
        """Test that note detail page loads."""
        response = self.client.get(reverse('note_detail', args=[self.note.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Test Note')
        self.assertContains(response, 'Content for view test')
    
    def test_empty_note_list(self):
        """Test note list when empty."""
        Note.objects.all().delete()
        response = self.client.get(reverse('note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No sticky notes yet')


class NoteCRUDTest(TestCase):
    """Essential CRUD operation tests."""
    
    def setUp(self):
        self.client = Client()
    
    def test_create_note(self):
        """Test creating a new note."""
        # Get the form page
        response = self.client.get(reverse('note_create'))
        self.assertEqual(response.status_code, 200)
        
        # Submit new note
        response = self.client.post(reverse('note_create'), {
            'title': 'New Test Note',
            'content': 'New test content'
        })
        
        # Should redirect to list
        self.assertEqual(response.status_code, 302)
        
        # Note should be created
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.first()
        self.assertEqual(note.title, 'New Test Note')
    
    def test_update_note(self):
        """Test updating an existing note."""
        note = Note.objects.create(
            title='Old Title',
            content='Old content'
        )
        
        # Submit updated note
        response = self.client.post(reverse('note_update', args=[note.id]), {
            'title': 'Updated Title',
            'content': 'Updated content'
        })
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Note should be updated
        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated Title')
    
    def test_delete_note(self):
        """Test deleting a note."""
        note = Note.objects.create(
            title='Delete Me',
            content='Content to delete'
        )
        
        # Delete the note
        response = self.client.post(reverse('note_delete', args=[note.id]))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Note should be deleted
        self.assertEqual(Note.objects.count(), 0)


class NoteFormTest(TestCase):
    """Essential form tests."""
    
    def test_valid_form(self):
        """Test form with valid data."""
        form = NoteForm(data={
            'title': 'Valid Note',
            'content': 'Valid content'
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        """Test form with missing title."""
        form = NoteForm(data={
            'title': '',  # Empty title
            'content': 'Some content'
        })
        self.assertFalse(form.is_valid())


class URLTest(TestCase):
    """Essential URL tests."""
    
    def setUp(self):
        self.client = Client()
        self.note = Note.objects.create(
            title='URL Test',
            content='Content'
        )
    
    def test_homepage_url(self):
        """Test that homepage loads."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_note_urls(self):
        """Test all note-related URLs."""
        urls = [
            '/',  # Home/list
            '/note/new/',  # Create
            f'/note/{self.note.id}/',  # Detail
            f'/note/{self.note.id}/edit/',  # Update
            f'/note/{self.note.id}/delete/',  # Delete
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])