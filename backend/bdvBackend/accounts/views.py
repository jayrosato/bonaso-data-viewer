from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login, authenticate
import json

User = get_user_model()
from accounts.models import UserProfile

class Settings(LoginRequiredMixin, View):
    def get(self, request):
        user = self.request.user
        userProfile = user.userprofile
        return render(request, 'accounts/settings.html', {'user':user, 'userProfile':userProfile})

class Profile(LoginRequiredMixin, generic.DetailView):
    model=User
    template_name='accounts/profile.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        from forms.models import Response, Respondent, Form
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        pk=self.kwargs['pk']
        employee = get_object_or_404(User, id=pk)
        responses = Response.objects.filter(created_by=employee.id).count()
        context['responses'] = responses
        respondents = Respondent.objects.filter(created_by=employee.id).count()
        context['respondents'] = respondents
        forms = Form.objects.filter(created_by=employee.id).count()
        context['forms'] = forms
        direct_team = UserProfile.objects.filter(supervisor=employee.id).count()
        underlings = UserProfile.objects.filter(manager=employee.id).count()
        context['direct_team'] = direct_team
        context['underlings'] = underlings

        try:
            employee_user_profile = employee.userprofile
        except UserProfile.DoesNotExist:
            employee_user_profile = None

        context['employee_user_profile'] = employee_user_profile
        return context


#for verifying mobile logins
'''
attempt = {
    'username':username,
    'password': raw_password
}
'''
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class MobileLoginRequest(View):
    def post(self, request):
        attempt = json.loads(request.body)
        username = attempt['username']
        password = attempt['password']
        user=authenticate(username=username, password=password)
        if user:
            login(request, user)
            response = {
                'status':'success',
                'session_id':'12345'
            }
        else:
            response = {
                'status':'Incorrect username or password.'
            }
        return JsonResponse(response)