"""herse : un limiteur de débit minimaliste pour API Python.

Même principe que la herse d'un château fort : les visiteurs
raisonnables passent, elle retombe sur les autres.

Algorithme : seau à jetons (token bucket). Chaque appel consomme
un jeton, et les jetons se régénèrent à vitesse constante.
"""

import functools
import threading
import time

__all__ = ["Herse", "HerseBaissee"]
__version__ = "0.3.1"


class HerseBaissee(Exception):
    """Levée quand la herse est baissée (trop de requêtes)."""

    def __init__(self, attente: float) -> None:
        self.attente = attente
        super().__init__(f"Herse baissée, revenez dans {attente:.2f} s")


class Herse:
    """Laisse passer `capacite` appels d'affilée, puis `debit` appels par seconde."""

    def __init__(self, capacite: int, debit: float) -> None:
        if capacite <= 0 or debit <= 0:
            raise ValueError("capacite et debit doivent être positifs")
        self.capacite = capacite
        self.debit = debit
        self._jetons = float(capacite)
        self._dernier = time.monotonic()
        self._verrou = threading.Lock()

    def _remplir(self) -> None:
        maintenant = time.monotonic()
        ecoule = maintenant - self._dernier
        self._jetons = min(self.capacite, self._jetons + ecoule * self.debit)
        self._dernier = maintenant

    def laisser_passer(self, cout: float = 1.0) -> bool:
        """Consomme `cout` jetons si possible. Ne bloque jamais."""
        if cout > self.capacite:
            raise ValueError("cout supérieur à la capacité : personne ne passera jamais")
        with self._verrou:
            self._remplir()
            if self._jetons >= cout:
                self._jetons -= cout
                return True
            return False

    def attente(self, cout: float = 1.0) -> float:
        """Secondes à patienter avant que `cout` jetons soient disponibles."""
        with self._verrou:
            self._remplir()
            manque = cout - self._jetons
            return max(0.0, manque / self.debit)

    def garder(self, fonction):
        """Décorateur : lève HerseBaissee quand la fonction est trop sollicitée."""

        @functools.wraps(fonction)
        def gardee(*args, **kwargs):
            if not self.laisser_passer():
                raise HerseBaissee(self.attente())
            return fonction(*args, **kwargs)

        return gardee


if __name__ == "__main__":
    herse = Herse(capacite=3, debit=1)

    @herse.garder
    def pont_levis(visiteur: str) -> str:
        return f"Bienvenue, {visiteur}."

    for nom in ["Gauvain", "Perceval", "Lancelot", "Un barbare pressé"]:
        try:
            print(pont_levis(nom))
        except HerseBaissee as e:
            print(f"{nom} : {e}")
