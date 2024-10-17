from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class TimestampIDField(models.BigAutoField):
    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, (int, str)):
            return super().get_prep_value(value)
        if isinstance(value, timezone.datetime):
            return int(value.timestamp())
        return super().get_prep_value(value)

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    students_enrolled = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Section(models.Model):
    course = models.ForeignKey(Course, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPES = (
        ('video', 'Video'),
        ('article', 'Article'),
    )
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=LESSON_TYPES)
    order = models.PositiveIntegerField()
    content = models.TextField(blank=True)

    # Video-specific fields
    video_url = models.URLField(blank=True, null=True)
    video_duration = models.PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)

    # Article-specific fields
    article_content = models.TextField(blank=True)
    article_read_time = models.PositiveIntegerField(help_text="Estimated read time in minutes", null=True, blank=True)

    class Meta:
        ordering = ['section__order', 'order']
        unique_together = ['section', 'order']

    def __str__(self):
        return f"{self.section.course.title} - {self.section.title} - {self.title}"

    def clean(self):
        if self.type == 'video' and not self.video_url:
            raise ValidationError("Video URL is required for video lessons.")
        elif self.type == 'article' and not self.article_content:
            raise ValidationError("Article content is required for article lessons.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']

    @property
    def course(self):
        return self.lesson.course

def calculate_course_progress(user, course):
    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = UserProgress.objects.filter(
        user=user, 
        lesson__course=course, 
        completed=True
    ).count()

    if total_lessons > 0:
        progress_percentage = (completed_lessons / total_lessons) * 100
    else:
        progress_percentage = 0
    return round(progress_percentage, 2)

def mark_lesson_completed(user, lesson):
    progress, created = UserProgress.objects.update_or_create(
        user=user,
        lesson=lesson,
        defaults={'completed': True}
    )

def get_next_lesson(user, course):
    completed_lessons = UserProgress.objects.filter(
        user=user, 
        lesson__course=course, 
        completed=True
    ).values_list('lesson_id', flat=True)

    return Lesson.objects.filter(course=course).exclude(id__in=completed_lessons).first()

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_enrollments')
    id = TimestampIDField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new enrollment
            self.course.students_enrolled += 1
            self.course.save()
        super().save(*args, **kwargs)