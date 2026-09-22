# 🏪 STORE.md — Publicar Plataforma Total en TIENDAS REALES (todo U$S 0 posible)

**Hoy (Sept 2026) la app ya es instalable real** (instalador NSIS + auto-update desde GitHub Releases).
Esto la lleva a tiendas oficiales — en orden de esfuerzo/beneficio para vos (UY, sin empresa):

---

## 1️⃣ itch.io — GRATIS, hoy mismo (recomendada para arrancar)

Marketplace serio de apps/juegos indie. Sin verificación de identidad, sin cuota, acepta ejecutables tal cual.

1. Crear cuenta en <https://itch.io/register> (email, 2 min).
2. **New project** → Kind: `Executable` → subí `PlataformaTotal-Windows.zip` (o el `.exe`; Desktop avisa "subí el zip para que instale auto").
3. Precio: "No payments" + ✅ *Accept payments optionally* (donaciones) — o dejá apagado; lo importante es la **página pública**: otra vitrina con SEO real y descargas contadas.
4. Descripción: pegá el README corto; tags: `education`, `programming`, `offline`, `spanish`, `free`.
5. Web también: agregá el link <https://plataforma-total-web.pages.dev> como "website" del proyecto.

*Resultado: URL pública tipo `tuusuario.itch.io/plataforma-total` — eso ES estar en una app store.*

---

## 2️⃣ winget (Microsoft) — GRATIS, instalación de tienda sin tienda

Es el gestor de paquetes oficial de Windows 11: el usuario hace `winget install SoftEngAi.PlataformaTotal`
desde la terminal, con verificación de hash hecha por Microsoft. Es tan "oficial" como la Store para usuarios técnicos.

1. Los manifiestos **ya están redactados** en `manifests/winget/` de este repo (installer URL + SHA256 real de v4.5.0).
2. En una PC con Windows 11: `winget install wingetcreate` → `wingetcreate submit manifests\winget\` (te logueás con tu GitHub).
3. Microsoft valida hash + instalador silencioso (`/S`) y mergea el PR a `microsoft/winget-pkgs` (1-3 días la primera vez).

---

## 3️⃣ Microsoft Store — GRATIS para individuos desde Jun 2025 🎉

Sin cuota, sin tarjeta de crédito, en ~200 países (Uruguay incluido). **Comisión 0% si usás tu propio
sistema de cobro** (el nuestro es externo — LS/MP — así que 0 comisión). El paso que SOLO podés hacer vos:

1. Registrate en <https://partner.microsoft.com/dashboard> → cuenta **Individual** (gratis) con tu Microsoft account.
2. **Verificación de identidad**: cédula/pasaporte + selfie (15 min, es el "KYC" estándar, igual que MP/Prex).
3. **Empaquetado**: la Store pide formato **MSIX**. En tu PC Windows (una sola vez):
   ```powershell
   winget install "MSIX Packaging Tool"
   # abrir → elegir PlataformaTotal-Windows.exe → asistente → genera PlataformaTotal.msix
   # (alternativa moderna: tauri puede emitir MSIX nativamente — ver nota técnica abajo)
   ```
4. Partner Center → New app → reservá el nombre **"Plataforma Total"** (¡hacélo YA, es gratis y se agotan!)
   → subí el `.msix` → cuestionario de contenido (educación, sin anuncios) → certificación (2-7 días).

> Nota técnica (cuando recompilemos): el instalador actual es NSIS vía pipeline propio; el build con
> Tauri puede generar `.msix` firmado directamente agregando `"bundle": {"targets": ["msix"]}` —
> queda como mejora del workflow `build-exe.yml` cuando estés dentro de Partner Center.

---

## ⛔ Posponer hasta que haya ingresos

| Tienda | Costo | Por qué posponer |
|---|---|---|
| Google Play (PWA/TWA vía Bubblewrap) | U$S 25 única vez | La PWA instalable ya cubre celulares; la Store suma cuando haya usuarios pidiéndola |
| Apple App Store | U$S 99/año | Caro; y la PWA en iPhone ya funciona "Agregar a pantalla de inicio" |

---

## 🧾 Resumen de pasos que requieren TU acción (interactivos)

1. **itch.io**: registro (email) — 5 min — hoy querés.
2. **MS Store**: reservar nombre **ahora** (gratis) + verificación de identidad cuando puedas (<https://partner.microsoft.com>).
3. **Google Play**: solo cuando entre plata por MP/LS (U$S 25).

Yo preparo todo lo técnico por cada paso (página de itch con textos, submit de winget, MSIX/CI)
en cuanto me digas cuál arrancás.
