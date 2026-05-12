from django.test import TestCase
from .models import Resource


class ResourceModelTest(TestCase):
    def setUp(self):
        self.resource = Resource.objects.create(
            name="CSci Textbooks",
            category="Books",
            location="Meriam Library",
            desc="A collection of computer science textbooks available for short-term loan.",
            avail="Available",
        )

    def test_resource_creation(self):
        """A Resource object is saved with the correct field values."""
        resource = Resource.objects.get(id=self.resource.id)
        self.assertEqual(resource.name, "CSci Textbooks")
        self.assertEqual(resource.category, "Books")
        self.assertEqual(resource.location, "Meriam Library")
        self.assertEqual(resource.desc, "A collection of computer science textbooks available for short-term loan.")
        self.assertEqual(resource.avail, "Available")

    def test_resource_setters(self):
        resource = Resource.objects.get(id=self.resource.id)
        resource.set_name("NAME")
        resource.set_category("Books")
        resource.set_location("LOCATION")
        resource.set_desc("DESC")
        resource.set_avail("Available")
        self.assertEqual(resource.name, "NAME")
        self.assertEqual(resource.category, "Books")
        self.assertEqual(resource.location, "LOCATION")
        self.assertEqual(resource.desc, "DESC")
        self.assertEqual(resource.avail, "Available")

    def test_resource_getters(self):
        resource = Resource.objects.get(id=self.resource.id)
        self.assertEqual(resource.get_name(), "CSci Textbooks")
        self.assertEqual(resource.get_category(), "Books")
        self.assertEqual(resource.get_location(), "Meriam Library")
        self.assertEqual(resource.get_desc(), "A collection of computer science textbooks available for short-term loan.")
        self.assertEqual(resource.get_avail(), "Available")
    
    def test_category_choices(self):
        """Resource accepts each valid category choice defined on the model."""
        valid_categories = [value for value, _ in Resource._meta.get_field("category").choices]
        for category in valid_categories:
            resource = Resource.objects.create(
                name=f"Test {category}",
                category=category,
                location="Campus",
                desc="Test description.",
                avail="Available",
            )
            self.assertEqual(resource.category, category)

    def test_availability_choices(self):
        """Resource accepts each valid availability choice defined on the model."""
        valid_avail = [value for value, _ in Resource._meta.get_field("avail").choices]
        for avail in valid_avail:
            resource = Resource.objects.create(
                name=f"Resource {avail}",
                category="Rooms",
                location="Campus",
                desc="Test description.",
                avail=avail,
            )
            self.assertEqual(resource.avail, avail)

    def test_resource_count_increases_on_creation(self):
        """Creating an additional Resource increases the count in the database."""
        initial_count = Resource.objects.count()
        Resource.objects.create(
            name="Study Room B",
            category="Rooms",
            location="Meriam Library",
            desc="A quiet study room available for booking.",
            avail="Limited",
        )
        self.assertEqual(Resource.objects.count(), initial_count + 1)

    def test_resource_deletion(self):
        """Deleting a Resource removes it from the database."""
        resource_id = self.resource.id
        self.resource.delete()
        self.assertFalse(Resource.objects.filter(id=resource_id).exists())
