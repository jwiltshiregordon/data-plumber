from uuid import uuid4, UUID

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import DataFormat


def format_builder_view(request):
    if request.method == "POST":
        build_uuid = uuid4()
        check_uuid = uuid4()
        data_format = DataFormat(
            name=request.POST["name"],
            description=request.POST["description"],
            xstate_json=request.POST["xstate_json"],
            generated_parser=request.POST["generated_parser"],
            journal="",
            build_uuid=build_uuid,
            check_uuid=check_uuid,
        )
        data_format.save()
        return JsonResponse(dict(check_url=reverse("format_checker", kwargs=dict(check_uuid=check_uuid))))
    return render(request, "main/format_builder.html", {})


def format_checker_view(request, check_uuid):
    data_format = get_object_or_404(DataFormat, check_uuid=check_uuid)
    context = dict(
        check_uuid=check_uuid,
        data_format=data_format,
        parser_url=reverse('format_parser', kwargs=dict(check_uuid=check_uuid))
    )
    return render(request, "main/format_checker.html", context)


def parser_view(request, check_uuid):
    data_format = get_object_or_404(DataFormat, check_uuid=check_uuid)
    file_contents = data_format.generated_parser
    return HttpResponse(file_contents, content_type='text/plain')


def search_view(request):
    context = dict(not_found=False)
    if request.method == 'POST':
        try:
            check_uuid = UUID(request.POST.get("format_id", ''))
        except (ValueError, ValidationError):
            context["invalid_id"] = True
            return render(request, 'main/format_search.html', context)
        data_format = DataFormat.objects.filter(check_uuid=check_uuid)
        if data_format.exists():
            return redirect('format_checker', check_uuid)
        context["not_found"] = True
    return render(request, 'main/format_search.html', context)
