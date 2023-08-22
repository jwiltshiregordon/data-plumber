from django.urls import reverse, resolve


def navigation_links(request):
    current_url_name = resolve(request.path_info).url_name

    return dict(
        home_url=reverse('home'),
        format_builder_url=reverse('format_builder'),
        format_search_url=reverse('format_search'),
        format_builder_active=(current_url_name == 'format_builder'),
        format_checker_active=(current_url_name in ['format_checker', 'format_search']),
    )
