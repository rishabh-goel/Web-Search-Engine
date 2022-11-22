from django.shortcuts import render, redirect
from django.http import HttpResponse
from core import CosineSimilarity

# Create your views here.

def home(request):
    return render(request, "core/home.html")

def analysis(request):
    # context = {
    #     'query' : 'test query (internship)',
    #     'links': ["http://ai.uic.edu/",
    #                 "http://nlp.lab.uic.edu/resources/contact/",
    #                 "http://cs.uic.edu/cs-research/labs/",
    #                 "http://cs.uic.edu/cs-events/calendar/",
    #                 "http://cs.uic.edu/previous-course-lists/",
    #                 "http://cs.uic.edu/cs-events/",
    #                 "http://engineering.uic.edu/undergraduate/majors-and-minors/",
    #                 "http://dbmc.lab.uic.edu/",
    #                 "http://cs.uic.edu/faculty-staff/postdocs/",
    #                 "http://cs.uic.edu/faculty-staff/staff/"
    #             ]
    # }
    if request.method == "POST":
        query = request.POST.get("query")
        links = CosineSimilarity.main(query)

        context = {
            'query' : query,
            'links': links
        }
    else:
        return redirect('home')
    return render(request, "core/analysis.html", context)