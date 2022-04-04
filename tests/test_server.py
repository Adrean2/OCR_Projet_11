import server
from server import loadClubs, loadCompetitions
from datetime import datetime


CORRECT_CLUB = "Iron Temple"
WRONG_CLUB = "Bronze Temple"
CORRECT_COMPETITION = "Spring Festival"
WRONG_COMPETITION = "Winter Festival"
POINTS_COST_PER_PLACE = 3

COMPETITION = {
        "name": "test_competition",
        "date": "2022-05-03 10:00:00",
        "numberOfPlaces": "34"
        }
CLUB = {
        "name": "test_club",
        "email": "test@test.club",
        "points": "37"
    }
LOW_POINTS_CLUB = {
        "name": "Low_points_club",
        "email": "test_low_points@test.club",
        "points": "3"
    }
LOW_PLACES_COMPETITION ={
        "name": "low_places_competition",
        "date": "2023-03-03 10:00:00",
        "numberOfPlaces": "2"

}
OLD_COMPETITION = {
        "name": "old_competition",
        "date": "2010-03-03 10:00:00",
        "numberOfPlaces": "34"
    }


def test_clubs():
    expected = [
        {
        "name": "Simply Lift",
        "email": "john@simplylift.co",
        "points": "13"
    },
    {
        "name": "Iron Temple",
        "email": "admin@irontemple.com",
        "points": "4"
    },
    {   "name": "She Lifts",
        "email": "kate@shelifts.co.uk",
        "points": "12"
    }
    ]
    assert loadClubs() == expected


def test_competitions():
    expected = [
        {
            "name": "Spring Festival",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        }
    ]
    assert loadCompetitions() == expected


def test_index(client):
    request = client.get("/")
    assert request.status_code == 200


def test_logout(client):
    request = client.get("/logout")
    # 302 = redirection réussi
    assert request.status_code == 302


def test_club_points(client):
    request = client.get("/")
    assert b"Simply Lift: 13 points" in request.data
    assert b"Iron Temple: 4 points" in request.data
    assert b"She Lifts: 12 points" in request.data


class TestSummary:

    def test_show_summary_with_correct_email(self, client):
        request = client.post("/showSummary", data={"email": "john@simplylift.co"})
        assert request.status_code == 200
        assert b"Summary | GUDLFT Registration" in request.data

    def test_show_summary_with_wrong_email(self,client):
        request = client.post("/showSummary",data={"email":"bad@email"})
        assert request.status_code == 200
        assert b"Vous devez utiliser une adresse email valide." in request.data

    def test_show_summary_with_empty_email(self,client):
        request = client.post("/showSummary",data={"email":""})
        assert request.status_code == 200
        assert b"Vous devez inscrire une adresse email" in request.data


class TestBooking:

    def setup_method(self):
        server.competitions.append(COMPETITION)
        server.competitions.append(LOW_PLACES_COMPETITION)
        server.competitions.append(OLD_COMPETITION)
        server.clubs.append(CLUB)
        server.clubs.append(LOW_POINTS_CLUB)

    def test_booking_with_correct_competition_and_club(self, client):
        request = client.get(f"/book/{CORRECT_COMPETITION}/Iron Temple")
        assert request.status_code == 200
        assert f"{CORRECT_COMPETITION}" in request.data.decode()

    def test_booking_with_wrong_competition_correct_club(self,client):
        request = client.get(f"/book/{WRONG_COMPETITION}/{CORRECT_CLUB}")
        assert request.status_code == 200
        assert b"Renseignez une competition valide" in request.data

    def test_booking_with_correct_competition_wrong_club(self,client):
        request = client.get(f"/book/{CORRECT_COMPETITION}/{WRONG_CLUB}")
        assert request.status_code == 200
        assert b"Renseignez un club valide" in request.data

    def test_booking_removes_stock(self,client):
        booking_places = 3
        expected = int(COMPETITION["numberOfPlaces"]) - booking_places
        request = client.post(f"/purchasePlaces",
                                data={"competition":COMPETITION["name"],
                                "club":CLUB["name"],
                                "places":booking_places})
        assert request.status_code == 200
        assert int(COMPETITION["numberOfPlaces"]) == expected

    def test_booking_removes_club_points(self,client):
        booking_places = 3
        expected = int(CLUB["points"]) - booking_places*POINTS_COST_PER_PLACE
        request = client.post(f"/purchasePlaces",
                                data={"competition":COMPETITION["name"],
                                "club":CLUB["name"],
                                "places":booking_places})
        assert request.status_code == 200
        assert int(CLUB["points"]) == expected

    def test_booking_more_than_12(self,client):
        CLUB["points"] = "36"
        request = client.post(f"/purchasePlaces",
                            data={"competition":COMPETITION["name"],
                            "club": CLUB["name"],
                            "places": 12
                            })
        assert request.status_code == 200
        assert b"Vous ne pouvez pas reserver + de 12 places" in request.data

    def test_booking_more_than_points_available(self,client):
        request = client.post(f"/purchasePlaces",
                            data={"competition":COMPETITION["name"],
                            "club": LOW_POINTS_CLUB["name"],
                            "places": 2
                            })
        assert request.status_code == 200
        assert b"Il vous faut plus de points pour reserver" in request.data

    def test_booking_past_competitions(self, client):
        request = client.post(f"/purchasePlaces",
                              data={"competition": OLD_COMPETITION["name"],
                                    "club": CLUB["name"],
                                    "places": 2
                                    })
        assert request.status_code == 200
        assert b"Cette competition est fini, vous ne pouvez plus reserver"

    def test_booking_empty_places(self,client):
        request = client.post(f"/purchasePlaces",
                              data={"competition": OLD_COMPETITION["name"],
                                    "club": CLUB["name"],
                                    "places": ""})
        assert request.status_code == 200
        assert b"Ecrivez une valeur" in request.data

    def test_booking_negative_places(self,client):
        request = client.post(f"/purchasePlaces",
                              data={"competition": OLD_COMPETITION["name"],
                                    "club": CLUB["name"],
                                    "places": -1})
        assert request.status_code == 200
        assert b"Utilisez un chiffre positif !" in request.data

    def test_booking_out_of_stock_places(self,client):
        request = client.post(f"/purchasePlaces",
                              data={"competition": LOW_PLACES_COMPETITION["name"],
                                    "club": CLUB["name"],
                                    "places": 3})
        assert request.status_code == 200
        assert b"Veuillez reserver dans la limite disponible" in request.data
