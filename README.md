# Maestro MCZ Plus

Integración complementaria para Home Assistant que reúne los datos de funcionamiento y las recetas de tu estufa MCZ Maestro. Usa la cuenta y la conexión de [Maestro MCZ](https://github.com/Robbe-B/maestro_mcz).

## Instalación

1. Comprueba que **Maestro MCZ** ya detecta tu estufa en Home Assistant. Este paquete se ha probado con Home Assistant 2026.10.4 en un entorno aislado.
2. Descomprime el ZIP de `dist/` y copia `custom_components/maestro_mcz_plus` en la carpeta `custom_components` de tu configuración de Home Assistant. Después reinicia Home Assistant.
3. Abre **Ajustes → Dispositivos y servicios → Añadir integración → Maestro MCZ Plus** y selecciona tu cuenta Maestro MCZ.

Esta versión se entrega como paquete local. Cuando exista un repositorio público, podrás añadir su URL desde **Ajustes → Marketplace → Añadir desde enlace** en Home Assistant 2026.11 o posterior; en versiones anteriores compatibles, desde **HACS → Repositorios personalizados**. Selecciona la categoría **Integración**. [Requisitos de HACS](https://www.hacs.xyz/docs/publish/integration/).

Si ya usas **Maestro MCZ Extra Sensors** o **Maestro MCZ Recipes**, esta integración se añade con entidades nuevas. Revisa las automatizaciones y los paneles que usan las entidades antiguas antes de desactivar esas integraciones.

## Datos de funcionamiento

Según el modelo, podrás ver la temperatura de humos y de la placa, la fase de funcionamiento, la potencia activa, las RPM del extractor y del sinfín, y los tiempos de limpieza del brasero. Las entidades aparecen cuando la integración de origen recibe esos datos. La frecuencia depende del intervalo de Maestro MCZ y puede diferir de la app.

## Recetas

Los valores de **Activo**, **Pellet** y **Modo de adaptación** aparecen cuando la estufa los proporciona. La lectura funciona desde el primer inicio. Para habilitar cambios de combustión, un técnico puede activar los controles de receta en **Ajustes → Dispositivos y servicios → Maestro MCZ Plus → Configurar**. Los controles se ofrecen únicamente para combinaciones de modelo y parámetros reconocidas. Los ajustes numéricos avanzan de uno en uno dentro de los límites que proporciona el modelo.

Las órdenes se han probado con simulaciones. Verifica en la app o en la estufa cualquier cambio real. La integración comunica un error si el origen no devuelve los valores solicitados después de la orden. Al cambiar un ajuste de Activo, conserva el otro valor que proporcionó la última consulta. Evita cambiar Activo desde dos clientes a la vez.

Si recargas o actualizas Maestro MCZ, recarga también Maestro MCZ Plus para volver a conectar los sensores al origen.

## Vista previa en macOS

Craft Anything puede abrir `dist/Maestro MCZ Plus Preview.app` para mostrar las lecturas y recetas de una estufa simulada. La conexión con tu estufa se realiza desde Home Assistant mediante la integración descrita arriba.

Para generar el ZIP de instalación y compilar la vista previa en macOS, usa el entorno de pruebas de Python indicado en `requirements-test.txt` y ejecuta `./build.sh` con las herramientas de línea de comandos de Xcode instaladas.

## Código y licencia

Esta integración reúne el trabajo de `maestro_rtinfo` y `maestro_recipes`. [Mecánica de Maestro+ 5.8.0](MECHANICS.md) documenta los límites de receta, el formato de las órdenes y los datos de telemetría encontrados en la aplicación. La compatibilidad de otras estufas depende de los datos y metadatos disponibles en Maestro MCZ.

[Licencia MIT](LICENSE).

## Desinstalación

En **Ajustes → Dispositivos y servicios**, abre el menú de Maestro MCZ Plus y selecciona **Eliminar**. Si la instalaste manualmente, elimina además la carpeta `custom_components/maestro_mcz_plus` y reinicia Home Assistant. Si la instalaste con Marketplace o HACS, desinstálala desde allí y sigue la indicación de reinicio. La integración Maestro MCZ y sus dispositivos se conservan.

## Resolución de problemas

- **No aparece ninguna cuenta:** configura primero Maestro MCZ y comprueba que su cuenta esté cargada y que detecte al menos una estufa.
- **Faltan datos o controles:** dependen de los valores y metadatos que proporcionan la estufa y la integración de origen. Los controles requieren activar la opción avanzada y una conexión reconocida.
- **Datos no disponibles después de recargar Maestro MCZ:** recarga Maestro MCZ Plus desde su menú en Dispositivos y servicios.
- **Un cambio no se confirma:** comprueba el estado en la app oficial o en la estufa antes de volver a intentarlo. Las órdenes solo se han validado mediante simulación.
