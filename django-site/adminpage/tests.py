import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Resource, Reservation


# ─────────────────────────────────────────────
#  Model Tests
# ─────────────────────────────────────────────

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
        self.assertEqual(
            resource.desc,
            "A collection of computer science textbooks available for short-term loan.",
        )
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


class ReservationModelTest(TestCase):
    def setUp(self):
        self.resource = Resource.objects.create(
            name="Study Room A",
            category="Rooms",
            location="Meriam Library",
            desc="Quiet study room.",
            avail="Available",
        )
        self.reservation = Reservation.objects.create(
            resource=self.resource,
            timeSlot="10:00 AM",
            timeReserved="2026-05-10T10:00:00+00:00",
        )

    def test_reservation_creation(self):
        """A Reservation is saved with the correct resource and time slot."""
        res = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(res.resource, self.resource)
        self.assertEqual(res.timeSlot, "10:00 AM")

    def test_reservation_deletion(self):
        """Deleting a Reservation removes it from the database."""
        res_id = self.reservation.id
        self.reservation.delete()
        self.assertFalse(Reservation.objects.filter(id=res_id).exists())

    def test_cascade_delete_on_resource(self):
        """Deleting a Resource also deletes its linked Reservations."""
        res_id = self.reservation.id
        self.resource.delete()
        self.assertFalse(Reservation.objects.filter(id=res_id).exists())

    def test_multiple_reservations_same_resource(self):
        """Multiple reservations can exist for the same resource."""
        Reservation.objects.create(
            resource=self.resource,
            timeSlot="11:00 AM",
            timeReserved="2026-05-10T11:00:00+00:00",
        )
        self.assertEqual(Reservation.objects.filter(resource=self.resource).count(), 2)


# ─────────────────────────────────────────────
#  View / API Tests
# ─────────────────────────────────────────────

class AdminPageViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_admin_page_returns_200(self):
        """GET / returns the admin page with status 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_admin_page_contains_app_title(self):
        """Admin page HTML contains the app name."""
        response = self.client.get("/")
        self.assertContains(response, "Campus Resource")


class StudentPageViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_student_page_returns_200(self):
        """GET /student/ returns the student page with status 200."""
        response = self.client.get("/student/")
        self.assertEqual(response.status_code, 200)

    def test_student_page_contains_title(self):
        """Student page HTML includes the expected heading text."""
        response = self.client.get("/student/")
        self.assertContains(response, "Campus Resource")


class GetResourcesViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        Resource.objects.create(
            name="Calculator",
            category="Loanables",
            location="Library Desk",
            desc="Scientific calculator for loan.",
            avail="Available",
        )

    def test_get_resources_returns_200(self):
        """GET /get-resources/ returns 200."""
        response = self.client.get("/get-resources/")
        self.assertEqual(response.status_code, 200)

    def test_get_resources_returns_json(self):
        """Response is valid JSON with a 'resources' key."""
        response = self.client.get("/get-resources/")
        data = response.json()
        self.assertIn("resources", data)

    def test_get_resources_contains_seeded_data(self):
        """The seeded resource appears in the response."""
        response = self.client.get("/get-resources/")
        names = [r["name"] for r in response.json()["resources"]]
        self.assertIn("Calculator", names)

    def test_get_resources_empty_when_no_data(self):
        """Returns an empty list when no resources exist."""
        Resource.objects.all().delete()
        response = self.client.get("/get-resources/")
        self.assertEqual(response.json()["resources"], [])


class AddResourceViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.url = "/add-resource/"
        self.valid_payload = {
            "name": "Study Room C",
            "location": "Meriam Library, 3rd Floor",
            "category": "Rooms",
            "desc": "A quiet study room.",
            "avail": "Available",
        }

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_add_resource_success(self):
        """Valid POST creates a resource and returns success=True."""
        response = self._post(self.valid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_add_resource_creates_db_entry(self):
        """After a successful POST, the resource exists in the database."""
        self._post(self.valid_payload)
        self.assertTrue(Resource.objects.filter(name="Study Room C").exists())

    def test_add_resource_returns_resource_data(self):
        """Response includes the newly created resource's fields."""
        response = self._post(self.valid_payload)
        resource = response.json()["resource"]
        self.assertEqual(resource["name"], "Study Room C")
        self.assertEqual(resource["category"], "Rooms")

    def test_add_resource_missing_name(self):
        """POST without 'name' returns success=False."""
        payload = {**self.valid_payload, "name": ""}
        response = self._post(payload)
        self.assertFalse(response.json()["success"])

    def test_add_resource_missing_location(self):
        """POST without 'location' returns success=False."""
        payload = {**self.valid_payload, "location": ""}
        response = self._post(payload)
        self.assertFalse(response.json()["success"])

    def test_add_resource_missing_desc(self):
        """POST without 'desc' returns success=False."""
        payload = {**self.valid_payload, "desc": ""}
        response = self._post(payload)
        self.assertFalse(response.json()["success"])

    def test_add_resource_invalid_json(self):
        """Malformed JSON body returns 400."""
        response = self.client.post(
            self.url,
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_add_resource_get_not_allowed(self):
        """GET request to add-resource/ is rejected (405)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class RemoveResourceViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.url = "/remove-resource/"
        self.resource = Resource.objects.create(
            name="Old Printer",
            category="Loanables",
            location="Lab",
            desc="An old laser printer.",
            avail="Unavailable",
        )

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_remove_resource_success(self):
        """Valid POST returns success=True."""
        response = self._post({"id": self.resource.id})
        self.assertTrue(response.json()["success"])

    def test_remove_resource_deletes_db_entry(self):
        """After deletion, the resource no longer exists in the database."""
        self._post({"id": self.resource.id})
        self.assertFalse(Resource.objects.filter(id=self.resource.id).exists())

    def test_remove_resource_missing_id(self):
        """POST without 'id' returns success=False."""
        response = self._post({})
        self.assertFalse(response.json()["success"])

    def test_remove_nonexistent_resource(self):
        """Deleting a non-existent ID still returns success (no crash)."""
        response = self._post({"id": 99999})
        self.assertTrue(response.json()["success"])

    def test_remove_resource_invalid_json(self):
        """Malformed JSON returns 400."""
        response = self.client.post(self.url, data="bad", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class AddReservationViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.url = "/add-reservation/"
        self.resource = Resource.objects.create(
            name="Conference Room",
            category="Rooms",
            location="OCNL 210",
            desc="Small conference room.",
            avail="Available",
        )
        self.valid_payload = {
            "resource_id": self.resource.id,
            "timeSlot": "2:00 PM",
            "timeReserved": "2026-05-10T14:00:00+00:00",
        }

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_add_reservation_success(self):
        """Valid POST returns success=True and reservation data."""
        response = self._post(self.valid_payload)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["reservation"]["timeSlot"], "2:00 PM")

    def test_add_reservation_creates_db_entry(self):
        """After a successful POST, the reservation exists in the database."""
        self._post(self.valid_payload)
        self.assertEqual(Reservation.objects.filter(resource=self.resource).count(), 1)

    def test_add_reservation_links_correct_resource(self):
        """The created reservation is linked to the correct resource."""
        self._post(self.valid_payload)
        reservation = Reservation.objects.get(resource=self.resource)
        self.assertEqual(reservation.resource.name, "Conference Room")

    def test_add_reservation_missing_resource_id(self):
        """POST without resource_id returns success=False."""
        payload = {**self.valid_payload, "resource_id": ""}
        response = self._post(payload)
        self.assertFalse(response.json()["success"])

    def test_add_reservation_invalid_resource_id(self):
        """POST with a non-existent resource_id returns 404."""
        payload = {**self.valid_payload, "resource_id": 99999}
        response = self._post(payload)
        self.assertEqual(response.status_code, 404)

    def test_add_reservation_invalid_time(self):
        """POST with an unparseable timeReserved returns success=False."""
        payload = {**self.valid_payload, "timeReserved": "not-a-date"}
        response = self._post(payload)
        self.assertFalse(response.json()["success"])

    def test_add_reservation_invalid_json(self):
        """Malformed JSON body returns 400."""
        response = self.client.post(self.url, data="bad", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class RemoveReservationViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.url = "/remove-reservation/"
        self.resource = Resource.objects.create(
            name="Yoga Studio",
            category="Rooms",
            location="WREC",
            desc="Yoga studio for group classes.",
            avail="Available",
        )
        self.reservation = Reservation.objects.create(
            resource=self.resource,
            timeSlot="8:00 AM",
            timeReserved="2026-05-10T08:00:00+00:00",
        )

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_remove_reservation_success(self):
        """Valid POST returns success=True."""
        response = self._post({"reservation_id": self.reservation.id})
        self.assertTrue(response.json()["success"])

    def test_remove_reservation_deletes_db_entry(self):
        """After deletion, the reservation no longer exists in the database."""
        self._post({"reservation_id": self.reservation.id})
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_remove_reservation_missing_id(self):
        """POST without reservation_id returns success=False."""
        response = self._post({})
        self.assertFalse(response.json()["success"])

    def test_remove_nonexistent_reservation(self):
        """Deleting a non-existent reservation ID returns success (no crash)."""
        response = self._post({"reservation_id": 99999})
        self.assertTrue(response.json()["success"])

    def test_remove_reservation_invalid_json(self):
        """Malformed JSON returns 400."""
        response = self.client.post(self.url, data="bad", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class GetReservationsViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.resource = Resource.objects.create(
            name="3D Printer",
            category="Loanables",
            location="Maker Space",
            desc="FDM 3D printer.",
            avail="Limited",
        )
        Reservation.objects.create(
            resource=self.resource,
            timeSlot="3:00 PM",
            timeReserved="2026-05-10T15:00:00+00:00",
        )

    def test_get_reservations_returns_200(self):
        """GET /get-reservations/ returns 200."""
        response = self.client.get("/get-reservations/")
        self.assertEqual(response.status_code, 200)

    def test_get_reservations_returns_json(self):
        """Response is valid JSON with a 'reservations' key."""
        response = self.client.get("/get-reservations/")
        self.assertIn("reservations", response.json())

    def test_get_reservations_contains_seeded_data(self):
        """The seeded reservation appears in the response."""
        response = self.client.get("/get-reservations/")
        slots = [r["timeSlot"] for r in response.json()["reservations"]]
        self.assertIn("3:00 PM", slots)

    def test_get_reservations_includes_resource_info(self):
        """Each reservation entry includes nested resource data."""
        response = self.client.get("/get-reservations/")
        reservation = response.json()["reservations"][0]
        self.assertIn("resource", reservation)
        self.assertEqual(reservation["resource"]["name"], "3D Printer")

    def test_get_reservations_empty_when_no_data(self):
        """Returns an empty list when no reservations exist."""
        Reservation.objects.all().delete()
        response = self.client.get("/get-reservations/")
        self.assertEqual(response.json()["reservations"], [])


# ─────────────────────────────────────────────
#  Integration Tests
# ─────────────────────────────────────────────

class ResourceCRUDIntegrationTest(TestCase):
    """End-to-end: add a resource, verify it appears, then delete it."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_full_resource_lifecycle(self):
        # 1. Add
        add_response = self.client.post(
            "/add-resource/",
            data=json.dumps({
                "name": "Whiteboard Room",
                "location": "OCNL 202",
                "category": "Rooms",
                "desc": "Room with full-wall whiteboards.",
                "avail": "Available",
            }),
            content_type="application/json",
        )
        self.assertTrue(add_response.json()["success"])
        resource_id = add_response.json()["resource"]["id"]

        # 2. Verify it appears in get-resources
        get_response = self.client.get("/get-resources/")
        names = [r["name"] for r in get_response.json()["resources"]]
        self.assertIn("Whiteboard Room", names)

        # 3. Delete
        del_response = self.client.post(
            "/remove-resource/",
            data=json.dumps({"id": resource_id}),
            content_type="application/json",
        )
        self.assertTrue(del_response.json()["success"])

        # 4. Confirm gone
        get_response2 = self.client.get("/get-resources/")
        names2 = [r["name"] for r in get_response2.json()["resources"]]
        self.assertNotIn("Whiteboard Room", names2)


class ReservationCRUDIntegrationTest(TestCase):
    """End-to-end: add a resource, reserve it, verify reservation, cancel it."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.resource = Resource.objects.create(
            name="Tutoring Room",
            category="Tutoring",
            location="Meriam 101",
            desc="Drop-in tutoring space.",
            avail="Available",
        )

    def test_full_reservation_lifecycle(self):
        # 1. Reserve
        add_res = self.client.post(
            "/add-reservation/",
            data=json.dumps({
                "resource_id": self.resource.id,
                "timeSlot": "1:00 PM",
                "timeReserved": "2026-05-10T13:00:00+00:00",
            }),
            content_type="application/json",
        )
        self.assertTrue(add_res.json()["success"])
        reservation_id = add_res.json()["reservation"]["id"]

        # 2. Verify it appears in get-reservations
        get_res = self.client.get("/get-reservations/")
        ids = [r["id"] for r in get_res.json()["reservations"]]
        self.assertIn(reservation_id, ids)

        # 3. Cancel
        del_res = self.client.post(
            "/remove-reservation/",
            data=json.dumps({"reservation_id": reservation_id}),
            content_type="application/json",
        )
        self.assertTrue(del_res.json()["success"])

        # 4. Confirm gone
        get_res2 = self.client.get("/get-reservations/")
        ids2 = [r["id"] for r in get_res2.json()["reservations"]]
        self.assertNotIn(reservation_id, ids2)