# 🤖 Agent Instructions - Code Quality Rules

> **Inspirado en los 7 consejos de Linus Torvalds para evitar código basura**

---

## 📚 Overview

Este directorio contiene las **7 reglas de calidad de código** que todos los agentes DEBEN seguir al escribir código en este repositorio.

Cada regla incluye:
- **Principio**: El consejo original de Linus Torvalds
- **Regla**: Instrucción accionable para agentes
- **Ejemplos**: Código ✅ (bien) / ❌ (mal)
- **Checklist**: Validaciones antes de commit

---

## 📋 Las 7 Reglas

| # | Regla | Principio |
|---|-------|-----------|
| 01 | [KISS Principle](./01-kiss-principle.md) | Hazlo simple o no lo hagas |
| 02 | [Delete Code Fearlessly](./02-delete-code-fearlessly.md) | Borra sin miedo el código inútil |
| 03 | [Code Not Comments](./03-code-not-comments.md) | Si necesitas comentarios, rehazlo |
| 04 | [Atomic Commits](./04-atomic-commits.md) | No mezcles refactors con arreglos |
| 05 | [Explain Simply](./05-explain-simply.md) | Si no lo puedes explicar rápido, está mal |
| 06 | [Make It Work First](./06-make-it-work-first.md) | Que funcione primero, optimiza después |
| 07 | [Small Commits](./07-small-commits.md) | Commits pequeños o estás ocultando algo |

---

## 🎯 Uso para Agentes

### Antes de Escribir Código

1. Leer las reglas aplicables al tipo de cambio
2. Tener las checklists presentes durante el desarrollo

### Antes de Commit

Para cada commit, validar:

```
□ Regla 01: ¿Es la solución más simple?
□ Regla 02: ¿Hay código muerto que eliminar?
□ Regla 03: ¿El código es autoexplicativo?
□ Regla 04: ¿El commit tiene un solo propósito?
□ Regla 05: ¿Puedes explicarlo en 30 segundos?
□ Regla 06: ¿Funciona primero (sin optimizar prematuro)?
□ Regla 07: ¿El commit es < 200 líneas?
```

### Durante Code Review

Usar las reglas como checklist de review:
- ¿Viola alguna regla?
- ¿Se puede mejorar según alguna regla?

---

## 🚨 Violaciones

Si un agente detecta una violación de alguna regla:

1. **Identificar** la regla violada
2. **Explicar** por qué es una violación
3. **Sugerir** la corrección
4. **No aprobar** hasta que se corrija

---

## 📖 Referencias

- [Linus Torvalds - Git Commit Messages](https://www.youtube.com/watch?v=O4X6iehLOa4)
- [Clean Code - Robert C. Martin](https://www.goodreads.com/book/show/3735293-clean-code)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

*Estas reglas son obligatorias para todos los agentes que escriben código en este repositorio.*
