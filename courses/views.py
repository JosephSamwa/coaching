from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from .models import Course, Enrollment, Lesson, UserProgress
from .progress_utils import mark_lesson_completed, calculate_course_progress, get_next_lesson
import logging

logger = logging.getLogger(__name__)

def course_list(request):
    logger.debug("Fetching all courses")
    courses = Course.objects.all()
    logger.debug(f"Found {courses.count()} courses")
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    logger.debug(f"Fetching course with id {course_id}")
    course = get_object_or_404(Course, id=course_id)
    logger.debug(f"Found course: {course.title}")
    return render(request, 'courses/course_detail.html', {'course': course})

@login_required
def enroll(request, course_id):
    logger.debug(f"Fetching course with id {course_id} for enrollment")
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the user is already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        logger.debug("User already enrolled in the course")
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:user_courses', course_id=course.id)
    
    if request.method == 'POST':
        logger.debug("POST request received for enrollment")
        # Redirect to payment initiation
        return redirect('payments:initiate_payment', course_id=course.id)
    
    # If it's a GET request, show the enrollment confirmation page
    return render(request, 'courses/enroll.html', {'course': course})


def home(request):
    logger.debug("Rendering home page")
    return render(request, 'courses/home.html')

def about(request):
    logger.debug("Rendering about page")
    return render(request, 'courses/about.html')

@login_required
def user_course_details(request):
    logger.debug("Fetching user enrollments")
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    logger.debug(f"Found {enrollments.count()} enrollments")
    return render(request, 'users/dashboard.html', {'enrollments': enrollments})
@login_required
def lesson_view(request, lesson_id):
    logger.debug(f"Fetching lesson with id {lesson_id}")
    
    lesson = get_object_or_404(Lesson.objects.select_related('course', 'section'), id=lesson_id)
    course = lesson.course
    user = request.user

    if request.method == 'POST':
        logger.debug(f"Marking lesson {lesson_id} as completed")
        UserProgress.objects.update_or_create(
            user=user,
            lesson=lesson,
            defaults={'completed': True}
        )
        messages.success(request, f"Lesson '{lesson.title}' marked as completed!")
        
        next_lesson = get_next_lesson(user, course)
        if next_lesson:
            logger.debug(f"Redirecting to next lesson with id {next_lesson.id}")
            return redirect('lesson_view', lesson_id=next_lesson.id)
        
        logger.debug(f"Redirecting to course detail with id {course.id}")
        return redirect('course_detail', course_id=course.id)

    user_progress, _ = UserProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={'completed': False}
    )
    
    all_lessons = list(Lesson.objects.filter(course=course).order_by('section__order', 'order'))
    current_index = all_lessons.index(lesson)
    previous_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None

    context = {
        'lesson': lesson,
        'course': course,
        'user_progress': user_progress,
        'course_progress': calculate_course_progress(user, course),
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
    }

    logger.debug(f"Rendering lesson view for lesson {lesson_id}")
    return render(request, 'courses/lesson_view.html', context)



@login_required
def user_courses(request):
    # Get all courses the user is enrolled in
    user_progress = UserProgress.objects.filter(user=request.user).select_related('lesson__course')
    
    # Group by course and get the latest progress for each course
    course_progress = {}
    for progress in user_progress:
        course = progress.lesson.course
        if course.id not in course_progress or progress.last_accessed > course_progress[course.id]['last_accessed']:
            course_progress[course.id] = {
                'course': course,
                'last_accessed': progress.last_accessed
            }
    
    courses_data = []
    for course_id, data in course_progress.items():
        course = data['course']
        total_lessons = Lesson.objects.filter(course=course).count()
        completed_lessons = UserProgress.objects.filter(
            user=request.user, 
            lesson__course=course, 
            completed=True
        ).count()
        
        progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        
        courses_data.append({
            'course': course,
            'progress': round(progress_percentage, 2),
            'last_accessed': data['last_accessed']
        })
    
    # Sort courses by last_accessed (most recent first)
    courses_data.sort(key=lambda x: x['last_accessed'], reverse=True)
    
    return render(request, 'users/user_courses.html', {'courses_data': courses_data})