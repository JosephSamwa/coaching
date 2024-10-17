from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser
from courses.models import Lesson, Section, Course, Enrollment
from payments.models import Payment

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'date_joined', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active', 'date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username',)
    ordering = ('date_joined',)
    readonly_fields = ('date_joined', 'last_login')

admin.site.register(CustomUser, CustomUserAdmin)

class EnrollmentAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        try:
            obj.save()
            self.message_user(request, f'The enrollment “{obj.user} enrolled in {obj.course}” was added successfully.', level=messages.SUCCESS)
        except ValidationError as e:
            self.message_user(request, e.message, level=messages.ERROR)
admin.site.register(Enrollment, EnrollmentAdmin)

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_name']
    search_fields = ['title', 'course__title']

    def course_name(self, obj):
        return obj.course.title
    course_name.admin_order_field = 'course'
    course_name.short_description = 'Course Name'

class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'students_enrolled']
    search_fields = ['id', 'title', 'price', 'students_enrolled']

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Section)

admin.site.site_header = "ACUMENINK Admin Panel"
admin.site.site_title = "ACUMENINK Admin Panel"
admin.site.index_title = "ACUMENINK Admin Panel"
