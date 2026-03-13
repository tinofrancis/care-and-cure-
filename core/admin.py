from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PatientProfile, DoctorProfile, Doctor, Appointment

class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (DoctorProfileInline,)
    list_display = ('username', 'email', 'is_doctor', 'is_patient', 'is_staff')
    list_filter = ('is_doctor', 'is_patient', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_doctor', 'is_patient')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Roles', {'fields': ('is_doctor', 'is_patient')}),
    )

admin.site.register(User, UserAdmin)

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_name', 'age', 'gender', 'get_doctors')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'
    def get_doctors(self, obj):
        return ", ".join([f"Dr. {d.last_name}" for d in obj.doctors.all()])
    get_doctors.short_description = 'Assigned Doctors'

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'degree', 'specialist')

@admin.register(Doctor)
class DoctorAdmin(BaseUserAdmin):
    inlines = (DoctorProfileInline,)
    list_display = ('username', 'get_name', 'email', 'get_degree', 'get_specialist', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password'),
        }),
    )
    ordering = ('username',)
    
    def save_model(self, request, obj, form, change):
        # Automatically set is_doctor to True when creating a new user in this section
        if not change:
            obj.is_doctor = True
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        # Only show doctors in this list
        return super().get_queryset(request).filter(is_doctor=True)

    def get_name(self, obj):
        return obj.get_full_name()
    get_name.short_description = 'Name'

    def get_degree(self, obj):
        return obj.doctorprofile.degree if hasattr(obj, 'doctorprofile') else ''
    get_degree.short_description = 'Degree'

    def get_specialist(self, obj):
        return obj.doctorprofile.specialist if hasattr(obj, 'doctorprofile') else ''
    get_specialist.short_description = 'Specialist'
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'doctor')
    search_fields = ('patient__user__username', 'doctor__user__username')
