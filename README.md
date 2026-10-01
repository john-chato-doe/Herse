# herse

Un limiteur de débit minimaliste pour API Python.
Même principe que la herse d'un château fort : les visiteurs raisonnables passent, elle retombe sur les autres.

Projet perso en cours, pas encore prêt pour la prod.

## Utilisation

```python
from herse import Herse, HerseBaissee

herse = Herse(capacite=10, debit=2)

@herse.garder
def mon_endpoint():
    return "bienvenue"

try:
    mon_endpoint()
except HerseBaissee as e:
    print(f"Revenez dans {e.attente:.1f} s")
```

Ici, la herse laisse passer 10 appels d'affilée, puis 2 par seconde. Sous le capot, c'est un seau à jetons (*token bucket*) : chaque appel consomme un jeton, et les jetons se régénèrent à vitesse constante. Le tout est protégé par un verrou, donc utilisable depuis plusieurs threads.

## Démo

```bash
python herse.py
```

## Tests

```bash
python -m unittest
```

## À faire

- [ ] Une herse par adresse IP
- [ ] Un middleware pour Flask et FastAPI
- [ ] Arrêter de tout nommer d'après des châteaux (peu probable)
