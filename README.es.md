# ✈ Anchor Project - Air Travel ✈

El proyecto ancla de Ryan Day para explorar y demostrar técnicas avanzadas relacionadas con la ciencia de datos, las APIs y, cada vez más, los LLM.

A medida que construyo cosas aquí, escribo sobre ellas en mi boletín Tip Sheet. Suscríbete aquí para aprender cómo construyo estos componentes del proyecto ancla y cómo tú también puedes hacerlo: [subscribe to the Tip Sheet newsletter](https://tips.handsonapibook.com/).

Este proyecto ancla incluye algunas técnicas bastante avanzadas. Si deseas desarrollar conocimientos fundamentales sobre APIs FastAPI para IA y Ciencia de Datos en Python, ¡he escrito un libro que deberías leer! Descúbrelo en [Hands-on APIs for AI and Data Science: Python Development with FastAPI](https://handsonapibook.com).

[English readme](README.md)

---

## Temas principales

* Construcción y uso de APIs para aplicaciones de IA y ciencia de datos
* Uso de técnicas de programación asíncrona en Python para aumentar el rendimiento y la confiabilidad en todas las áreas

---

## Visión general de la arquitectura

![Anchor Project Architecture](images/anchor_project_big_picture.png)

Aquí se muestra una visión general de todos los componentes del proyecto ancla. Representan diferentes piezas de una solución empresarial construida alrededor de una fuente de datos y frameworks de Python.

El **Air Travel SDK** sirve como la capa central de integración, permitiendo que múltiples consumidores reutilicen la misma funcionalidad mientras se minimiza la duplicación de código.

---

## Tecnologías utilizadas

* Python - prácticamente todo el código está escrito en Python
* FastAPI - plataforma para el desarrollo de APIs
* PostgreSQL y Supabase - base de datos PostgreSQL en la nube
* FastMCP - framework para construir servidores y clientes MCP
* Typer - biblioteca para construir interfaces de línea de comandos (CLI)
* HTTPX - biblioteca asíncrona para llamadas a APIs
* Scikit-Learn - framework de Python para el entrenamiento de modelos de aprendizaje automático
* ONNX Runtime - framework abierto para alojar modelos de ML para inferencia
* Jupyter Notebooks - el mejor amigo de todo científico de datos

---

## Temas principales

# Componentes principales

## Air Travel CLI

Una interfaz de línea de comandos diseñada para desarrolladores, analistas y agentes de programación basados en IA.

La CLI proporciona una forma conveniente de buscar y recuperar información de vuelos directamente desde la terminal, aprovechando el SDK compartido que se encuentra debajo.

**Ruta en el repositorio:**

[cli/](./cli)

---

## Air Travel SDK

El paquete central de Python utilizado en todo el proyecto.

El SDK abstrae la implementación subyacente de la API y proporciona una interfaz coherente para múltiples consumidores.

Es utilizado por:

* La Air Travel CLI
* El servidor MCP
* Jupyter Notebooks
* Aplicaciones Streamlit y Gradio [FUTURE]

**Ruta en el repositorio:**

[sdk/](./sdk)

---

## Flights API

Una aplicación FastAPI que expone información de vuelos mediante endpoints REST.

La API actúa como la capa principal de acceso a los datos de vuelos y es consumida por el SDK.

**Ruta en el repositorio:**

[flights-api/](./flights-api)

---

## Air Travel Database

Un almacén de datos respaldado por PostgreSQL/Supabase que contiene datos operativos procesados de aerolíneas.

La Flights API recupera la información de vuelos desde esta capa de base de datos.

**Ruta en el repositorio:**

[postgres/](./postgres)

---

## Air Travel MCP Server

Un servidor MCP (Model Context Protocol) que permite a asistentes de IA y agentes de programación interactuar con el ecosistema Air Travel mediante herramientas estandarizadas.

En lugar de implementar su propia lógica de base de datos, el servidor MCP reutiliza el SDK compartido.

**Ruta en el repositorio:**

[mcp/](./mcp)

---

## Análisis ad hoc

Jupyter Notebooks utilizados para análisis exploratorio, experimentación y creación de prototipos.

Estos cuadernos demuestran cómo los analistas pueden trabajar con el mismo SDK utilizado en otras partes del proyecto.

Las actividades típicas incluyen:

* Exploración de datos
* Ingeniería de características
* Pruebas de hipótesis
* Experimentación

**Ruta en el repositorio:**

[llm/](./llm)

---

## Entrenamiento de modelos de ML e inferencia mediante API

Jupyter Notebooks que demuestran el entrenamiento de modelos de aprendizaje automático y la construcción de una API para inferencia.

El modelo entrenado en este ejemplo es bastante simple, así que no lo analices demasiado en detalle.

Sin embargo, el enfoque para entrenar modelos y ofrecer inferencia mediante una API constituye un marco sólido.

**Ruta en el repositorio:**

[ml-models/](./ml-models)

---

## Aplicaciones de datos [FUTURE]

Aplicaciones interactivas construidas con frameworks como Streamlit o Gradio.

Estas aplicaciones proporcionan experiencias para los usuarios finales mientras utilizan el SDK para recuperar datos.

Los posibles casos de uso incluyen:

* Aplicaciones de búsqueda de vuelos
* Paneles de control
* Demostraciones
* Experiencias asistidas por IA

**Ruta en el repositorio:**

[llm/](./llm)

---

# Fuente de datos

El proyecto utiliza datos operativos de aerolíneas disponibles públicamente del Bureau of Transportation Statistics (BTS) del Departamento de Transporte de los Estados Unidos.

Portal de datos BTS:

https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK&QO_fu146_anzr=b0-gvzr

---

# Otros componentes del Anchor Project

## data/

Conjuntos de datos de apoyo, recursos de ingestión y artefactos intermedios utilizados en todo el proyecto.

---

## inference-api/

Servicios relacionados con la inferencia de modelos de aprendizaje automático y la experimentación con despliegues.

---

## llm/

Experimentos relacionados con modelos de lenguaje de gran tamaño, ingeniería de prompts y flujos de trabajo de IA.

---

## ml-models/

Recursos para el entrenamiento, evaluación y experimentación con modelos de aprendizaje automático.

---

## postgres/

Infraestructura de base de datos, definiciones de esquemas y scripts de soporte.

---

# Primeros pasos

Clona el repositorio:

```
git clone https://github.com/Ryandaydev/anchor_project_air_travel.git
```

Explora uno de los principales puntos de entrada:

* `sdk/` para funcionalidades reutilizables del cliente
* `cli/` para flujos de trabajo desde la línea de comandos
* `flights-api/` para la implementación de la API REST
* `mcp/` para integraciones con agentes de IA

---

# Filosofía de diseño

El Anchor Project enfatiza varios principios arquitectónicos:

* **Un SDK, muchos consumidores** -- la funcionalidad compartida minimiza la duplicación de lógica.
* **Desarrollo centrado en APIs** -- los servicios se comunican mediante interfaces bien definidas.
* **Arquitectura preparada para IA** -- los servidores MCP y los flujos de trabajo con agentes se tratan como consumidores de primera clase.
* **Componentes componibles** -- las aplicaciones pueden evolucionar de forma independiente mientras comparten fundamentos comunes.
* **Transparencia educativa** -- el repositorio demuestra patrones prácticos para proyectos modernos de ingeniería de datos, APIs e IA.
