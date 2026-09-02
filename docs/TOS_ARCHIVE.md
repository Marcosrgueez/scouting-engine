> **Documento de metodología (archivado).** Registro de una investigación o decisión tomada durante el desarrollo. La validación de datos se hizo en un espacio de trabajo aparte (`data-experiment/`, no incluido en este repositorio); las rutas a `reports/`, `raw_data/` y `scripts/*.py` se refieren a ese espacio, no a este repo. Índice de docs: [`docs/README.md`](./README.md).

---

# Archivo de términos de servicio — Sportmonks y API-Football

Cierra el pendiente de la nota de `DECISIONS.md` del 2026-08-31: dejar
archivado el texto literal de los términos de uso de datos de ambos
proveedores, con fecha y URL, antes de la Fase 9.

> **Aviso.** Esto es una transcripción de los términos publicados y un
> análisis del texto, **no asesoramiento legal**. Ninguna de las dos
> páginas muestra fecha de "última actualización", así que conviene
> guardar además una captura de pantalla con la fecha visible del sistema.

---

## 1. Sportmonks

- **URL consultada:** https://www.sportmonks.com/terms-of-service/
- **Fecha de consulta:** 2026-08-31
- **Fecha de vigencia / última actualización:** no indicada en la página.
- **Método:** descarga directa de la página (acceso público, sin login).
  Transcripción literal verificada.

### Sección "Terms of use" (cita textual)

> When subscribing to Sportmonks.com, you agree to keep your contact
> details up-to-date.
>
> Your Sportmonks account is your own personal account and may not be
> shared with other developers.
>
> We are not responsible for how you choose to use the feed or for any
> potential consequences of using our data.
>
> We provide our data as is and make no guarantees of 100% accuracy
> because, in the end, the data is gathered by humans, which is always
> liable to various errors. However, you can expect that we will do our
> utmost best to retain our high quality to the best of our abilities.
>
> Coverage gaps may exist across certain leagues or competitions.
> Sportmonks does not guarantee the completeness, accuracy, or
> availability of data at all times and disclaims all liability for any
> resulting discrepancies or omissions.
>
> **Reselling Sportmonks' data without approval is not allowed. This means
> that you cannot directly sell the data we provide. We provide data for
> you to build apps, websites, games, and so on. If you sell our data
> directly, you are competing with Sportmonks with our own data. This is
> not allowed.**
>
> **In principle, if you use our data to create something based on our
> data and start earning money from your creation, everything is fine.**
> If you are unsure if your plan is according to these rules, don't be
> afraid to explain your plan and ask if this is allowed.
>
> Our data is exclusively available per domain, and the prices listed on
> our website apply. It's important to note that the pricing will be
> adjusted accordingly for multiple domains.

### Sección "Copyright" (cita textual)

> Our services and related applications are copyright-protected.
>
> **Reproduction, transferring, distribution, or storage of our services
> is strictly prohibited without the prior permission of Sportmonks.
> However, distribution, transfer, and storage of data provided by our
> services is allowed, but reselling the product is forbidden without our
> consent.**
>
> All the material on our website, including text, illustrations, audio
> and video clips, are protected by copyright. Usage of material from
> Sportmonks is strictly for personal and non-commercial use. Neither the
> website nor the materials may be modified, reproduced, distributed,
> publicly displayed, or otherwise used without prior consent from
> Sportmonks.

### Lectura de las cláusulas relevantes

| Tema | Qué dice |
|---|---|
| **Almacenar los datos** | Permitido explícitamente: *"distribution, transfer, and storage of data provided by our services is allowed"*. |
| **Reproducir "los servicios"** | Prohibido sin permiso — pero se refiere a la API/plataforma en sí (*"our services"*), no a los datos. El párrafo distingue las dos cosas en la misma frase. |
| **Producto derivado / comercial** | Permitido: *"if you use our data to create something based on our data and start earning money from your creation, everything is fine"*. |
| **Reventa de datos** | Prohibida sin consentimiento. Es la única restricción dura sobre los datos. |
| **"personal and non-commercial use" / "publicly displayed"** | Está en el párrafo sobre *"material on our website"* (textos, ilustraciones, clips de audio/vídeo del sitio de Sportmonks), no sobre los datos de la API. |
| **Por dominio** | Los datos y el precio son por dominio; varios dominios = varias suscripciones. Relevante al desplegar (Fase 9/10), no para un repo. |
| **Código / metodología** | No hay ninguna cláusula sobre publicar el código de integración, la metodología o el análisis. |

---

## 2. API-Football / API-Sports (api-sports.io)

- **URLs:** https://www.api-football.com/terms  y  https://api-sports.io/terms
- **Fecha de consulta:** 2026-08-31
- **Fecha de vigencia / última actualización:** no indicada.
- **Método:** ⚠️ **NO se pudo transcribir literalmente.** Ambas URLs
  devuelven **HTTP 403 (Cloudflare)** ante cualquier acceso automatizado —
  el mismo bloqueo ya documentado en la Fase 0
  (`README.md` de `data-experiment`, punto 7 de "Discrepancias"). El
  contenido de abajo procede de **extractos de motores de búsqueda**, no
  de la página verificada.

> **ACCIÓN PENDIENTE:** abrir ambas URLs en un navegador normal, copiar el
> texto literal de las secciones sobre licencia de datos / publicación /
> propiedad intelectual, y **pegarlo aquí sustituyendo este bloque**, con
> la fecha.

### Contenido según extractos de búsqueda (SIN verificar verbatim)

Sobre **licencia de publicación de datos**:

> API-Football does not provide a "license" for the use and publication of
> the data provided by their services on applications, websites or any
> other products made by the user. Any license or permission to publish
> the data must be requested by the user from the competent authorities.

Sobre **derechos de terceros (ligas / federaciones)**:

> Some sports data provided through the services may be subject to
> intellectual property rights or commercial restrictions imposed by
> third parties, including leagues, federations, or event organizers. It
> is the responsibility of the user to verify and obtain any necessary
> authorizations or licenses to use or publish such data in their own
> products or services.

Sobre **logos / imágenes de marca**:

> Some images or data may be subject to intellectual property or trademark
> rights held by third parties (including but not limited to leagues,
> federations, or clubs). The use of such content in applications,
> websites, or products may require additional authorization or licensing
> from the respective rights holders.

Sobre **usos que exigen licencias adicionales**:

> The use of their data for betting platforms, television broadcasting,
> fantasy sports platforms, or any mass media distribution may require
> additional licenses from the relevant rights holders.

Sobre **reventa y responsabilidad**:

> API-Sports prohibits reselling their data to third parties. The data is
> provided for you to create different projects such as applications,
> websites, fantasy soccer games etc. API-Football declines all
> responsibility in case of unauthorized or infringing use by the client.

Sobre **caché / almacenamiento local** (de la documentación, no de los
términos): API-Sports **recomienda** cachear en base de datos local los
datos de referencia (`/countries`, `/leagues`, equipos, standings) y las
imágenes (logos), servidos desde almacenamiento propio.

### Lectura de las cláusulas relevantes

| Tema | Qué dice (según extractos) |
|---|---|
| **Almacenar / cachear los datos** | Permitido y recomendado en la documentación; la reventa está prohibida. |
| **Publicar los datos** | **No otorgan licencia de publicación.** Publicar los datos exige que el usuario consiga la licencia de "las autoridades competentes" (ligas/federaciones). |
| **Propiedad intelectual de terceros** | Toda la carga de verificar y licenciar recae en el usuario; API-Football se exime de responsabilidad. |
| **Producto derivado** | Permitido crear apps/webs/juegos con los datos; no revenderlos. |
| **Código / metodología** | Los extractos no mencionan nada sobre publicar código de integración. **No verificado** — puede haber una cláusula no vista. |

---

## 3. ¿Tener `scouting-engine` público en GitHub entra en conflicto?

**Qué contiene el repo `scouting-engine`:** esquema PostgreSQL (SQLAlchemy),
ETL, análisis (percentiles, role scores, similarity, team style, tactical
fit), scripts, y documentación. **Qué NO contiene:** `raw_data/` (en
`.gitignore`), ningún dump ni volcado de la base de datos, ningún fichero
de datos de Sportmonks o API-Football. El historial está limpio de tokens
(verificado). Los docs sí incluyen ~una docena de cifras derivadas de
ejemplo (p. ej. "posesión Barça 68.4%", "Mbappé goles/90 percentil 98") en
tablas de validación.

### Sportmonks — **sin conflicto**

- El repo **no revende datos** (única restricción dura) ni **reproduce el
  servicio** de Sportmonks (lo prohibido en "Copyright" es reproducir
  *"our services"*, la API en sí; publicar código que *llama* a la API no
  es eso).
- Almacenar/transferir/distribuir los datos está **permitido
  explícitamente**, así que ni siquiera las cifras de ejemplo en los docs
  son un problema (no son reventa).
- Crear un producto derivado, incluso comercial, está **permitido
  explícitamente**.
- No hay ninguna cláusula sobre publicar el código, la metodología ni el
  análisis.
- La cláusula de *"personal and non-commercial use"* aplica al **material
  del sitio web** de Sportmonks (textos, ilustraciones, clips), no a los
  datos de la API ni a tu código.

### API-Football — **sin conflicto para un repo solo-código, pero con dos matices**

- Sus términos restringen publicar **los datos**, no el **código**. El
  repo no contiene datos de API-Football, y además API-Football **no está
  en el pipeline de producción** — se usó solo como contraste puntual en
  la Fase 0 (`DECISIONS.md`: *"queda como fuente de contraste / backup"*).
- La única presencia de API-Football en el repo es la columna
  `players.apifootball_player_id` (vacía) y referencias en `loaders/`. Cero
  datos.
- **Matiz 1:** no pude verificar sus términos verbatim (403). El análisis
  se apoya en extractos de búsqueda. **Podría existir una cláusula no
  vista** (p. ej. sobre ingeniería inversa o publicar detalles de los
  endpoints). Improbable, pero no descartado.
- **Matiz 2:** sus términos ponen toda la carga de licenciar la
  propiedad intelectual de terceros (LaLiga, etc.) en el usuario y se
  eximen de responsabilidad. Para un **repo de código** esto no aplica
  (no publica datos), pero **sí aplicará si la Fase 10 (frontend)
  muestra los datos en público** — eso es "publicar datos" y necesita su
  propia revisión.

### Respuesta

**Sí es seguro tener `scouting-engine` público hoy**, siempre que:

1. El repo siga sin contener `raw_data/`, dumps de BD, ni tokens
   (hoy se cumple).
2. Se complete el archivo con el **texto verbatim de API-Football**
   (abrir en navegador, pegar, fechar) y se confirme que no hay ninguna
   cláusula sobre publicar código de integración. *Hasta que eso se haga,
   queda un ~5% de incertidumbre no eliminable sobre API-Football.*

**Recomendaciones de cautela** (ninguna la exigen los términos, pero
reducen la superficie):

- Genericar las ~12 cifras concretas de jugador/equipo en los docs
  (usar valores inventados o "equipo A / jugador X"). Sportmonks permite
  distribuir datos, así que no es obligatorio; es higiene.
- Antes de la **Fase 9/10** (desplegar): revisar la cláusula "per domain"
  de Sportmonks (cada dominio desplegado = su suscripción) y hacer una
  revisión legal aparte para "mostrar datos en público", que es distinto
  de "almacenar para uso propio" y donde API-Football es explícitamente
  restrictivo (betting/broadcast/fantasy/"mass media distribution").
- Guardar capturas de pantalla de ambas páginas de términos con fecha
  visible, ya que ninguna lleva fecha de versión.

---

## Fuentes

- Sportmonks — Terms of Service: https://www.sportmonks.com/terms-of-service/
- API-Football — Terms of Service: https://www.api-football.com/terms (403 a acceso automatizado)
- API-Sports — Terms of Service: https://api-sports.io/terms (403 a acceso automatizado)
