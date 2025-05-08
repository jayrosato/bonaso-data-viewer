from django.urls import path

from . import views

app_name = "organizations"
urlpatterns = [
    path('', views.ViewOrgsIndex.as_view(), name='view-orgs-index'),
    path('<int:pk>', views.ViewOrgDetail.as_view(), name='view-org-detail'),
    path('create', views.CreateOrg.as_view(), name='create-org'),
    path('<int:pk>/update', views.UpdateOrg.as_view(), name='update-org'),
    path('<int:pk>/delete', views.DeleteOrg.as_view(), name='delete-org'),
    path('team', views.EmployeesIndexView.as_view(), name='view-employees-index'),
    path('team/<int:pk>', views.EmployeeDetailView.as_view(), name='view-employee-detail'),
    path('team/addmember', views.CreateUser.as_view(), name='create-user'),

    path('targets', views.ViewTargetsIndex.as_view(), name='view-targets-index'),
    path('targets/<int:pk>', views.ViewTargetDetail.as_view(), name='view-target-detail'),
    path('targets/create', views.CreateTarget.as_view(), name='create-target'),
    path('targets/<int:pk>/update', views.UpdateTarget.as_view(), name='update-target'),
    path('targets/<int:pk>/delete', views.DeleteTarget.as_view(), name='delete-target'),

    path('targets/<int:pk>/query', views.GetTargetDetails.as_view()),
]