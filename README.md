<div style="text-align: center;">
  <img src="docs/images/KubeSightLogo.png" alt="KubeSight Logo" width="100"/> <h1>KubeSight</h1>
</div>


**KubeSight** es un visor de Kubernetes diseñado para ser amigable, intuitivo y extremadamente fácil de usar. Construido con **Python** y **Flet**, ofrece una interfaz moderna y reactiva para interactuar con tus clústeres sin la complejidad de las herramientas de línea de comandos tradicionales.

## 🚀 Características Principales

- **Interfaz Intuitiva**: Diseño limpio y organizado para facilitar la navegación por tus recursos de Kubernetes.
- **Visualización en Tiempo Real**: Observa el estado de tus Pods, Deployments y Servicios al instante.
- **Fácil de Usar**: Pensado para desarrolladores y operadores que buscan simplicidad sin perder potencia.
- **Multi-Plataforma**: Gracias a Flet, KubeSight corre nativamente en Windows, macOS y Linux.

## 🛠️ Tecnologías

- **Lenguaje**: Python 3.11+
- **UI Framework**: [Flet](https://flet.dev/) (Flutter para Python)
- **K8s Client**: Kubernetes Python Client

## 📦 Instalación y Uso

### Requisitos Previos
- Python 3.11 o superior.
- Acceso a un clúster de Kubernetes (configurado en `~/.kube/config`).

### Pasos

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/tu-usuario/kubesight.git
    cd kubesight
    ```

2.  **Configurar el entorno virtual**:
    ```powershell
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**:
# KubeSight 🔭

**KubeSight** es un visor de Kubernetes diseñado para ser amigable, intuitivo y extremadamente fácil de usar. Construido con **Python** y **Flet**, ofrece una interfaz moderna y reactiva para interactuar con tus clústeres sin la complejidad de las herramientas de línea de comandos tradicionales.

## 🚀 Características Principales

- **Interfaz Intuitiva**: Diseño limpio y organizado para facilitar la navegación por tus recursos de Kubernetes.
- **Visualización en Tiempo Real**: Observa el estado de tus Pods, Deployments y Servicios al instante.
- **Fácil de Usar**: Pensado para desarrolladores y operadores que buscan simplicidad sin perder potencia.
- **Multi-Plataforma**: Gracias a Flet, KubeSight corre nativamente en Windows, macOS y Linux.

## 🛠️ Tecnologías

- **Lenguaje**: Python 3.11+
- **UI Framework**: [Flet](https://flet.dev/) (Flutter para Python)
- **K8s Client**: Kubernetes Python Client

## 📦 Instalación y Uso

### Requisitos Previos
- Python 3.11 o superior.
- Acceso a un clúster de Kubernetes (configurado en `~/.kube/config`).

### Pasos

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/tu-usuario/kubesight.git
    cd kubesight
    ```

2.  **Configurar el entorno virtual**:
    ```powershell
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**:
    ```bash
    python main.py
    ```

## 🗺️ Roadmap

- [x] Estructura base y Layout (Screaming Architecture).
- [ ] Gestión de Contextos (Clusters) y Namespaces.
- [ ] Explorador de Recursos:
    - [ ] Deployments.
    - [ ] CronJobs.
- [ ] Visualización de Logs en tiempo real.
- [ ] Gestión básica (Eliminar Pods, Reiniciar Deployments).

---
Hecho con ❤️ y Python.