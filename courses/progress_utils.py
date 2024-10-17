from courses.models import Lesson, UserProgress




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

def get_next_lesson(user, course):
    completed_lessons = UserProgress.objects.filter(
        user=user, 
        lesson__course=course, 
        completed=True
    ).values_list('lesson_id', flat=True)

    return Lesson.objects.filter(course=course).exclude(id__in=completed_lessons).first()

def mark_lesson_completed(user, lesson):
    course = lesson.course
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        course=course,
        lesson=lesson,
        defaults={'completed': True}
    )
    if not created:
        progress.completed = True
        progress.save()


