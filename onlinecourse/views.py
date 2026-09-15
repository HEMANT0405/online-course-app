from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Course, Question, Choice, Submission


@login_required
def submit(request, course_id):
    if request.method != "POST":
        return HttpResponse("Invalid request")

    # Get the course
    course = get_object_or_404(Course, id=course_id)

    # Get all questions for this course
    questions = Question.objects.filter(course=course)

    selected_ids = []

    # Save the student's answers
    for question in questions:

        selected_choice_id = request.POST.get(
            "question_" + str(question.id)
        )

        if selected_choice_id:

            selected_ids.append(int(selected_choice_id))

            choice = get_object_or_404(
                Choice,
                id=selected_choice_id,
                question=question
            )

            Submission.objects.create(
                user=request.user,
                question=question,
                choice=choice
            )

    # Calculate score
    grade = 0
    possible = questions.count()

    for question in questions:

        selected_choice_id = request.POST.get(
            "question_" + str(question.id)
        )

        if selected_choice_id:

            choice = get_object_or_404(
                Choice,
                id=selected_choice_id,
                question=question
            )

            if choice.is_correct:
                grade += 1

    # Get the latest submission ID
    latest_submission = Submission.objects.filter(
        user=request.user,
        question__course=course
    ).order_by("-id").first()

    if latest_submission:
        submission_id = latest_submission.id
    else:
        submission_id = 0

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        {
            "course": course,
            "selected_ids": selected_ids,
            "grade": grade,
            "possible": possible,
            "submission_id": submission_id,
        }
    )


@login_required
def show_exam_result(request, course_id, submission_id):

    # Get the course
    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Get the submission
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )

    # Get all submissions of this user for this course
    submissions = Submission.objects.filter(
        user=request.user,
        question__course=course
    ).select_related(
        "question",
        "choice"
    )

    # Store selected choice IDs
    selected_ids = []

    for item in submissions:
        selected_ids.append(item.choice.id)

    # Total questions
    possible = Question.objects.filter(
        course=course
    ).count()

    # Calculate correct answers
    grade = 0

    for item in submissions:

        if item.choice.is_correct:
            grade += 1

    # Send required context to template
    context = {
        "course": course,
        "selected_ids": selected_ids,
        "grade": grade,
        "possible": possible,
        "submission": submission,
        "submissions": submissions,
    }

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        context
    )
