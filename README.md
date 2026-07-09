# IA para Negocios y Autónomos

Sitio web de nicho sobre inteligencia artificial aplicada a empresas y autónomos, en español. Orientado a monetización con **Google AdSense** y **afiliación SaaS**.

## Estructura del proyecto

```
ia-para-negocios/
├── index.html                    # Home page
├── css/
│   └── styles.css                # Sistema de diseño completo
├── categorias/
│   ├── chatgpt-empresas.html     # ChatGPT para Empresas (13 artículos)
│   ├── automatizacion-ia.html    # Automatización con IA (12 artículos)
│   ├── herramientas-ia.html      # Herramientas de IA (12 artículos)
│   ├── ia-marketing.html         # IA para Marketing (12 artículos)
│   ├── ia-por-sector.html        # IA por Sector (12 artículos)
│   ├── productividad-ia.html     # Productividad con IA (12 artículos)
│   ├── ia-ecommerce.html         # IA para eCommerce (12 artículos)
│   └── legal-privacidad-ia.html  # Legal y Privacidad IA (12 artículos)
└── articulos/
    ├── como-usar-chatgpt-empresa.html
    ├── mejores-herramientas-ia-2025.html
    ├── automatizacion-ia-pequenas-empresas.html
    ├── ia-estrategia-marketing-digital.html
    └── ... (100 artículos planificados)
```

## Despliegue

### GitHub Pages (recomendado para empezar)

1. Ve a **Settings → Pages** en el repositorio de GitHub.
2. En *Source*, selecciona la rama `main` y la carpeta `/ (root)`.
3. Haz clic en **Save**. Tu sitio estará en `https://<usuario>.github.io/<repo>/` en ~2 minutos.

### Dominio personalizado con GitHub Pages

1. Compra tu dominio (ej. `iaparanegocios.es`) en cualquier registrador.
2. En GitHub Pages Settings, introduce tu dominio en *Custom domain*.
3. En tu registrador, añade estos registros DNS:
   ```
   A     @    185.199.108.153
   A     @    185.199.109.153
   A     @    185.199.110.153
   A     @    185.199.111.153
   CNAME www  <usuario>.github.io
   ```
4. Marca **Enforce HTTPS** una vez que el DNS propague (~24h).

### Netlify (alternativa con formularios y redirects)

1. Conecta el repositorio en [netlify.com](https://netlify.com).
2. Build command: *(dejar vacío, es HTML estático)*
3. Publish directory: `/` (raíz)
4. Haz clic en **Deploy site**.

### Vercel

```bash
npm i -g vercel
vercel --prod
```

## Google AdSense

1. Solicita una cuenta en [adsense.google.com](https://adsense.google.com).
2. Cuando te aprueben, añade el tag de AdSense en el `<head>` de todas las páginas:
   ```html
   <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX" crossorigin="anonymous"></script>
   ```
3. Los marcadores `<div class="ad-slot ad-slot-banner">` y `<div class="ad-slot ad-slot-rectangle">` en el HTML indican dónde colocar los bloques de anuncio. Sustitúyelos por el código de unidad de anuncio de AdSense.

### Ubicaciones de anuncios actuales

| Ubicación | Formato | Clase CSS |
|-----------|---------|-----------|
| Debajo del hero (home) | Banner 728×90 | `ad-slot-banner` |
| Sidebar artículos | Rectangle 300×250 | `ad-slot-rectangle` |
| Sidebar categorías | Rectangle 300×250 | `ad-slot-rectangle` |

## Afiliación SaaS

Los artículos están diseñados para enlazar de forma natural a herramientas SaaS con programas de afiliados. Herramientas con programas de afiliados recomendadas:

| Herramienta | Programa | Comisión | Estado |
|-------------|----------|----------|--------|
| ChatGPT / OpenAI | No tiene (usa alternativas) | — | — |
| ElevenLabs | [try.elevenlabs.io](https://try.elevenlabs.io/v6gvji9kdntz) | — | **Activo** (enlace en eleven-labs-voz-ia.html) |
| Grammarly | Impact.com | $0.20 por registro + comisión | Solicitud enviada, pendiente de aprobación |
| Gamma | PartnerStack | — | Solicitud enviada, pendiente de aprobación |
| Make.com | [make.com/affiliate](https://make.com/en/affiliate) | 35% recurrente | **Recomendado siguiente**: mejor encaje temático, revisión manual, sin requisito mínimo de tráfico conocido |
| Jasper AI | [jasper.ai/legal/affiliates](https://jasper.ai) | 25% recurrente (30% si superas 100 leads convertidos en 12 meses) | Pendiente de solicitar; revisión manual más estricta con la calidad/audiencia del contenido |
| Perplexity | partners.dub.co/perplexity | Sin confirmar | Estado dudoso: el antiguo programa de referidos de Comet terminó el 6-nov-2025; confirmar en navegador si el enlace sigue activo antes de solicitar |
| Copy.ai | [copy.ai/affiliate](https://copy.ai) | 45% recurrente (verificar tras la reestructuración de precios 2025) | No solicitado |
| Notion | [notion.so/affiliates](https://notion.so) | 50% primer año | No solicitado |
| Zapier | [zapier.com/referral](https://zapier.com) | 15% recurrente | No solicitado |
| Semrush | [semrush.com/partner](https://semrush.com) | $200 por venta | No solicitado |
| HubSpot | [hubspot.com/partners](https://hubspot.com) | 30% recurrente | No solicitado |

## SEO

Cada página incluye:
- `<title>` y `<meta name="description">` únicos
- `<link rel="canonical">` para evitar contenido duplicado
- Schema markup JSON-LD (`WebSite`, `CollectionPage`, `Article`)
- Estructura de encabezados semántica (h1 → h2 → h3)

Para un sitemap XML automático, considera usar [xml-sitemaps.com](https://xml-sitemaps.com) o añadir un script de generación.

## Desarrollo local

No se necesita servidor ni build process. Abre directamente en el navegador:

```bash
# Con Python (cualquier versión)
python3 -m http.server 8080
# Luego ve a http://localhost:8080

# Con Node.js
npx serve .
# Luego ve a http://localhost:3000
```

## Plan de contenido

El sitio está planificado para **100 artículos** divididos en 8 categorías:

| Categoría | Artículos | Estado |
|-----------|-----------|--------|
| ChatGPT para Empresas | 13 | Página creada |
| Automatización con IA | 12 | Página creada |
| Herramientas de IA | 12 | Página creada |
| IA para Marketing | 12 | Página creada |
| IA por Sector | 12 | Página creada |
| Productividad con IA | 12 | Página creada |
| IA para eCommerce | 12 | Página creada |
| Legal y Privacidad IA | 12 | Página creada |
| **Total** | **97** | |

## Tecnologías

- HTML5 semántico
- CSS3 con variables custom (sin frameworks externos)
- JavaScript vanilla (solo para menú móvil y barra de progreso de lectura)
- Sin dependencias npm ni proceso de build
- Compatible con todos los navegadores modernos

## Licencia

Contenido © 2025 IA para Negocios. Todos los derechos reservados.
