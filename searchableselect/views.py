try:
    # Django <=1.9
    from django.db.models.loading import get_model
except ImportError:
    # Django 1.10+
    from django.apps import apps

    get_model = apps.get_model

from django.utils.encoding import smart_str
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def filter_models(request):
    model_name = request.GET.get("model")
    search_field = request.GET.get("search_field")
    value = request.GET.get("q")
    limit = int(request.GET.get("limit", 10))
    addition_filter = request.GET.get("addition_filter") or False
    addition_filter_condition = request.GET.get("addition_filter_condition") or False
    try:
        model = get_model(model_name)
    except LookupError as e:  # pragma: no cover
        return JsonResponse(dict(status=400, error=e.message))
    except (ValueError, AttributeError) as e:  # pragma: no cover
        return JsonResponse(dict(status=400, error="Malformed model parameter."))

    values = model.objects.all()
    if addition_filter and eval(addition_filter_condition):
        values = eval(addition_filter)
    values = values.filter(**{"{}__icontains".format(search_field): value})

    values = values[:limit]
    values = [dict(pk=v.pk, name=smart_str(v)) for v in values]

    return JsonResponse(dict(result=values))
