"""Entry point: Login window -> Affiliation data entry window."""

from affiliation_view import AffiliationWindow
from login_view import LoginWindow


def main() -> None:
    login = LoginWindow()
    login.mainloop()
    if login.authenticated:
        AffiliationWindow().mainloop()


if __name__ == "__main__":
    main()
