from django.test import TestCase
from django.urls import reverse
from .models import Wager, WagerOption, WagerUser, Bet
from .forms import wager_bet_form

# Create your tests here.

class HomeViewTest(TestCase):
    def test_view_no_wagers(self):
        response = self.client.get(reverse("bet:home"))
        self.assertContains(response, "No wagers!")
        self.assertQuerySetEqual(response.context['all_wagers'], [])

    def test_view_one_wager(self):
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        response = self.client.get(reverse("bet:home"))
        self.assertQuerySetEqual(response.context['all_wagers'], [wager], ordered=False)

    def test_view_two_wagers(self):
        wager1 = Wager.objects.create(name="test wager1", description="test description1", pot=500)
        wager2 = Wager.objects.create(name="test wager2", description="test description2", pot=500)
        response = self.client.get(reverse("bet:home"))
        self.assertQuerySetEqual(response.context['all_wagers'], [wager1, wager2], ordered=False)

class WagerBetFormtest(TestCase):
    def test_valid_form(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        form = wager_bet_form(wager, user)(data={"selected_option": wager_option.id, "bet_value": 500})
        self.assertTrue(form.is_valid())

    def test_invalid_option(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        form = wager_bet_form(wager, user)(data={"selected_option": 9999, "bet_value": 500})
        self.assertFalse(form.is_valid())

    def test_ascii_bet_value(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        form = wager_bet_form(wager, user)(data={"selected_option": wager_option.id, "bet_value": "asd"})
        self.assertFalse(form.is_valid())

    def test_negative_bet_value(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        form = wager_bet_form(wager, user)(data={"selected_option": wager_option.id, "bet_value": -500})
        self.assertFalse(form.is_valid())

    def test_no_option(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        form = wager_bet_form(wager, user)(data={"bet_value": 500})
        self.assertFalse(form.is_valid())

    def test_no_bet_value(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        form = wager_bet_form(wager, user)(data={"selected_option": wager_option.id})
        self.assertFalse(form.is_valid())

class WagerViewTest(TestCase):
    def test_view_wager(self):
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        response = self.client.get(reverse("bet:wager", args=(wager.id,)))
        self.assertContains(response, "Make bet")

    def test_wager_view_contains_option(self):
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        response = self.client.get(reverse("bet:wager", args=(wager.id,)))
        self.assertContains(response, wager_option.name)

    def test_wager_view_with_bet_already_placed(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        Bet.objects.create(user=user, option=wager_option, wager=wager, value=500)
        response = self.client.get(reverse("bet:wager", args=(wager.id,)))
        self.assertContains(response, "Already made a bet")

class PlaceBetTest(TestCase):
    def test_create_valid_bet(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        response = self.client.post(
            reverse("bet:place_bet", args=(wager.id,)),
            {
                "selected_option": wager_option.id,
                "bet_value": 500,
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 1500)
        self.assertEqual(response.status_code, 302)

    def test_place_bet_with_negative_value(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        response = self.client.post(
            reverse("bet:place_bet", args=(wager.id,)),
            {
                "option": wager_option.id,
                "bet_value": -20,
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 2000)
        self.assertContains(response, "Bet must be non-negative")

    def test_place_bet_larger_than_balance(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        response = self.client.post(
            reverse("bet:place_bet", args=(wager.id,)),
            {
                "option": wager_option.id,
                "bet_value": 3000,
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 2000)
        self.assertContains(response, "User does not have enough points for this bet")

    def test_place_bet_when_user_has_already_placed_bet(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        Bet.objects.create(user=user, option=wager_option, wager=wager, value=500)
        response = self.client.post(
            reverse("bet:place_bet", args=(wager.id,)),
            {
                "option": wager_option.id,
                "bet_value": 500,
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 2000)
        self.assertEqual(response.status_code, 403)

        