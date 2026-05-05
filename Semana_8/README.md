# CSP con Backtracking y AC-3

Este proyecto implementa un solucionador de problemas de satisfaccion de restricciones
(CSP, por sus siglas en ingles) usando backtracking, inferencia con AC-3 y heuristicas
para seleccionar variables.

El programa incluye una interfaz por consola en `cps_backtracking/main.py` para ingresar
variables, dominios y restricciones, ejecutar el algoritmo y mostrar los resultados.

## Estructura

- `cps_backtracking/main.py`: interfaz de consola para ingresar el problema y ejecutar el solucionador.
- `cps_backtracking/csp/csp.py`: implementacion de las clases y algoritmos CSP.
- `cps_backtracking/csp/__init__.py`: exporta las funciones principales del paquete.
- `tests/test_csp.py`: pruebas unitarias del solucionador.

## Instalacion

Desde la carpeta `Semana_8`, instale las dependencias:

```bash
pip install -r requirements.txt
```

Si su sistema usa `python3` y `pip3`, puede ejecutar:

```bash
pip3 install -r requirements.txt
```

## Ejecucion

Desde la raiz del repositorio:

```bash
python3 Semana_8/cps_backtracking/main.py
```

Tambien puede ejecutarse desde la carpeta `Semana_8`:

```bash
python3 cps_backtracking/main.py
```

## Uso de la interfaz

Al iniciar, el programa pregunta si desea usar el ejemplo incluido:

```text
Usar ejemplo de cursos A-G? [s/N]:
```

Si responde `s`, se cargan automaticamente:

- Variables: `A, B, C, D, E, F, G`
- Dominio: `Monday, Tuesday, Wednesday`
- Restricciones: `A!=B`, `A!=C`, `B!=C`, etc.

Si responde `n` o deja vacio, debe ingresar sus propios datos.

### Variables

Las variables se ingresan separadas por coma:

```text
A, B, C
```

Cada variable representa un elemento al que se le debe asignar un valor. En el ejemplo
de cursos, cada variable puede ser un curso.

### Dominio

El dominio tambien se ingresa separado por coma:

```text
Monday, Tuesday, Wednesday
```

El dominio contiene los valores posibles que puede tomar cada variable.

### Restricciones

Las restricciones se ingresan separadas por coma usando el formato `X!=Y`:

```text
A!=B, B!=C
```

Esta restriccion significa que las variables conectadas no pueden recibir el mismo valor.
Por ejemplo, `A!=B` indica que `A` y `B` no pueden asignarse al mismo dia.

## Opciones de algoritmo

Despues de ingresar el problema, el programa permite escoger el algoritmo:

```text
1. Backtracking simple
2. Backtracking con AC-3
```

### Backtracking simple

El backtracking simple intenta asignar valores a las variables una por una.

Para cada variable:

1. Prueba un valor de su dominio.
2. Revisa si la asignacion cumple las restricciones con las variables ya asignadas.
3. Si cumple, continua con la siguiente variable.
4. Si no cumple o mas adelante no hay solucion, retrocede y prueba otro valor.

Este metodo garantiza encontrar una solucion si existe, pero puede explorar muchas
combinaciones.

### Backtracking con AC-3

El backtracking con inferencia usa AC-3 despues de cada asignacion.

AC-3 revisa la consistencia de arcos entre variables. En este proyecto, un arco es una
relacion entre dos variables que tienen una restriccion `!=`.

La idea principal es:

1. Cuando una variable recibe un valor, su dominio se reduce a ese valor.
2. AC-3 revisa si las variables vecinas todavia tienen valores compatibles.
3. Si algun dominio queda vacio, esa rama se descarta inmediatamente.
4. Si los dominios siguen siendo validos, el algoritmo continua buscando solucion.

Esto permite detectar fallos antes que el backtracking simple.

## Heuristicas disponibles

Cuando se usa backtracking con AC-3, se puede escoger una heuristica para seleccionar
la siguiente variable:

```text
1. Primera variable disponible
2. MRV
3. Degree
4. MRV + Degree
```

### Primera variable disponible

Selecciona la primera variable no asignada de la lista.

### MRV

MRV significa Minimum Remaining Values.

Selecciona la variable con el dominio mas pequeno. La idea es resolver primero la
variable mas restringida, porque tiene menos opciones disponibles.

### Degree

Selecciona la variable con mayor cantidad de restricciones hacia otras variables no
asignadas.

La idea es escoger primero la variable que mas afecta al resto del problema.

### MRV + Degree

Primero aplica MRV. Si varias variables tienen el mismo tamano de dominio, usa Degree
para desempatar.

## Ejemplo de entrada manual

```text
Usar ejemplo de cursos A-G? [s/N]: n
Variables separadas por coma (ej: A, B, C): A, B
Dominio separado por coma (ej: Monday, Tuesday): Monday, Tuesday
Ingrese restricciones separadas por coma: A!=B
Seleccione una opcion [2]: 2
Seleccione una opcion [1]: 2
```

## Ejemplo de salida

```text
Problema ingresado
Variables: A, B
Dominio: Monday, Tuesday
Restricciones: A!=B

AC-3: consistente

Dominios
  A: ['Monday', 'Tuesday']
  B: ['Monday', 'Tuesday']

Solucion
  A: Monday
  B: Tuesday
```

Si el problema no tiene solucion, el programa muestra:

```text
No se encontro solucion.
```

## Pruebas

Desde la raiz del repositorio:

```bash
pytest Semana_8/tests/test_csp.py
```

Desde la carpeta `Semana_8`:

```bash
pytest
```
