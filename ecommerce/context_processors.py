from .models import School
from django.db.models import Q
from django.http import JsonResponse


# lists schools in the base.html
def schools_listed(request):
    schools = School.objects.all()[:5]
    print('School listed: ', schools)
    return {'schools': schools}


# also lists schools in the base.html
def schools_fulllist(request):
    school_listing = School.objects.all()[:5]
    print('School listed: ', school_listing)
    return {'school_listing': school_listing}


def all_schools(request):
    query = request.GET.get('q')
    if query:
        words = query.split()
        q_object = Q()
        for word in words:
            q_object |= Q(school_name__icontains=word)
        schools = School.objects.filter(q_object)
    else:
        schools = School.objects.all()
    return {'all_schools': schools}



