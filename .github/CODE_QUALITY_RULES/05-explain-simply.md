# 05 - Explain Simply

> **Consejo de Linus:** "Si no lo puedes explicar rápido, está mal"

---

## 🎯 Principio

La complejidad no es inteligencia. Si no puedes explicar el código en 1 minuto, está demasiado complejo.

El código simple:
- Se explica en segundos
- Se entiende al leerlo
- Se mantiene fácilmente
- Se debuggea rápido

---

## 📋 Regla para Agentes

**Si no puedes explicar el código en 1 minuto, está demasiado complejo.**

Los agentes DEBEN:
1. Validar que la lógica sea explicable rápidamente
2. Recordar: complejidad ≠ inteligencia
3. Simplificar antes de commit
4. Usar la prueba del "compañero junior"

---

## ✅ Ejemplos

### ✅ Código Explicable (BIEN)

```python
# Se explica en 5 segundos:
# "Filtra usuarios activos y ordena por nombre"
def get_active_users_sorted(users: list[User]) -> list[User]:
    return sorted(
        [u for u in users if u.is_active],
        key=lambda u: u.name
    )
```

```python
# Se explica en 10 segundos:
# "Calcula el total con IVA y descuento si es premium"
def calculate_order_total(order: Order, user: User) -> float:
    subtotal = sum(item.price * item.quantity for item in order.items)

    if user.is_premium:
        subtotal *= 0.9  # 10% descuento

    return subtotal * 1.21  # +21% IVA
```

### ❌ Código Inexplicable (MAL)

```python
# ¿Qué hace esto? Intenta explicarlo en 1 minuto...
def process(data, flags=None):
    result = []
    for i, (x, y) in enumerate(zip(data[::2], data[1::2])):
        if flags and i < len(flags) and flags[i]:
            result.append((x + y) * (1 if i % 2 == 0 else -1))
        else:
            result.append(x * y if x > y else y * x)
    return result
```

```python
# Demasiada lógica anidada para explicar rápido
def validate_user(user: User) -> bool:
    if user.is_active:
        if user.has_subscription:
            if user.subscription_end_date > datetime.now():
                if user.payment_status == 'paid':
                    if user.email_verified:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

# ✅ Debería ser:
def validate_user(user: User) -> bool:
    return (
        user.is_active
        and user.has_subscription
        and user.subscription_end_date > datetime.now()
        and user.payment_status == 'paid'
        and user.email_verified
    )
```

---

## 🔍 Checklist Antes de Commit

Antes de hacer commit, el agente DEBE validar:

- [ ] ¿Puedes explicar qué hace el código en 30 segundos?
- [ ] ¿Un compañero junior lo entendería?
- [ ] ¿La función tiene menos de 20 líneas?
- [ ] ¿Tiene menos de 3 niveles de anidación?
- [ ] ¿Los nombres de variables/funciones son claros?

**Si respondes NO a alguna, SIMPLIFICA antes de commit.**

---

## 🧪 La Prueba del "Compañero Junior"

Antes de commit, intenta explicar tu código a un compañero (real o imaginario):

```
"Esta función [NOMBRE] hace [PROPÓSITO]
tomando [INPUTS] y retornando [OUTPUTS].
Usa [ALGORITMO/ENFOQUE] porque [RAZÓN SIMPLE]."
```

**Si tardas más de 1 minuto o usas palabras como "básicamente", "es complicado", "tienes que entender que"... → REFACTORIZA**

---

## 🚨 Anti-patrones a Evitar

| Anti-patrón | Por qué está mal | Alternativa |
|-------------|------------------|-------------|
| Funciones de 50+ líneas | Demasiado que explicar | Dividir en funciones más pequeñas |
| 5+ niveles de anidación | Imposible de seguir | Early returns, guard clauses |
| Variables `x`, `temp`, `data` | No explican nada | Nombres descriptivos |
| Lógica booleana compleja | Difícil de razonar | Extraer a funciones con nombre |
| Patrones "clever" | Solo tú lo entiendes | Código aburrido y claro |

---

## 💡 Frase para Recordar

> "Si no puedes explicárselo a un junior, no lo entiendes tú tampoco."

---

## 📚 Referencias

- [Feynman Technique for Code](https://www.goodreads.com/book/show/3735293-clean-code)
- [Rubber Duck Debugging](https://en.wikipedia.org/wiki/Rubber_duck_debugging)

---

*Regla inspirada en los consejos de Linus Torvalds para evitar código basura*
