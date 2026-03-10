import datetime

from django.test import TestCase, SimpleTestCase, TransactionTestCase, LiveServerTestCase
from django.urls import reverse, resolve
from django.utils import timezone
from urllib.request import urlopen

from .models import Question, Choice
from .views import vote


class PollsSimpleTests(SimpleTestCase):
    def test_vote_url_resolves_to_vote_view(self):
        # build the vote url for a sample question id
        url = reverse("polls:vote", args=[123])

        # check which view this url points to
        match = resolve(url)

        self.assertEqual(url, "/polls/123/vote/")
        self.assertEqual(match.func, vote)


class PollsVoteTests(TestCase):
    def make_question(self):
        # make a past question so it works in the app
        return Question.objects.create(
            question_text="Favourite language?",
            pub_date=timezone.now() - datetime.timedelta(days=1)
        )

    def test_vote_increments_selected_choice_and_redirects(self):
        question = self.make_question()

        # make choices for this question
        choice1 = Choice.objects.create(question=question, choice_text="Python", votes=0)
        Choice.objects.create(question=question, choice_text="Java", votes=0)

        # send post request like the form does
        response = self.client.post(
            reverse("polls:vote", args=[question.id]),
            {"choice": choice1.id}
        )

        # reload from db to get updated votes
        choice1.refresh_from_db()

        self.assertEqual(choice1.votes, 1)
        self.assertRedirects(response, reverse("polls:results", args=[question.id]))

    def test_vote_without_selecting_choice_shows_error_message(self):
        question = self.make_question()

        Choice.objects.create(question=question, choice_text="Python", votes=0)

        # post with no choice selected
        response = self.client.post(reverse("polls:vote", args=[question.id]), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You didn't select a choice.")


class PollsTransactionTests(TransactionTestCase):
    def test_deleting_question_deletes_related_choices(self):
        question = Question.objects.create(
            question_text="Delete test",
            pub_date=timezone.now()
        )

        # these choices belong to the question
        Choice.objects.create(question=question, choice_text="A", votes=0)
        Choice.objects.create(question=question, choice_text="B", votes=0)

        self.assertEqual(Choice.objects.count(), 2)

        # deleting the parent should delete the children too
        question.delete()

        self.assertEqual(Choice.objects.count(), 0)


class PollsLiveServerTests(LiveServerTestCase):
    def test_index_page_displays_question_text(self):
        Question.objects.create(
            question_text="Live server poll question",
            pub_date=timezone.now() - datetime.timedelta(hours=1)
        )

        # open the real test server in the browser request
        response = urlopen(self.live_server_url + reverse("polls:index"))
        html = response.read().decode("utf-8")

        self.assertIn("Live server poll question", html)