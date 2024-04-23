from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question, Choice
from django.urls import reverse

# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_post(self):
        time = timezone.now() - datetime.timedelta(hours=4)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text, votes):
    return Choice.objects.create(question=question,choice_text=choice_text,votes=votes)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question_with_choice(self):
        question = create_question(question_text='Past question', days=-30)
        choice = create_choice(question, 'Past question choice', 0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question],)

    def test_future_question(self):
        create_question(question_text='Future question', days=5)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_and_past_question(self):
        past_question = create_question(question_text='Past question', days=-30)
        choice = create_choice(past_question, 'Past question choice', 0)
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [past_question],)

    def test_two_past_questions_with_choices(self):
        question_1 = create_question(question_text='Past question 1', days=-30)
        choice_1 = create_choice(question=question_1, choice_text='Question 1', votes=0)
        question_2 = create_question(question_text='Past question 2', days=-35)
        choice_2 = create_choice(question=question_2, choice_text='Question 2', votes=0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question_1, question_2],)

    def test_question_with_no_choices(self):
        question = create_question(question_text='Past question', days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerySetEqual(response.context['latest_question_list'], [])



class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text='Future question', days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_choice(self):
        past_question = create_question(question_text='Past question', days=-5)
        choice = create_choice(question=past_question, choice_text='Past question choice', votes=0)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        self.assertContains(response, choice.choice_text)


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text='Future question', days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text='Past question', days=-5)
        choice = create_choice(question=past_question, choice_text='Past question choice', votes=0)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        self.assertContains(response, choice.choice_text)