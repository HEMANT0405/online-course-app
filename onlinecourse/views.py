from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Question, Choice, Submission


def submit(request):
    if request.method == "POST":

        for question in Question.objects.all():

            selected_choice_id = request.POST.get(
                "question_" + str(question.id)
            )

            if selected_choice_id:
                choice = get_object_or_404(
                    Choice,
                    id=selected_choice_id
                )

                Submission.objects.create(
                    user=request.user,
                    question=question,
                    choice=choice
                )

        return show_exam_result(request)

    return HttpResponse("Invalid request")


def show_exam_result(request):
    user = request.user

    submissions = Submission.objects.filter(
        user=user
    ).select_related("question", "choice")

    total_questions = Question.objects.count()

    correct_answers = 0

    for submission in submissions:
        if submission.choice.is_correct:
            correct_answers += 1

    if total_questions > 0:
        score = (correct_answers / total_questions) * 100
    else:
        score = 0

    context = {
        "submissions": submissions,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score": score
    }

    return render(
        request,
        "onlinecourse/exam_result.html",
        context
    )
