"""Controlador de la hipoteca inversa.

Coordina la comunicación entre las vistas (consola, Kivy) y el modelo de
negocio (`src.model.logica_hipoteca_inversa`). Concentra en un solo lugar
la lógica que, de otro modo, cada vista tendría que reimplementar:

- Convertir el texto que escribe el usuario en los tipos de datos que
  espera el modelo, tolerando formatos numéricos comunes (punto o coma
  como separador decimal, puntos o comas como separador de miles), para
  que la aplicación funcione sin importar cómo el usuario esté
  acostumbrado a escribir números.
- Traducir cualquier error (de formato, de una regla de negocio, o un
  error inesperado durante el cálculo) a un mensaje legible, mediante
  una única excepción (`ErrorCalculoHipoteca`).

Gracias a esto, ninguna vista necesita conocer las excepciones propias
del modelo ni reimplementar el parseo de datos: todas llaman a
`calcular_hipoteca()` y solo se encargan de pedir datos y mostrar el
resultado o el mensaje de error.
"""

from dataclasses import dataclass

from src.model import logica_hipoteca_inversa as logica


class ErrorCalculoHipoteca(Exception):
    """Error de formato, de regla de negocio o inesperado al calcular.

    Es el único tipo de excepción que las vistas necesitan capturar.
    """


@dataclass(frozen=True)
class ResultadoHipoteca:
    """Resultado del cálculo, listo para que la vista lo muestre."""

    cuota_mensual: float
    total_abonos: float
    total_intereses: float


def _normalizar_numero(texto: str) -> str:
    """Tolera formatos numéricos comunes en español y en inglés.

    Ejemplos de texto que esta función deja listos para ``float()``:

    - ``"1,2"``               -> ``"1.2"``            (coma decimal)
    - ``"300.000.000"``       -> ``"300000000"``      (puntos de miles)
    - ``"300,000,000"``       -> ``"300000000"``      (comas de miles)
    - ``"300.000.000,50"``    -> ``"300000000.50"``   (formato es-CO)
    - ``"300,000,000.50"``    -> ``"300000000.50"``   (formato en-US)
    """
    texto = texto.strip()
    tiene_coma = "," in texto
    tiene_punto = "." in texto

    if tiene_coma and tiene_punto:
        # El separador que aparece de último es el decimal; el otro,
        # separador de miles.
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif texto.count(",") > 1:
        texto = texto.replace(",", "")
    elif tiene_coma:
        texto = texto.replace(",", ".")
    elif texto.count(".") > 1:
        texto = texto.replace(".", "")

    return texto


def _a_float(texto: str, nombre_campo: str, ejemplo: str) -> float:
    try:
        return float(_normalizar_numero(texto))
    except (TypeError, ValueError) as error:
        raise ErrorCalculoHipoteca(
            f"{nombre_campo} debe ser un número (ejemplo: {ejemplo})."
        ) from error


def _a_entero_meses(texto: str) -> int:
    valor = _a_float(texto, "El plazo en meses", "120")
    if not valor.is_integer():
        raise ErrorCalculoHipoteca(
            "El plazo en meses debe ser un número entero, sin decimales (ejemplo: 120)."
        )
    return int(valor)


def construir_parametros(
    valor_inmueble_texto: str,
    porcentaje_texto: str,
    tasa_texto: str,
    plazo_texto: str,
) -> logica.ParametrosHipoteca:
    """Convierte el texto ingresado por el usuario en ``ParametrosHipoteca``.

    Lanza ``ErrorCalculoHipoteca`` si algún campo no tiene un formato
    numérico válido.
    """
    valor_inmueble = _a_float(valor_inmueble_texto, "El valor del inmueble", "300000000")
    porcentaje = _a_float(porcentaje_texto, "El porcentaje de desembolso", "40") / 100
    tasa_mensual = _a_float(tasa_texto, "La tasa de interés mensual", "1.2") / 100
    plazo_meses = _a_entero_meses(plazo_texto)

    return logica.ParametrosHipoteca(
        valor_inmueble=valor_inmueble,
        porcentaje=porcentaje,
        tasa_mensual=tasa_mensual,
        plazo_meses=plazo_meses,
    )


def calcular_hipoteca(
    valor_inmueble_texto: str,
    porcentaje_texto: str,
    tasa_texto: str,
    plazo_texto: str,
) -> ResultadoHipoteca:
    """Punto de entrada único usado por todas las vistas (consola y Kivy).

    Retorna un ``ResultadoHipoteca`` si el cálculo fue exitoso. En
    cualquier otro caso lanza ``ErrorCalculoHipoteca`` con un mensaje ya
    listo para mostrar al usuario, sin importar si el problema fue de
    formato, de una regla de negocio del modelo, o un error inesperado
    (por ejemplo, una combinación de datos extrema que produzca una
    división por cero en el cálculo financiero).
    """
    parametros = construir_parametros(
        valor_inmueble_texto, porcentaje_texto, tasa_texto, plazo_texto
    )

    try:
        cuota, abonos, intereses = logica.desembolso_mensual(parametros)
    except logica.HipotecaInversaError as error:
        raise ErrorCalculoHipoteca(str(error)) from error
    except Exception as error:  # defensa ante cualquier caso no previsto
        raise ErrorCalculoHipoteca(
            "No fue posible calcular la hipoteca con esos datos. "
            "Verifique los valores ingresados e intente nuevamente."
        ) from error

    return ResultadoHipoteca(cuota, abonos, intereses)
