# 04 - Atomic Commits

> **Consejo de Linus:** "No mezcles refactors con arreglos"

---

## 🎯 Principio

Un commit = un propósito. Los commits atómicos son:
- Más fáciles de revisar
- Más fáciles de revertir
- Más fáciles de entender
- Mejor historial de git

---

## 📋 Regla para Agentes

**Un commit = un propósito. Refactor ≠ Bugfix ≠ Feature.**

Los agentes DEBEN:
1. Separar cambios en commits atómicos
2. Nunca mezclar refactors con bugfixes
3. Nunca mezclar features con refactorings
4. Hacer commits por tipo de cambio, no por archivo
5. Escribir mensajes de commit que expliquen el propósito único

---

## ✅ Ejemplos

### ✅ Commits Atómicos (BIEN)

```bash
# Commit 1: Solo refactor
git commit -m "refactor: extract user validation logic to separate function"

# Commit 2: Solo bugfix
git commit -m "fix: handle null pointer in payment processor"

# Commit 3: Solo feature
git commit -m "feat: add discount code support to checkout"
```

```bash
# Commit 1: Solo cambio de formato/naming
git commit -m "style: rename variables for clarity"

# Commit 2: Solo lógica de negocio
git commit -m "feat: implement tiered pricing calculation"
```

### ❌ Commits Mezclados (MAL)

```bash
# ❌ MAL: Demasiados cambios en un commit
git commit -m "fix: fix payment bug and refactor user service and add logging"
# ¿Qué estoy revisando? ¿El fix? ¿El refactor? ¿Los logs?
```

```bash
# ❌ MAL: No se puede revertir selectivamente
git commit -m "feat: add new checkout flow
- Refactored entire payment module
- Fixed bug in discount calculation
- Added new checkout endpoint
- Updated tests
- Changed variable names"
# Si el checkout tiene un bug, no puedo revertir sin perder el fix
```

---

## 🔍 Checklist Antes de Commit

Antes de hacer commit, el agente DEBE validar:

- [ ] ¿Este commit tiene un solo propósito?
- [ ] ¿Podrías revertir este commit sin romper otros cambios?
- [ ] ¿El mensaje de commit describe un solo cambio?
- [ ] ¿Estás mezclando refactor con feature/fix? → SEPARAR
- [ ] ¿El commit es más pequeño que 200 líneas?

**Si respondes NO a alguna, SEPARA en commits más pequeños.**

---

## 📝 Tipos de Commits (Conventional Commits)

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `feat` | Nueva funcionalidad | `feat: add user export to CSV` |
| `fix` | Bugfix | `fix: prevent null pointer in auth` |
| `refactor` | Refactor sin cambio de comportamiento | `refactor: extract validation logic` |
| `style` | Formato, sin cambio de lógica | `style: format imports, fix spacing` |
| `docs` | Documentación | `docs: add API examples to README` |
| `test` | Tests | `test: add edge cases for discount` |
| `chore` | Mantenimiento | `chore: update dependencies` |

---

## 🚨 Anti-patrones a Evitar

| Anti-patrón | Por qué está mal | Alternativa |
|-------------|------------------|-------------|
| "Arreglé esto mientras refactorizaba" | No se puede revertir selectivamente | Hacer 2 commits separados |
| Commit "WIP" con 10 cambios | Historial sucio | Commits atómicos frecuentes |
| "Todo en uno" antes del PR | Review imposible | Separar por tipo de cambio |
| Renombrar + cambiar lógica | Git pierde el rastro | Commit 1: renombrar, Commit 2: lógica |

---

## 💡 Frase para Recordar

> "Si no puedes explicar qué hace un commit en una frase, tiene demasiados cambios."

---

## 📚 Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
- [Atomic Commits - GitLab](https://docs.gitlab.com/ee/development/code_review.html#atomic-commits)

---

*Regla inspirada en los consejos de Linus Torvalds para evitar código basura*
