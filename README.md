# Hipoteca Inversa

Aplicación de consola en Python para simular el cálculo de una **hipoteca inversa**, siguiendo principios de código limpio y arquitectura por capas (Modelo - Vista - Controlador).

## Estructura del proyecto

```
Hipoteca-inversa/
├── doc/
│   ├── EntrevistaJuanDavid.mp3      # Entrevista de levantamiento de requisitos
│   └── casos_de_prueba.xlsx         # Casos de prueba documentados
├── src/
│   ├── controller/
│   │   ├── __init__.py
│   │   └── hipoteca_controller.py   # Lógica compartida entre las vistas: parseo de datos y manejo de errores
│   ├── model/
│   │   ├── __init__.py
│   │   └── logica_hipoteca_inversa.py  # Lógica de negocio y cálculos financieros
│   └── view/
│       ├── __init__.py
│       ├── console.py               # Interfaz de consola (entrada/salida de datos)
│       └── interfaz_kivy.py         # Interfaz gráfica con Kivy (entrada/salida de datos)
├── tests/
│   ├── __init__.py
│   └── tests_hipoteca_inversa.py    # Pruebas unitarias de la lógica de negocio
├── .gitignore
├── LICENSE
├── requirements.txt                 # Dependencia opcional (Kivy) para la interfaz gráfica
└── README.md
```

### Descripción de la arquitectura

El proyecto sigue una separación de responsabilidades tipo **MVC**:

- **`model`**: contiene toda la lógica de cálculo de la hipoteca inversa (validaciones, fórmulas financieras, reglas de negocio y excepciones propias del dominio). No depende de cómo se muestren los datos.
- **`view`**: expone la interfaz de consola (`console.py`) y una interfaz gráfica construida con [Kivy](https://kivy.org/) (`interfaz_kivy.py`), ambas encargadas de solicitar datos al usuario y mostrar resultados. Ninguna contiene lógica de negocio.
- **`controller`**: actúa como intermediario entre `view` y `model`, coordinando el flujo de la aplicación sin mezclar responsabilidades de cálculo ni de presentación. `hipoteca_controller.py` es usado por **ambas** vistas (consola y Kivy): convierte el texto ingresado en los tipos de datos del modelo (tolerando formatos numéricos como `1,2` o `300.000.000`) y traduce cualquier error —de formato, de regla de negocio o inesperado— a un mensaje legible mediante una única excepción, `ErrorCalculoHipoteca`.
- **`tests`**: pruebas unitarias que validan el comportamiento de `model`, incluyendo casos válidos, casos límite y manejo de excepciones.
- **`doc`**: soporte documental del proyecto (entrevista de requisitos y casos de prueba).

## Funcionalidades

La lógica de negocio (`src/model/logica_hipoteca_inversa.py`) expone la función `desembolso_mensual(valor_inmueble, porcentaje, tasa_mensual, plazo_meses)`, que calcula, usando la fórmula de anualidad financiera:

- **Cuota mensual**: el valor que el banco pagaría mensualmente al propietario.
- **Abonos totales**: la suma de todas las cuotas pagadas durante el plazo.
- **Intereses totales**: la diferencia entre los abonos totales y el valor financiado del inmueble.

Si la tasa mensual es `0`, el cálculo usa una división simple del valor financiado entre el número de meses, evitando la indeterminación de la fórmula de anualidad.

### Reglas de negocio y validaciones

La función valida los datos de entrada y lanza una excepción específica por cada regla incumplida:

| Excepción | Condición que la dispara |
|---|---|
| `ValorPropiedad0` | El valor del inmueble es menor o igual a 0 |
| `HipotecaUsura` | La tasa mensual supera el 4% (límite de usura) |
| `PlazoMayor240` | El plazo excede los 240 meses (20 años) |
| `PlazoMenorIgual0` | El plazo es menor o igual a 0 meses |

### Pruebas unitarias

`tests/tests_hipoteca_inversa.py` valida el comportamiento de `desembolso_mensual` con:

- 3 casos normales con distintos valores de inmueble, porcentaje, tasa y plazo.
- 3 casos extraordinarios: tasa mensual en cero, desembolso único a 1 mes con 100% de financiación, y plazo máximo permitido (240 meses).
- 4 casos de error, uno por cada excepción de negocio (`ValorPropiedad0`, `HipotecaUsura`, `PlazoMenorIgual0`, `PlazoMayor240`).

## Requisitos

- Python 3.10 o superior
- La interfaz de consola no requiere dependencias externas (usa únicamente la librería estándar de Python)
- La interfaz gráfica (`interfaz_kivy.py`) requiere [Kivy](https://kivy.org/):

  ```bash
  pip install -r requirements.txt
  ```

Puedes verificar tu versión de Python con:

```bash
python --version
```

## Cómo ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/Jose-Dv/Hipoteca-inversa.git
```

### 2. Ubicarse en la carpeta del proyecto

```bash
cd Hipoteca-inversa
```

### 3. Ejecutar la interfaz de consola

```bash
python src/view/console.py
```

Esto iniciará la aplicación en modo consola, donde podrás ingresar los datos solicitados (valor del inmueble, porcentaje de financiación, tasa de interés mensual y plazo en meses) para obtener la cuota mensual, los abonos totales y los intereses totales de la hipoteca inversa.

### 4. Ejecutar la interfaz gráfica (Kivy)

Instala primero la dependencia de Kivy (ver [Requisitos](#requisitos)) y luego ejecuta, desde la raíz del proyecto:

```bash
python -m src.view.interfaz_kivy
```

Se abrirá una ventana con campos para ingresar el valor del inmueble, el porcentaje de desembolso, la tasa de interés mensual y el plazo en meses. Al presionar **Calcular**, se muestra la cuota mensual, el total de abonos y el total de intereses, o el mensaje de error correspondiente si algún dato no cumple las reglas de negocio.

### 5. Ejecutar las pruebas unitarias

Desde la raíz del proyecto:

```bash
python -m unittest tests/tests_hipoteca_inversa.py
```

O bien, si prefieres ejecutar todas las pruebas del proyecto automáticamente:

```bash
python -m unittest discover -s tests
```

Un resultado exitoso mostrará algo similar a:

```
----------------------------------------------------------------------
Ran 10 tests in 0.00Xs

OK
```

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.
