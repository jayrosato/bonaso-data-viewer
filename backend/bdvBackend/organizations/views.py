from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from datetime import datetime
from django.views import generic, View
import calendar

from organizations.models import Organization, Target, User
from accounts.models import UserProfile

from organizations.forms import TargetForm

class ViewOrgsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'organizations/orgs/view-orgs-index.html'
    context_object_name = 'organizations'
    def get_queryset(self):
        return Organization.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context

class ViewOrgDetail(LoginRequiredMixin, generic.DetailView):
    model=Organization
    template_name='organizations/orgs/view-org-detail.html'
    context_object_name = 'organization'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        pk = self.kwargs['pk']
        child_orgs = Organization.objects.filter(parent_organization = pk)
        context['user_org'] = user_org
        context['child_orgs'] = child_orgs
        return context

class CreateOrg(LoginRequiredMixin, generic.CreateView):
    model=Organization
    template_name = 'organizations/orgs/update-org.html'
    fields = [
            'organization_name', 'parent_organization'
            ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_org = self.request.user.userprofile.organization
        if user_org.id != 3:
            if user_org.parent_organization:
                form.fields['parent_organization'].queryset = Organization.objects.filter(id=user_org.parent_organization.id)
            else:
                form.fields['parent_organization'].queryset = Organization.objects.filter(Q(id=user_org.id) | Q(id=user_org.parent_organization))
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        context['update'] = False
        return context
    
    def get_success_url(self):
        return reverse_lazy('organizations:view-org-detail', kwargs={'pk': self.object.id})

class UpdateOrg(LoginRequiredMixin, generic.UpdateView):
    model=Organization
    template_name = 'organizations/orgs/update-org.html'
    fields = [
            'organization_name', 'parent_organization'
            ]
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_org = self.request.user.userprofile.organization
        if user_org.id != 3:
            if user_org.parent_organization:
                form.fields['parent_organization'].queryset = Organization.objects.filter(id=user_org.parent_organization.id)
            else:
                form.fields['parent_organization'].queryset = Organization.objects.filter(Q(id=user_org.id) | Q(id=user_org.parent_organization))
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        context['update'] = True
        return context
    
    def get_success_url(self):
        return reverse_lazy('organizations:view-org-detail', kwargs={'pk': self.object.id})
    
class DeleteOrg(LoginRequiredMixin, generic.DeleteView):
    model=Organization
    success_url = reverse_lazy('organizations:view-orgs-index')

class ViewTargetsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'organizations/targets/view-targets-index.html'
    context_object_name = 'targets'

    def get_queryset(self):
        return Target.objects.filter(target_start__lte= datetime.today(), target_end__gte = datetime.today()).order_by('organization')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context
    
class ViewTargetDetail(LoginRequiredMixin, generic.DetailView):
    template_name = 'organizations/targets/view-target-detail.html'
    context_object_name = 'target'

    def get_queryset(self):
        return Target.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context

class CreateTarget(LoginRequiredMixin, generic.CreateView):
    model=Target
    template_name = 'organizations/targets/update-target.html'
    form_class = TargetForm
    def get_success_url(self):  
        return reverse_lazy('organizations:view-target-detail', kwargs={'pk': self.object.id})

class UpdateTarget(LoginRequiredMixin, generic.UpdateView):
    model=Target
    template_name = 'organizations/targets/update-target.html'
    form_class = TargetForm
    def get_success_url(self):
        return reverse_lazy('organizations:view-target-detail', kwargs={'pk': self.object.id})

class DeleteTarget(LoginRequiredMixin, generic.DeleteView):
    model=Target
    success_url = reverse_lazy('organizations:view-targets-index')

class EmployeesIndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'organizations/orgs/view-employees-index.html'
    context_object_name = 'employees'
    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context

class EmployeeDetailView(LoginRequiredMixin, generic.DetailView):
    model=User
    template_name='organizations/orgs/view-employee-detail.html'
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

class CreateUser(LoginRequiredMixin, generic.CreateView):
    model = UserProfile
    fields = '__all__'
    template_name = 'organizations/orgs/create-user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context
    
    def get_success_url(self):
        return reverse_lazy('organiations:view-employee-detail', kwargs={'pk': self.object.id})
    

class GetTargetDetails(LoginRequiredMixin, View):
    def get(self, request, pk):
        target = Target.objects.filter(id=pk).first()
        data = {
            "labels": ['Target', 'Actual'],
            "datasets": [{
                "label": f'{calendar.month_name[target.target_end.month]}, {target.target_end.year}',
                "data": [target.target_amount, target.get_actual()],
                'backgroundColor': "#FFFFFF",
                'scaleFontColor': '#FFFFFF',
                },
            ]
        }
        return JsonResponse(data)
