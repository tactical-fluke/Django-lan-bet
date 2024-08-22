from django.test import TestCase
from django.urls import reverse
from .models import Wager, WagerOption, WagerUser, Bet

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

class WagerViewTest(TestCase):
    def test_view_wager(self):
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        response = self.client.get(reverse("bet:wager", args=(wager.id,)))
        self.assertContains(response, wager.name)
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
                "option": wager_option.id,
                "bet_value": 500,
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 1500)
        self.assertEqual(response.status_code, 302)

    def test_create_bet_with_no_choice(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        response = self.client.post(
            reverse("bet:place_bet", args=(wager.id,)),
            {
                "bet_value": 500,
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 2000)
        self.assertContains(response, "Please select an option")

    def test_place_bet_with_no_value(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        response = self.client.post(
            reverse("bet:place_bet", args=(wager.id,)),
            {
                "option": wager_option.id,
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 2000)
        self.assertContains(response, "Please enter a valid bet!")

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
        self.assertContains(response, "Please enter a valid bet!")

    def test_place_bet_with_ascii_value(self):
        user = WagerUser.objects.create_user('user', email='email@email.com', password='password')
        self.assertTrue(self.client.login(username='user', password='password'))
        wager = Wager.objects.create(name="test wager", description="test description", pot=500)
        wager_option = WagerOption.objects.create(name="test option", description="a test option", wager=wager)
        response = self.client.post(
            reverse("bet:place_bet", args=(wager.id,)),
            {
                "option": wager_option.id,
                "bet_value": "bet",
            }
        )
        user.refresh_from_db()
        self.assertEqual(user.balance, 2000)
        self.assertContains(response, "Please enter a valid bet!")

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

        