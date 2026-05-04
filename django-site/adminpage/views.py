from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Resource, Reservation
from datetime import date
import json


# ── Resource views ────────────────────────────────────────────────────────────

@require_POST
def add_resource(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    name     = data.get("name", "").strip()
    location = data.get("location", "").strip()
    category = data.get("category", "").strip()
    desc     = data.get("desc", "").strip()
    avail    = data.get("avail", "").strip()

    if not name or not location or not desc:
        return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

    resource = Resource.objects.create(
        name=name, location=location, category=category, desc=desc, avail=avail
    )
    return JsonResponse({
        "success": True,
        "resource": {
            "id": resource.id, "name": resource.name, "location": resource.location,
            "category": resource.category, "desc": resource.desc, "avail": resource.avail,
        }
    })


@require_POST
def remove_resource(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    resource_id = data.get("id", "")
    if not resource_id:
        return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

    Resource.objects.filter(id=resource_id).delete()
    return JsonResponse({"success": True})


def get_resources(request):
    resources = list(Resource.objects.values("id", "name", "category", "location", "desc", "avail"))
    return JsonResponse({"resources": resources})


# ── Reservation views ─────────────────────────────────────────────────────────

@require_POST
def make_reservation(request):
    """Create a reservation. Returns 409 if slot already taken."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    resource_id = data.get("resource_id")
    user_email  = data.get("user_email", "").strip()
    time_slot   = data.get("time_slot", "").strip()
    # Accept a date string (YYYY-MM-DD) or default to today
    date_str    = data.get("date", str(date.today()))

    if not resource_id or not user_email or not time_slot:
        return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        return JsonResponse({"success": False, "error": "Resource not found"}, status=404)

    reservation, created = Reservation.objects.get_or_create(
        resource=resource,
        time_slot=time_slot,
        date=date_str,
        defaults={"user_email": user_email},
    )

    if not created:
        return JsonResponse({"success": False, "error": "That slot is already taken"}, status=409)

    return JsonResponse({
        "success": True,
        "reservation": {
            "id": reservation.id,
            "resource_id": resource.id,
            "resource_name": resource.name,
            "time_slot": reservation.time_slot,
            "date": str(reservation.date),
        }
    })


@require_POST
def cancel_reservation(request):
    """Delete a reservation — only the owner can cancel."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    reservation_id = data.get("id")
    user_email     = data.get("user_email", "").strip()

    if not reservation_id or not user_email:
        return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

    deleted, _ = Reservation.objects.filter(id=reservation_id, user_email=user_email).delete()
    if deleted == 0:
        return JsonResponse({"success": False, "error": "Reservation not found or not yours"}, status=404)

    return JsonResponse({"success": True})


def get_reservations(request):
    """
    Two modes:
      ?user_email=x@y.z          → reservations for that user
      ?resource_id=5&date=YYYY-MM-DD → taken slots for a resource on a date
    """
    user_email  = request.GET.get("user_email")
    resource_id = request.GET.get("resource_id")
    date_str    = request.GET.get("date", str(date.today()))

    if user_email:
        qs = Reservation.objects.filter(user_email=user_email).select_related("resource")
        data = [
            {
                "id": r.id,
                "resource_id": r.resource.id,
                "resource_name": r.resource.name,
                "time_slot": r.time_slot,
                "date": str(r.date),
                "created_at": r.created_at.isoformat(),
            }
            for r in qs
        ]
        return JsonResponse({"reservations": data})

    if resource_id:
        taken = list(
            Reservation.objects.filter(resource_id=resource_id, date=date_str)
            .values_list("time_slot", flat=True)
        )
        return JsonResponse({"taken_slots": taken})

    return JsonResponse({"error": "Provide user_email or resource_id"}, status=400)


# ── Page render ───────────────────────────────────────────────────────────────

@ensure_csrf_cookie
def showAdminPage(request):
    return render(request, 'adminpage/adminpage.html')