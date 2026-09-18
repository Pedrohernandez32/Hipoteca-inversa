"""Interfaz gráfica en Kivy para el cálculo de hipoteca inversa.

Construida siguiendo los patrones del proyecto de ejemplo
https://github.com/ProfeBill/hello-kivy:

- ``BoxLayout`` (orientation="vertical"/"horizontal") para organizar los
  controles en filas, igual que en ``input.py``.
- ``TextInput`` para capturar los datos numéricos del usuario.
- ``Button.bind(on_press=...)`` para conectar el botón con un callback,
  igual que en ``events.py``.
- ``Label`` para mostrar el resultado del cálculo.

Esta vista no contiene lógica de negocio ni de validación de formato:
solo recoge los datos y se los entrega al controlador
(`src.controller.hipoteca_controller`), el mismo que usa la interfaz de
consola (`console.py`), y muestra el resultado o el mensaje de error que
este le devuelva.

Requisitos:
    pip install "kivy[base]"

Ejecución: se puede lanzar de cualquier forma (`python interfaz_kivy.py`,
`python src/view/interfaz_kivy.py`, `python -m src.view.interfaz_kivy`, o
desde el botón "Run" de un editor) gracias al ajuste de sys.path incluido
más abajo.
"""

import sys
from pathlib import Path

# Agrega la raíz del proyecto a sys.path para que `import src...` funcione
# sin importar cómo se invoque este archivo (ver detalle en console.py).
_RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
if str(_RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(_RAIZ_PROYECTO))

from kivy.app import App  # noqa: E402
from kivy.uix.boxlayout import BoxLayout  # noqa: E402
from kivy.uix.button import Button  # noqa: E402
from kivy.uix.label import Label  # noqa: E402
from kivy.uix.textinput import TextInput  # noqa: E402

from src.controller import hipoteca_controller as controlador  # noqa: E402


def _fila_de_entrada(texto_etiqueta):
    """Crea una fila horizontal con una Label y un TextInput.

    Sigue el mismo patrón de composición de widgets que ``input.py`` en
    hello-kivy: un BoxLayout agrupa los controles y se retorna también
    el TextInput para poder leer su valor más adelante.
    """
    fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=48, spacing=10)
    etiqueta = Label(text=texto_etiqueta, size_hint_x=0.6, halign="left", valign="middle")
    etiqueta.bind(size=etiqueta.setter("text_size"))
    entrada = TextInput(multiline=False, size_hint_x=0.4)
    fila.add_widget(etiqueta)
    fila.add_widget(entrada)
    return fila, entrada


class HipotecaInversaApp(App):
    """Aplicación Kivy: cada app desciende de ``kivy.app.App``."""

    title = "Calculadora de Hipoteca Inversa"

    def build(self):
        # build() crea y retorna el widget contenedor de toda la ventana,
        # tal como se hace en hello.py, input.py y events.py.
        contenedor = BoxLayout(orientation="vertical", padding=20, spacing=12)

        contenedor.add_widget(Label(
            text="Calculadora de Hipoteca Inversa",
            font_size=24,
            size_hint_y=None,
            height=40,
        ))

        fila_valor, self.entrada_valor = _fila_de_entrada("Valor del inmueble:")
        fila_porcentaje, self.entrada_porcentaje = _fila_de_entrada("Porcentaje de desembolso (%):")
        fila_tasa, self.entrada_tasa = _fila_de_entrada("Tasa de interés mensual (%):")
        fila_plazo, self.entrada_plazo = _fila_de_entrada("Plazo en meses:")

        for fila in (fila_valor, fila_porcentaje, fila_tasa, fila_plazo):
            contenedor.add_widget(fila)

        boton_calcular = Button(text="Calcular", size_hint_y=None, height=56)
        # bind(on_press=...) conecta el evento del botón con el callback,
        # igual que Boton.bind(on_press=self.callback) en events.py.
        boton_calcular.bind(on_press=self.calcular)
        contenedor.add_widget(boton_calcular)

        self.resultado = Label(text="Ingrese los datos y presione Calcular.", halign="center")
        self.resultado.bind(size=self.resultado.setter("text_size"))
        contenedor.add_widget(self.resultado)

        return contenedor

    def calcular(self, instance):
        """Callback del botón Calcular.

        ``instance`` es el widget que generó el evento (el propio botón),
        siguiendo la misma convención de ``seleccionar_casilla`` en
        tictactoe.py. Todo el trabajo de conversión de datos, validación
        de negocio y manejo de errores vive en el controlador, que es el
        mismo que usa la consola: esta vista solo lee los TextInput y
        escribe el resultado.
        """
        try:
            resultado = controlador.calcular_hipoteca(
                self.entrada_valor.text,
                self.entrada_porcentaje.text,
                self.entrada_tasa.text,
                self.entrada_plazo.text,
            )
        except controlador.ErrorCalculoHipoteca as error:
            self.resultado.text = str(error)
            return

        self.resultado.text = (
            f"Cuota mensual: {resultado.cuota_mensual:,.2f}\n"
            f"Total abonos: {resultado.total_abonos:,.2f}\n"
            f"Total intereses: {resultado.total_intereses:,.2f}"
        )


if __name__ == "__main__":
    HipotecaInversaApp().run()
