# 06 - Make It Work First

> **Consejo de Linus:** "Que funcione primero, optimiza después"

---

## 🎯 Principio

La optimización prematura es la raíz de todos los males. Primero haz que funcione, luego haz que sea rápido.

El orden correcto:
1. **Funciona** → El código hace lo correcto
2. **Correcto** → Maneja edge cases, errores
3. **Rápido** → Optimiza basado en profiling, no suposiciones

---

## 📋 Regla para Agentes

**Primero haz que funcione correctamente, luego optimiza.**

Los agentes DEBEN:
1. No optimizar prematuramente
2. Medir antes de optimizar (profilado > suposiciones)
3. Escribir código claro primero, rápido después
4. Solo optimizar cuellos de botella reales
5. Recordar: "Premature optimization is the root of all evil" - Knuth

---

## ✅ Ejemplos

### ✅ Enfoque Correcto (BIEN)

```python
# PASO 1: Que funcione (claro y simple)
def find_user_by_id(users: list[User], user_id: int) -> User | None:
    for user in users:
        if user.id == user_id:
            return user
    return None

# PASO 2: Medir (¿es realmente un cuello de botella?)
# profile muestra que esta función se llama 10000 veces/segundo

# PASO 3: Optimizar SOLO si es necesario
def find_user_by_id(users: list[User], user_id: int) -> User | None:
    # Pre-crear índice una vez, no en cada llamada
    return users_by_id.get(user_id)
```

```python
# PASO 1: Que funcione
def process_orders(orders: list[Order]) -> list[Result]:
    results = []
    for order in orders:
        result = process_single_order(order)
        results.append(result)
    return results

# PASO 2: Medir
# profile muestra que process_single_order es I/O bound

# PASO 3: Optimizar SOLO si es necesario
async def process_orders(orders: list[Order]) -> list[Result]:
    return await asyncio.gather(
        *[process_single_order(o) for o in orders]
    )
```

### ❌ Optimización Prematura (MAL)

```python
# ❌ Optimizando sin medir
def find_user_by_id(users: list[User], user_id: int) -> User | None:
    # ¿Por qué este cache complejo si se llama 5 veces al día?
    cache_key = f"user:{user_id}:{hash(users)}"
    if cache_key in _lru_cache:
        return _lru_cache[cache_key]
    # ... 50 líneas más de lógica de cache ...
```

```python
# ❌ Código "rápido" pero ilegible
def process(data):
    return [f(x) for x in data if p(x)] if len(data) > 1000 else list(map(f, filter(p, data)))
    # ¿Qué? ¿Por qué? ¿Realmente importa?
```

```python
# ❌ Optimización sin necesidad
def get_total(cart: Cart) -> float:
    # Usar numpy para sumar 3 items...
    import numpy as np
    return float(np.sum(np.array([item.price for item in cart.items])))
```

---

## 🔍 Checklist Antes de Commit

Antes de hacer commit, el agente DEBE validar:

- [ ] ¿El código funciona correctamente primero?
- [ ] ¿Tienes datos de profiling que justifiquen la optimización?
- [ ] ¿La optimización vale la pérdida de claridad?
- [ ] ¿Optimizaste un cuello de botella real o una suposición?
- [ ] ¿Los tests prueban que la optimización no rompe nada?

**Si respondes NO a alguna, PRIORIZA claridad sobre velocidad.**

---

## 📊 Cuándo Optimizar

| Situación | ¿Optimizar? | Por qué |
|-----------|-------------|---------|
| Código que se ejecuta 5 veces/día | ❌ NO | No impacta performance |
| Bucle en hot path (profiling) | ✅ SÍ | Cuello de botella real |
| Query N+1 detectado | ✅ SÍ | Problema conocido |
| "Por si acaso crece" | ❌ NO | YAGNI |
| Llamada a API externa | ✅ SÍ | I/O bound, impacta UX |
| Código de startup (one-time) | ❌ NO | No se nota |

---

## 🚨 Anti-patrones a Evitar

| Anti-patrón | Por qué está mal | Alternativa |
|-------------|------------------|-------------|
| Cache sin medir | Complejidad innecesaria | Medir primero |
| Micro-optimizaciones | 0.001ms no importa | Claridad > micro-opt |
| Algoritmos complejos "rápidos" | Nadie los mantiene | Simple y 10% más lento está bien |
| Premature parallelization | Race conditions | Funciona single-thread primero |

---

## 💡 Frase para Recordar

> "Premature optimization is the root of all evil" - Donald Knuth

> "Make it work, make it right, make it fast" - Kent Beck

---

## 📚 Referencias

- [Premature Optimization - Wikipedia](https://en.wikipedia.org/wiki/Program_optimization#When_to_optimize)
- [Clean Code - Performance Chapter](https://www.goodreads.com/book/show/3735293-clean-code)

---

*Regla inspirada en los consejos de Linus Torvalds para evitar código basura*
