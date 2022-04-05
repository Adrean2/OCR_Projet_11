import server
from server import loadClubs,loadCompetitions

def test_clubs():
    expected = [
        {
        "name":"Simply Lift",
        "email":"john@simplylift.co",
        "points":"13"
    },
    {
        "name":"Iron Temple",
        "email": "admin@irontemple.com",
        "points":"4"
    },
    {   "name":"She Lifts",
        "email": "kate@shelifts.co.uk",
        "points":"12"
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
