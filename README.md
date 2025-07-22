<h1 align="center">Filtro de Citas 🏥</h1>
<p align="center">
  <img src="https://img.shields.io/badge/status-stable-brightgreen?style=plastic">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=plastic">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=plastic&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=plastic&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Uvicorn-121212?style=plastic&logo=uvicorn&logoColor=white" alt="Uvicorn">
  <img src="https://img.shields.io/badge/Pydantic-0A1128?style=plastic&logo=python&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=plastic&logo=pytest&logoColor=white" alt="Pytest">
</p>


Proyecto que implementa un componente para **Filtrar Citas** dentro de una pipeline ETL, para la coordinación y contacto de pacientes en sistemas hospitalarios de Latinoamérica.

El sistema permite aplicar reglas negocio sobre citas médicas provenientes de APIs hospitalarias, generando un subconjunto de citas a contactar, de acuerdo a condiciones personalizadas para diferentes institución.

> 💡 Pensado para ser **modular, desacoplado, auditable y fácilmente integrable**, facilitando la evolución de cada módulo y el monitoreo de resultados por equipos técnicos y no técnicos.



## 🏗️ Arquitectura General

> ![Arquitectura General](/imgs/arquitectura_general.png)
*Representación el flujo ETL completo, desde la consulta a las APIs hospitalarias hasta el contacto con pacientes, resalta los **supuestos** clave de integración y filtrado.*



> ![Zoom Filtrar Citas](/imgs/zoom_filtrar_citas.gif)
*Detalle de la arquitectura interna del proceso `Filtrar citas`*



## ⚙️ Características técnicas principales

- **Entrada:** Lista de citas en formato JSON, simulada o proveniente de integración con API hospitalaria.
- **Reglas:** Definidas externamente (por Customer Success), cargadas desde archivos `.json` con Domain-Specific Language (DSL).
- **Motor de reglas:** Evalúa condiciones lógicas parametrizadas sin codificar reglas como `if` rígidos.
- **Salida:** Subconjunto de citas a contactar, en formato estructurado para el siguiente módulo.
- **Integración:** Puede exponerse vía FastAPI como un microservicio.
- **100% Anotaciones de tipo en Python** para máxima claridad y mantenibilidad.
- **Empaquetado con Docker** para portabilidad y facilidad de despliegue.



## 🐳 Ejecuta el sistema con Docker

1. **Clona este repositorio:**

```bash
git clone https://github.com/Seba3995/filtro_citas.git
cd filtro_citas
````

2. **Levanta todo el entorno con Docker:**

```bash
docker-compose up --build
```

> 🔗 Documentación interactiva de FastAPI 
👉 [http://localhost:8000/docs](http://localhost:8000/docs)


## 📁 Estructura del Proyecto

```bash
filtro_citas/
├── app/
│   ├── __init__.py                    # Inicializa el módulo Python para la app
│   ├── filter_engine.py               # Motor de reglas: lógica central para evaluar y filtrar citas
│   ├── main.py                        # Entrada FastAPI: expone la API para filtrar citas
│   ├── models.py                      # Modelos Pydantic para validación y documentación de datos
│   ├── rules/
│   │   └── rules.json                 # Definición de reglas (mini-DSL) modificables sin cambiar el código
│   ├── sample_data/
│   │   └── citas_ejemplo.json         # Datos de ejemplo para pruebas funcionales/manuales
│   └── tests/
│       └── test_filter_engine.py      # Pruebas unitarias del motor de filtrado (automatización y cobertura)
│
├── imgs/
│   ├── arquitectura_general.jpg       # Diagrama general del flujo ETL y contexto de integración
│   └── zoom_filtrar_citas.jpg         # Detalle de la arquitectura interna del componente Filtrar Citas
│
├── .gitignore                         
├── docker-compose.yml                 # Orquestador para levantar servicios de la solución
├── Dockerfile                         # Imagen Docker del microservicio para despliegue portátil
├── LICENSE                            
├── README.md                          
└── requirements.txt                   # Dependencias Python necesarias para reproducir el entorno
```
