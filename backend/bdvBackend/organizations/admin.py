from django.contrib import admin
from organizations.models import Organization

class OrganizationAdmin(admin.ModelAdmin):
    fieldsets = [('Basic Information', {'fields': ['organization_name']})]

admin.site.register(Organization, OrganizationAdmin)