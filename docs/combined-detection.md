# Detecção Combinada de Mãos e Pessoa

## O que foi implementado?

Modularizamos o código de detecção e criamos um sistema que permite detectar **mãos e pessoas (corpo inteiro) simultaneamente** no mesmo vídeo.

## Estrutura do Código

### Novos Arquivos Criados

1. **[src/detection/face_detector.py](../src/detection/face_detector.py)**
   - Módulo de detecção de pessoas modularizado
   - Usa Haar Cascade Full Body do OpenCV
   - Interface similar ao `HandDetector`
   - Detecta corpo humano completo

2. **[combined_detection.py](../combined_detection.py)**
   - Script principal para detecção combinada
   - Detecta mãos E pessoas (corpo inteiro) ao mesmo tempo
   - Visual limpo: mãos com detalhes + corpo com quadrado azul

### Arquivos Modificados

1. **[src/detection/__init__.py](../src/detection/__init__.py)**
   - Adicionado export do `FaceDetector`

2. **[src/config.py](../src/config.py)**
   - Adicionadas configurações de detecção de pessoa:
     - `PERSON_SCALE_FACTOR = 1.1`
     - `PERSON_MIN_NEIGHBORS = 3` (mais sensível para corpo inteiro)
     - `PERSON_MIN_SIZE = (60, 120)` (maior para corpo completo)

3. **[face_detection.py](../face_detection.py)**
   - Atualizado para usar o módulo `FaceDetector` (agora detecta corpo inteiro)
   - Detecta pessoas completas em vez de apenas rostos
   - Mantém funcionalidades de gravação e screenshot

## Como Usar

### 1. Detecção Apenas de Mãos (sem alterações)
```bash
python hand_detection.py
```
- Detecta apenas mãos
- Reconhece gestos
- Mostra labels dos dedos

### 2. Detecção Apenas de Pessoas (corpo inteiro)
```bash
python face_detection.py
```
- Detecta apenas pessoas (corpo completo)
- Quadrado azul simples ao redor do corpo
- Suporta gravação de vídeo (tecla 'r')
- Suporta screenshot (tecla 's')

### 3. Detecção Combinada (NOVO!)
```bash
python combined_detection.py
```
- Detecta **mãos e pessoas simultaneamente**
- Mãos: landmarks verdes + gestos + labels de dedos
- Pessoas: apenas quadrado azul simples ao redor do corpo
- Mostra contadores no topo: "Hands: X | People: Y"

## Controles

Todos os scripts usam os mesmos controles básicos:
- **'q'** - Sair do programa
- **'s'** - Salvar frame atual como imagem

O `face_detection.py` também tem:
- **'r'** - Iniciar/parar gravação de vídeo

## Detalhes Técnicos

### FaceDetector (Person Detector)

**Classe**: `FaceDetector` (nome mantido para compatibilidade, mas detecta corpo inteiro)

**Métodos**:
- `__init__()` - Carrega o Haar Cascade Full Body
- `process(frame)` - Detecta pessoas (corpo inteiro), retorna lista de coordenadas (x, y, w, h)
- `draw_detections(frame, people)` - Desenha retângulos azuis ao redor dos corpos
- `close()` - Cleanup (mantém consistência com HandDetector)

**Uso**:
```python
from src.detection import FaceDetector

detector = FaceDetector()
people = detector.process(frame)  # Detecta pessoas (corpo inteiro)
detector.draw_detections(frame, people)
detector.close()
```

### Configuração

Você pode ajustar os parâmetros no [src/config.py](../src/config.py):

```python
# Detecção mais rigorosa (menos falsos positivos)
PERSON_MIN_NEIGHBORS = 5

# Detecção mais sensível (pode ter mais falsos positivos)
PERSON_MIN_NEIGHBORS = 2

# Ignorar pessoas pequenas (pessoas distantes)
PERSON_MIN_SIZE = (80, 160)

# Detectar pessoas menores/mais próximas
PERSON_MIN_SIZE = (40, 80)
```

## Benefícios da Modularização

✅ **Código reutilizável** - `FaceDetector` (person detector) pode ser usado em qualquer lugar

✅ **Separação de responsabilidades** - Cada módulo tem uma função clara

✅ **Fácil manutenção** - Mudanças no detector não afetam outros códigos

✅ **Interface consistente** - Todos os detectores seguem o mesmo padrão

✅ **Configuração centralizada** - Todos os parâmetros em um só lugar

## Tipos de Detecção Disponíveis

O módulo usa **Haar Cascade Full Body** que detecta pessoas de corpo inteiro. Se precisar de outros tipos:

- **Apenas rosto**: Trocar `haarcascade_fullbody.xml` por `haarcascade_frontalface_default.xml`
- **Parte superior do corpo**: Usar `haarcascade_upperbody.xml`
- **Parte inferior**: Usar `haarcascade_lowerbody.xml`

## Performance

- **Haar Cascade Full Body (pessoas)**: ~5-10ms por frame
- **MediaPipe (mãos)**: ~15-30ms por frame
- **Combinado**: Deve manter ~30 FPS sem problemas

**Nota**: Detecção de corpo inteiro funciona melhor quando:
- A pessoa está visível de corpo completo na câmera
- Boa iluminação
- Pessoa está de pé ou sentada (posição frontal)

## Próximos Passos (Opcional)

Se você quiser estender o sistema:

1. **Adicionar mais detectores** - Seguir o mesmo padrão
2. **Criar gestos customizados** - Modificar `gesture_recognition.py`
3. **Adicionar tracking** - Rastrear IDs de faces/mãos entre frames
4. **Salvar dados** - Exportar coordenadas para análise
