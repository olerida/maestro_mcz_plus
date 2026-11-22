# Revisión para Marketplace y criterios Bronce

Revisión local basada en la documentación oficial consultada el 22 de noviembre de 2026. Esta integración personalizada no tiene una clasificación Bronce oficial; las reglas de calidad corresponden a Home Assistant Core. No se ha publicado ni enviado ninguna solicitud.

## Marketplace

- Estructura: `app/` debe ser la raíz del futuro repositorio, con una única integración en `custom_components/maestro_mcz_plus`, `hacs.json`, README e icono local.
- Manifest: incluye dominio, versión, documentación, incidencias y responsable propuestos; estas URL y el responsable solo son verificables cuando exista el repositorio correspondiente. La categoría es `climate.thermostats_heating`.
- Preparado el flujo `.github/workflows/validate.yml` para ejecutar hassfest y HACS sin omitir comprobaciones. No se ha ejecutado en GitHub: su éxito está pendiente, y no debe afirmarse hasta comprobarlo.
- Para el catálogo público aún faltan un repositorio público no archivado, descripción, temas, incidencias habilitadas, ambas validaciones aprobadas y una versión completa publicada en GitHub. El ZIP local no es una release de GitHub. La inclusión en el catálogo requiere una solicitud posterior que no se ha realizado.
- Verificar derechos y atribuciones de todo código o material de terceros y el uso de la marca antes de distribuir. El README indica que reúne trabajo de otras integraciones, pero no identifica aquí sus licencias de origen.
- Comprobar en una instalación real la compatibilidad con la versión de Maestro MCZ que se vaya a recomendar; se usan estructuras y métodos internos de esa integración, que pueden cambiar. En el Home Assistant accesible se ha identificado Maestro MCZ 1.7.0 y una estructura de coordinador compatible en principio; no se ha hecho una prueba funcional completa. Las escrituras en una estufa física siguen sin verificar.

## Criterios Bronce de Core

| Regla | Evaluación local |
| --- | --- |
| action-setup, docs-actions, docs-conditions, docs-triggers | No aplican: no se registran acciones, condiciones ni disparadores propios. |
| appropriate-polling | Reutiliza el coordinador de Maestro MCZ; no añade sondeo periódico propio. El intervalo efectivo depende de la integración de origen. |
| brands | Icono local para Marketplace. La regla de Core exige icono y logotipo en el repositorio de marcas; pendiente y fuera del alcance de esta revisión. |
| common-modules | Entidad común en `entity.py`; utiliza coordinadores del origen y no define uno propio. |
| config-flow | Configuración por interfaz y opciones; selección de cuenta existente y advertencia de controles. |
| config-flow-test-coverage | Las pruebas locales ejecutadas cubren el 100 % de líneas de `config_flow.py`; no equivale por sí solo a probar todos los escenarios posibles. |
| dependency-transparency | Depende de otra integración personalizada, no de un paquete declarado directamente. Falta evaluar si esta arquitectura y sus dependencias serían aceptables para Core. |
| docs-high-level-description, docs-installation-instructions, docs-removal-instructions | Cubiertas en README para instalación manual, requisitos, configuración y retirada. La instalación mediante enlace dependerá de un repositorio real. |
| entity-event-setup | Las entidades usan `CoordinatorEntity`; el descubrimiento registra el listener en la configuración y lo elimina al descargar la entrada. Revisión de Core pendiente para confirmar la excepción por listener de plataforma. |
| entity-unique-id, has-entity-name | Los identificadores derivan del código de estufa y la clave; las entidades usan `has_entity_name`. La estabilidad depende del identificador de origen. |
| runtime-data | Datos de ejecución en `ConfigEntry.runtime_data`. |
| test-before-configure, test-before-setup | Se comprueba la disponibilidad del coordinador de origen; no se realiza una conexión independiente. Pendiente validar que esta comprobación sea suficiente para Core. |
| unique-config-entry | El identificador único es la entrada de origen y se impiden duplicados. |

Fuentes: [reglas de calidad](https://contributors.home-assistant.io/core/quality-scale/rules/), [integraciones personalizadas](https://contributors.home-assistant.io/marketplace/guides/integrations/), [catálogo](https://contributors.home-assistant.io/marketplace/guides/catalog/) y [validaciones](https://contributors.home-assistant.io/marketplace/reference/validation/).
