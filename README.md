# practicepilot

Paquete Python instalable desde GitHub (incluyendo Google Colab) para utilidades y componentes de *practice workflows*.

## Instalación

### Desde GitHub (recomendado para Colab)

```bash
pip install git+https://github.com/sigifredo/practicepilot.git
```

## Desarrollo local (editable)

```bash
git clone https://github.com/sigifredo/practicepilot.git
cd practicepilot
pip install -e .
```

## Uso

```python
import practicepilot
```

Si el paquete expone funciones específicas desde `practicepilot/__init__.py`, podrás importarlas directamente:

```python
from practicepilot import <algo>
```

## Colab: ejemplo mínimo

```bash
!pip install -q git+https://github.com/sigifredo/practicepilot.git
```

```python
import practicepilot
print('practicepilot importó correctamente')
```