# Guemara en Español (plugin.video.guemara)

🎥 Estudio del Talmud en Español directamente desde Kodi.

## Descripción
Este addon permite acceder a lecciones en vídeo del Talmud divididas por órdenes (Sedarim) y tratados (Masejtot), en español. Los videos son cargados dinámicamente desde archivos `.txt` y estructurados con JSON.

## Estructura
El contenido está organizado de acuerdo a los seis órdenes del Talmud:
- Seder Zeraim
- Seder Moed
- Seder Nashim
- Seder Nezikin
- Seder Kodashim
- Seder Taharot

## Funcionalidades
- 📂 Navegación jerárquica por Seder y Masejta
- 🔍 Búsqueda de lecciones
- 📺 Soporte de historial de visualización
- 📄 Estructura dinámica cargada desde archivos `.txt`

## Solución de Problemas

**Problemas de Reproducción (Ej: Vídeos no inician)**

Si algunos vídeos no comienzan a reproducirse o fallan al iniciar, podrías necesitar ajustar una configuración avanzada de Kodi para desactivar HTTP/2. Esto a veces resuelve problemas de conexión con ciertos servidores de streaming.

**Cómo aplicar la solución:**

1.  **Localiza tu carpeta `userdata` de Kodi.** La ubicación exacta varía según tu sistema operativo. Puedes encontrar las rutas comunes buscando "userdata folder" en la Wiki oficial de Kodi.
2.  Dentro de la carpeta `userdata`, busca un archivo llamado `advancedsettings.xml`.
3.  **Si el archivo NO existe:** Créalo usando un editor de texto plano (como Notepad, TextEdit, etc.).
    **Si el archivo SÍ existe:** Ábrelo con un editor de texto plano.
4.  Asegúrate de que el archivo contenga el siguiente bloque de `<network>`. Si estás editando un archivo existente, añade la sección `<network>` con cuidado dentro de las etiquetas principales `<advancedsettings>`, asegurándote de no eliminar otras configuraciones que ya pudieras tener:

    ```xml
    <advancedsettings>
      <network>
        <disablehttp2>true</disablehttp2>
      </network>
      </advancedsettings>
    ```

5.  **Guarda** el archivo `advancedsettings.xml`.
6.  **Reinicia Kodi** completamente para que los cambios surtan efecto.

Después de reiniciar, intenta reproducir el vídeo problemático de nuevo.

## Instalación
1. Clona o descarga este repositorio en tu carpeta de addons de Kodi.
2. Asegúrate de tener activado el soporte para addons no oficiales en Kodi.
3. Abre Kodi y accede a `Add-ons > Mis Add-ons > Video > Guemara en Español`.

## Contribuir
¡Pull requests y sugerencias son bienvenidas!