# 01 - KISS Principle (Keep It Simple, Stupid)

> **Consejo de Linus:** "Hazlo simple o no lo hagas"

---

## 🎯 Principio

La simplicidad es la máxima sofisticación. El código simple es:
- Más fácil de entender
- Más fácil de mantener
- Menos propenso a bugs
- Más fácil de testear

---

## 📋 Regla para Agentes

**Si una solución tiene más de 3 niveles de anidación o requiere explicaciones complejas, RECONSIDERA el enfoque.**

Los agentes DEBEN:
1. Buscar siempre la solución más simple primero
2. Evitar sobre-ingeniería y patrones innecesarios
3. Preguntar: "¿Hay una forma más simple de hacer esto?"
4. Rechazar soluciones complejas cuando existe una simple

---

## ✅ Ejemplos

### ✅ Código Simple (BIEN)

```python
# Simple y directo
def get_active_users(users: list[User]) -> list[User]:
    return [u for u in users if u.is_active]
```

```python
# Una responsabilidad, una función
def calculate_discount(price: float, discount: float) -> float:
    return price * (1 - discount)
```

### ❌ Código Complejo (MAL)

```python
# Sobre-ingeniería innecesaria
def get_active_users(users: list[User]) -> list[User]:
    result = []
    for user in users:
        if user.is_active is True:
            if user.status != 'inactive':
                if not user.deleted:
                    result.append(user)
    return result
```

```python
# Patrón innecesario para algo simple
class DiscountCalculator:
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def calculate(self, price: float) -> float:
        return self.strategy.execute(price)

# Cuando podrías tener:
def calculate_discount(price: float, discount: float) -> float:
    return price * (1 - discount)
```

---

## 🔍 Checklist Antes de Commit

Antes de hacer commit, el agente DEBE validar:

- [ ] ¿Esta función tiene menos de 20 líneas?
- [ ] ¿El código tiene menos de 3 niveles de anidación?
- [ ] ¿Podrías explicar qué hace en 10 segundos?
- [ ] ¿Estás usando patrones de diseño realmente necesarios?
- [ ] ¿Hay una forma más simple de lograr lo mismo?

**Si respondes NO a alguna, REFACTORIZA antes de commit.**

---

## 🚨 Anti-patrones a Evitar

| Anti-patrón | Por qué está mal | Alternativa |
|-------------|------------------|-------------|
| AbstractFactory para 2 implementaciones | Sobre-ingeniería | Función simple o interfaz directa |
| 5+ niveles de if/for | Complejidad ciclomática alta | Early returns, guard clauses |
| Herencia múltiple profunda | Difícil de seguir | Composición sobre herencia |
| Configurar 10 parámetros opcionales | API confusa | Objeto de configuración o builder |

---

## 📚 Referencias

- [KISS Principle - Wikipedia](https://en.wikipedia.org/wiki/KISS_principle)
- [Simple Made Easy - Rich Hickey](https://www.infoq.com/presentations/Simple-Made-Easy/)

---

*Regla inspirada en los consejos de Linus Torvalds para evitar código basura*
