import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import EmployeeForm
from .models import Employee


def employee_to_dict(employee):
    return {
        "id": employee.id,
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "phone": employee.phone,
        "department": employee.department,
        "designation": employee.designation,
        "salary": str(employee.salary),
        "joining_date": employee.joining_date.isoformat(),
        "is_active": employee.is_active,
        "created_at": employee.created_at.isoformat(),
        "updated_at": employee.updated_at.isoformat(),
    }


def get_request_data(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return None

    return request.POST


@csrf_exempt
def employee_list(request):

    if request.method == "GET":
        employees = Employee.objects.all().order_by("id")

        data = [
            employee_to_dict(employee)
            for employee in employees
        ]

        return JsonResponse(
            {
                "success": True,
                "count": len(data),
                "employees": data,
            },
            status=200,
        )

    if request.method == "POST":
        data = get_request_data(request)

        if data is None:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON data.",
                },
                status=400,
            )

        form = EmployeeForm(data)

        if form.is_valid():
            employee = form.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Employee created successfully.",
                    "employee": employee_to_dict(employee),
                },
                status=201,
            )

        return JsonResponse(
            {
                "success": False,
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )

    return JsonResponse(
        {
            "success": False,
            "message": "Method not allowed.",
        },
        status=405,
    )


@csrf_exempt
def employee_detail(request, id):

    try:
        employee = Employee.objects.get(id=id)

    except Employee.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Employee not found.",
            },
            status=404,
        )

    if request.method == "GET":
        return JsonResponse(
            {
                "success": True,
                "employee": employee_to_dict(employee),
            },
            status=200,
        )

    if request.method in ["PUT", "PATCH"]:
        data = get_request_data(request)

        if data is None:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON data.",
                },
                status=400,
            )

        form = EmployeeForm(
            data,
            instance=employee
        )

        if form.is_valid():
            employee = form.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Employee updated successfully.",
                    "employee": employee_to_dict(employee),
                },
                status=200,
            )

        return JsonResponse(
            {
                "success": False,
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )

    if request.method == "DELETE":
        employee.delete()

        return JsonResponse(
            {
                "success": True,
                "message": "Employee deleted successfully.",
            },
            status=200,
        )

    return JsonResponse(
        {
            "success": False,
            "message": "Method not allowed.",
        },
        status=405,
    )