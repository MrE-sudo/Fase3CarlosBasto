"""Punto de entrada: ventana de Login -> ventana de ingreso de afiliados."""

from affiliation_view import AffiliationWindow
from login_view import LoginWindow


def main() -> None:
    login = LoginWindow()
    login.mainloop()
    if login.authenticated:
        AffiliationWindow().mainloop()


if __name__ == "__main__":
    main()
