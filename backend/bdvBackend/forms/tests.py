import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, created_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("forms:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No forms are available.")
        self.assertQuerySetEqual(response.context["recent_question_list"], [])

    def test_no_options(self):
        '''
        If a question has no options, do not display it
        '''
        create_question(question_text='No options', days=0)
        response = self.client.get(reverse('forms:index'))
        self.assertContains(response, 'No forms are available.')
        self.assertQuerySetEqual(response.context["recent_question_list"], [])

    def test_past_question(self):
        """
        Questions with a created_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("forms:index"))
        self.assertQuerySetEqual(
            response.context["recent_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a created_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("forms:index"))
        self.assertContains(response, "No forms are available.")
        self.assertQuerySetEqual(response.context["recent_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("forms:index"))
        self.assertQuerySetEqual(
            response.context["recent_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("forms:index"))
        self.assertQuerySetEqual(
            response.context["recent_question_list"],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a created_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("forms:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a created_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("forms:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionModelTests(TestCase):
    def test_created_recently_future(self):
        time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(created_date=time)
        self.assertIs(future_question.created_recently(), False)
    def created_recently_older_1(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(created_date=time)
        self.assertIs(old_question.created_recently(), False)
    def created_recently_within_1(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(created_date=time)
        self.assertIs(recent_question.created_recently(), True)
