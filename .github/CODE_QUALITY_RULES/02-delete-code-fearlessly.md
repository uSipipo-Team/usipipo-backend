# 02 - Delete Code Fearlessly

> **Consejo de Linus:** "Borra sin miedo el código inútil"

---

## 🎯 Principio

El mejor código es el código que no existe. El código muerto:
- Aumenta la deuda técnica
- Confunde a los desarrolladores
- Requiere mantenimiento innecesario
- Aumenta el tiempo de build/test
- Oculta el código realmente importante

---

## 📋 Regla para Agentes

**El código muerto es deuda técnica. Identifícalo y ELIMÍNALO.**

Los agentes DEBEN:
1. Sugerir eliminar código no usado en cada refactor
2. Identificar funciones/métodos/clases sin referencias
3. Eliminar código comentado (para eso está git)
4. Preferir 100 líneas menos que 10 líneas más
5. No tener miedo de borrar código que costó esfuerzo

---

## ✅ Ejemplos

### ✅ Eliminar Código (BIEN)

```python
# ANTES: Código acumulado
def get_user(user_id: int) -> User:
    # old_code = get_user_legacy(user_id)  # TODO: remove
    # legacy fallback removed
    return user_repository.get_by_id(user_id)

# DESPUÉS: Código limpio
def get_user(user_id: int) -> User:
    return user_repository.get_by_id(user_id)
```

```python
# ANTES: Función que ya no se usa
def calculate_old_discount(price: float) -> float:
    # Esta función fue reemplazada por calculate_discount_v2
    pass

def calculate_discount_v2(price: float, discount: float) -> float:
    return price * (1 - discount)

# DESPUÉS: Eliminar lo que no se usa
def calculate_discount(price: float, discount: float) -> float:
    return price * (1 - discount)
```

### ❌ Acumular Código (MAL)

```python
# Código comentado que "quizás se use después"
def process_payment(amount: float):
    # old_method = legacy_process(amount)
    # if old_method:
    #     return old_method
    # TODO: revert if new method fails
    return new_process(amount)
```

```python
# Funciones deprecated que nadie usa pero todos temen borrar
def get_users(): ...           # nueva
def get_users_v2(): ...        # más nueva
def get_users_legacy(): ...    # vieja
def get_users_old(): ...       # muy vieja
def _get_users_internal(): ... # quién sabe
```

---

## 🔍 Checklist Antes de Commit

Antes de hacer commit, el agente DEBE validar:

- [ ] ¿Hay código comentado que pueda eliminarse?
- [ ] ¿Hay funciones/métodos sin referencias?
- [ ] ¿Hay imports que no se usan?
- [ ] ¿Hay variables declaradas y no usadas?
- [ ] ¿Hay código marcado como TODO/obsolete que ya no sirve?

**Si encuentras algo, ELIMÍNALO antes de commit.**

---

## 🛠️ Herramientas para Identificar Código Muerto

| Herramienta | Uso |
|-------------|-----|
| `ruff --select=F401,F841` | Imports y variables sin usar |
| `vulture` | Código muerto en Python |
| `deadcode` | Análisis estático de código no alcanzable |
| Git blame | Ver cuándo y por qué se agregó código |
| IDE warnings | La mayoría de IDEs detectan código no usado |

---

## 🚨 Anti-patrones a Evitar

| Anti-patrón | Por qué está mal | Alternativa |
|-------------|------------------|-------------|
| Comentar código "por si acaso" | Para eso está git | Borrar y hacer commit |
| Mantener funciones "deprecated" sin uso | Confunde y aumenta superficie | Eliminar después de migración |
| `if False:` blocks | Código muerto disfrazado | Eliminar directamente |
| imports comentados | Ruido visual | Eliminar |

---

## 💡 Frase para Recordar

> "Si el código es tan bueno que da miedo borrarlo, es tan malo que da miedo usarlo."

---

## 📚 Referencias

- [The Best Code is No Code](https://www.goodreads.com/quotes/6388-the-best-code-is-no-code-at-all)
- [Dead Code Detection - Wikipedia](https://en.wikipedia.org/wiki/Dead_code_elimination)

---

*Regla inspirada en los consejos de Linus Torvalds para evitar código basura*
