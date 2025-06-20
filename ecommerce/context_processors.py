from .models import School


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
