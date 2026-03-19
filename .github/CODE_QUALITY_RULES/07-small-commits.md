# 07 - Small Commits

> **Consejo de Linus:** "Commits pequeños o estás ocultando algo"

---

## 🎯 Principio

Commits pequeños son:
- Más fáciles de revisar
- Más fáciles de revertir
- Más fáciles de entender
- Menos riesgo de conflictos
- Mejor historial de git

**Regla general:** Commits > 200 líneas merecen revisión. ¿Por qué tan grandes?

---

## 📋 Regla para Agentes

**Commits pequeños o estás ocultando algo.**

Los agentes DEBEN:
1. Hacer commits frecuentes y pequeños
2. Commits > 200 líneas requieren justificación
3. Dividir cambios grandes en commits lógicos
4. Recordar: commits pequeños = reviews fáciles = menos bugs
5. Commitear cada cambio coherente, no cada archivo

---

## ✅ Ejemplos

### ✅ Commits Pequeños (BIEN)

```bash
# Commit enfocado: solo modelo
git commit -m "feat: add User model with authentication fields"
# 3 archivos, 80 líneas

# Commit enfocado: solo validación
git commit -m "feat: add email validation to User model"
# 2 archivos, 40 líneas

# Commit enfocado: solo tests
git commit -m "test: add unit tests for User validation"
# 1 archivo, 120 líneas
```

```bash
# Refactor en pasos pequeños
git commit -m "refactor: extract validation logic to separate function"
# 2 archivos, 50 líneas

git commit -m "refactor: rename variables for clarity"
# 3 archivos, 30 líneas

git commit -m "refactor: simplify conditional logic"
# 2 archivos, 40 líneas
```

### ❌ Commits Gigantes (MAL)

```bash
# ❌ MAL: Demasiados cambios
git commit -m "feat: complete user module"
# 47 archivos, 2500 líneas
# ¿Qué estoy revisando? ¿En qué orden?
```

```bash
# ❌ MAL: "Todo junto" antes del PR
git add .
git commit -m "WIP: lots of changes"
# 89 archivos, 5000 líneas
# Imposible de revisar, imposible de revertir
```

```bash
# ❌ MAL: Cambios no relacionados juntos
git commit -m "fix: fix login bug and update README and refactor utils"
# 15 archivos, 400 líneas
# Deberían ser 3 commits separados
```

---

## 🔍 Checklist Antes de Commit

Antes de hacer commit, el agente DEBE validar:

- [ ] ¿El commit tiene menos de 200 líneas?
- [ ] ¿Puedes explicar el commit en 1 frase?
- [ ] ¿El commit es fácil de revertir?
- [ ] ¿Un reviewer puede entenderlo en 5 minutos?
- [ ] ¿Estás commitando cambios no relacionados juntos? → SEPARAR

**Si respondes NO a alguna, DIVIDE en commits más pequeños.**

---

## 📊 Guía de Tamaño de Commits

| Tamaño | Líneas | ¿Aceptable? | Notas |
|--------|--------|-------------|-------|
| 🟢 Pequeño | < 50 | ✅ Ideal | Fácil de revisar |
| 🟡 Mediano | 50-200 | ✅ Aceptable | Justificar si > 100 |
| 🟠 Grande | 200-500 | ⚠️ Revisar | ¿Por qué tan grande? |
| 🔴 Enorme | > 500 | ❌ Dividir | Imposible de revisar |

---

## 🛠️ Técnicas para Commits Pequeños

### 1. Commit por Archivo vs Commit por Cambio

```bash
# ❌ MAL: Commit por archivo (mezcla cambios)
git add user.py auth.py utils.py README.md
git commit -m "changes"

# ✅ BIEN: Commit por cambio lógico
git add user.py auth.py
git commit -m "feat: add user authentication"

git add utils.py
git commit -m "refactor: extract validation helper"

git add README.md
git commit -m "docs: add authentication examples"
```

### 2. Usar `git add -p`

```bash
# Revisar cambios por hunk
git add -p

# Permite commitear partes de un archivo
# hunk 1: fix bug → commit
# hunk 2: refactor → otro commit
```

### 3. Commits de Refactor en Pasos

```bash
# En lugar de un commit gigante de refactor:
# Paso 1: Mover archivos
git mv old/ new/
git commit -m "refactor: move files to new structure"

# Paso 2: Renombrar
git commit -m "refactor: rename User class to AuthenticatedUser"

# Paso 3: Extraer lógica
git commit -m "refactor: extract validation to separate module"

# Paso 4: Simplificar
git commit -m "refactor: simplify conditional logic"
```

---

## 🚨 Anti-patrones a Evitar

| Anti-patrón | Por qué está mal | Alternativa |
|-------------|------------------|-------------|
| "Commit al final del día" | Acumula cambios | Commits frecuentes |
| "Todo funciona, hago commit" | 1000+ líneas | Commits por feature |
| Merge conflicts gigantes | Horas de resolución | Commits pequeños = conflicts pequeños |
| "Arreglé 5 bugs juntos" | No se puede revertir 1 | 5 commits separados |

---

## 💡 Frase para Recordar

> "Si tu commit es más grande que 200 líneas, ¿qué estás ocultando?"

---

## 📚 Referencias

- [Small Commits - Atlassian](https://www.atlassian.com/git/tutorials/saving-changes)
- [How to Write Better Git Commits](https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/)

---

*Regla inspirada en los consejos de Linus Torvalds para evitar código basura*
