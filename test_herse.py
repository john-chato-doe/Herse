import time
import unittest

from herse import Herse, HerseBaissee


class TestHerse(unittest.TestCase):
    def test_laisse_passer_jusqua_la_capacite(self):
        herse = Herse(capacite=3, debit=1)
        self.assertTrue(all(herse.laisser_passer() for _ in range(3)))
        self.assertFalse(herse.laisser_passer())

    def test_les_jetons_reviennent(self):
        herse = Herse(capacite=1, debit=20)
        self.assertTrue(herse.laisser_passer())
        self.assertFalse(herse.laisser_passer())
        time.sleep(0.1)
        self.assertTrue(herse.laisser_passer())

    def test_decorateur(self):
        herse = Herse(capacite=1, debit=0.001)

        @herse.garder
        def entrer():
            return "ok"

        self.assertEqual(entrer(), "ok")
        with self.assertRaises(HerseBaissee):
            entrer()

    def test_parametres_invalides(self):
        with self.assertRaises(ValueError):
            Herse(capacite=0, debit=1)
        with self.assertRaises(ValueError):
            Herse(capacite=2, debit=1).laisser_passer(cout=3)


if __name__ == "__main__":
    unittest.main()
