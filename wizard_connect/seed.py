from .extensions import db
from .models import Post, User


TEST_USERS = (
    ("irsan", "Irsan Sefer", "is@wizard.de", "admin", "admin123", 70),
    ("flo", "Flo", "flo@wizard.de", "admin", "admin123", 85),
    ("patrick", "Patrick", "patrick@wizard.de", "user", "user123", 150),
    ("till", "Till", "till@wizard.de", "user", "user123", 90),
    ("lucas", "Lucas", "lucas@wizard.de", "user", "user123", 120),
)


def seed_test_data() -> None:
    if User.query.first() is not None:
        return
    users = {}
    for username, name, email, role, password, score in TEST_USERS:
        user = User(username=username, name=name, email=email, role=role, score=score)
        user.set_password(password)
        db.session.add(user)
        users[username] = user
    db.session.flush()
    db.session.add(
        Post(
            title="Willkommen",
            category="General",
            content="Willkommen bei Wizard-KI-Connect!",
            author=users["irsan"],
        )
    )
    db.session.commit()
