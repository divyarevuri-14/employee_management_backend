from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Employee


def health_check(request):
    return JsonResponse({
        "status": "success",
        "message": "Employee Management Backend is running"
    })


@csrf_exempt
def employee_list(request):

    if request.method == "POST":
        data = json.loads(request.body)

        employee = Employee.objects.create(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            department=data["department"],
            designation=data["designation"]
        )

        return JsonResponse({
            "status": "success",
            "message": "Employee created successfully",
            "employee_id": employee.id
        }, status=201)

    return JsonResponse({
        "status": "error",
        "message": "Method not allowed"
    }, status=405)