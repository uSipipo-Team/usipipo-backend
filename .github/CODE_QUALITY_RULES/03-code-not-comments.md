# 03 - Code Not Comments

> **Consejo de Linus:** "Si necesitas comentarios, rehazlo"

---

## 🎯 Principio

El código debe ser autoexplicativo. Los comentarios son un parche para código confuso.

**Excepción válida:** Comentarios que explican el **POR QUÉ** (decisiones de negocio, restricciones externas), no el **QUÉ** (lo que el código ya dice).

---

## 📋 Regla para Agentes

**El código debe ser autoexplicativo. Si requiere comentarios, REFACTORIZALO.**

Los agentes DEBEN:
1. Refactorizar antes de comentar
2. Usar nombres de variables/funciones descriptivos
3. Solo permitir comentarios de "por qué" (decisiones de negocio)
4. Eliminar comentarios que explican "qué" hace el código
5. Considerar el comentario como señal de código confuso

---

## ✅ Ejemplos

### ✅ Código Autoexplicativo (BIEN)

```python
# Nombres descriptivos que no necesitan comentarios
def calculate_final_price(base_price: float, discount_percentage: float) -> float:
    return base_price * (1 - discount_percentage / 100)

def is_user_eligible_for_discount(user: User) -> bool:
    return user.is_premium and user.has_active_subscription
```

```python
# Comentario válido: explica el POR QUÉ (decisión de negocio)
def process_refund(order_id: str) -> None:
    # Stripe requiere esperar 24h para refunds de nuevos usuarios
    # para prevenir fraudes con tarjetas robadas
    if is_new_user(order_id):
        schedule_refund_for_later(order_id, hours=24)
    else:
        process_immediate_refund(order_id)
```

### ❌ Comentarios que Explican el Qué (MAL)

```python
# ❌ El código ya dice esto
def calc(p, d):  # Calcula el precio con descuento
    return p * (1 - d)  # Multiplica precio por 1 menos descuento
```

```python
# ❌ Comentario que explica lo obvio
def get_active_users():
    # Filtra solo los usuarios activos
    return [u for u in users if u.active]  # Retorna lista de activos
```

```python
# ❌ Código confuso + comentario parche
def proc(data):
    # Itera sobre los elementos y suma el valor si es positivo
    result = 0
    for x in data:  # Para cada elemento
        if x > 0:  # Si es mayor que 0
            result += x  # Suma al resultado
    return result

# ✅ Debería ser:
def sum_positive_values(values: list[int]) -> int:
    return sum(v for v in values if v > 0)
```

---

## 🔍 Checklist Antes de Commit

Antes de hacer commit, el agente DEBE validar:

- [ ] ¿Los comentarios explican "qué" hace el código? → ELIMINAR
- [ ] ¿Los nombres de variables/funciones son descriptivos?
- [ ] ¿El código es legible sin comentarios?
- [ ] ¿Los comentarios restantes explican solo "por qué" (decisiones)?
- [ ] ¿Hay código confuso que intentaste explicar con comentarios? → REFACTORIZAR

**Si encuentras comentarios de "qué", REFACTORIZA el código.**

---

## 📝 Tipos de Comentarios

| Tipo | ¿Válido? | Ejemplo |
|------|----------|---------|
| Explica qué hace el código | ❌ NO | `# Suma 1 al contador` |
| Explica por qué (decisión) | ✅ SÍ | `# Espera 24h por política anti-fraude` |
| TODO/FIXME | ✅ SÍ | `# TODO: migrar a nueva API en v2` |
| Documentación pública (docstrings) | ✅ SÍ | `"""Calcula el IVA según la región."""` |
| Código comentado | ❌ NO | Eliminar, para eso está git |
| Comentarios de debugging | ❌ NO | `# print para debug` → Eliminar |

---

## 🚨 Anti-patrones a Evitar

| Anti-patrón | Por qué está mal | Alternativa |
|-------------|------------------|-------------|
| Comentar cada línea | Ruido visual, código confuso | Nombres descriptivos |
| `# FIX ME` sin ticket | Se olvida fácilmente | Usar sistema de issues |
| Comentarios desactualizados | Mienten sobre el código | Actualizar o eliminar |
| Comentarios agresivos | `# ESTO ESTÁ ROTO` | Profesionalismo |

---

## 💡 Frase para Recordar

> "El código es leído más veces de las que es escrito. Haz que se lea bien."

---

## 📚 Referencias

- [Clean Code - Comments Chapter](https://www.goodreads.com/book/show/3735293-clean-code)
- [Linus Torvalds on Comments](https://www.youtube.com/watch?v=O4X6iehLOa4)

---

*Regla inspirada en los consejos de Linus Torvalds para evitar código basura*
