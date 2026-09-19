from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def pagination(request, invoices):
    """
    Paginate the given list of invoices.
    """
    # default page = 1
    default_page = 1
    page = request.GET.get("page", default_page)
    items_per_page = 5  # Number of invoices to display per page
    paginator = Paginator(
        invoices, items_per_page
    )  # Show items_per_page invoices per page

    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)

    return items_page  # Return the paginated invoices for rendering in the template
