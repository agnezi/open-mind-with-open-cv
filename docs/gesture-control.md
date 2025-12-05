# Controle por Gestos via HTTP

## O que foi implementado?

Sistema de **controle remoto via gestos de mão** que envia comandos HTTP POST com JSON no body para um dispositivo externo (como um robô, ESP32, etc.) quando gestos específicos são reconhecidos.

**Principais características**:
- Envia **POST requests** com JSON no body
- **URL única** para todos os comandos
- **Debounce global** de 250ms para evitar spam
- Comandos simples e configuráveis

## Arquitetura

### Novos Arquivos

1. **[src/control/gesture_control.py](../src/control/gesture_control.py)**
   - Módulo de controle HTTP
   - Classe `GestureController` que envia comandos HTTP
   - Sistema de cooldown para evitar spam
   - Tratamento de erros de conexão

2. **[src/control/__init__.py](../src/control/__init__.py)**
   - Exporta `GestureController` para uso fácil

### Arquivos Modificados

1. **[src/config.py](../src/config.py)**
   - Adicionadas configurações de controle HTTP
   - Mapeamento de gestos para endpoints
   - Configurações de timeout e cooldown

2. **[hand_detection.py](../hand_detection.py)**
   - Integrado `GestureController`
   - Tecla 'c' para ativar/desativar controle
   - Indicador visual de status do controle

## Como Usar

### 1. Configurar a URL do Dispositivo

A URL é **única** para todos os comandos. Configure no [src/config.py](../src/config.py) ou arquivo `.env`:

**Opção A: Editar config.py diretamente**
```python
CONTROL_URL = 'http://YOUR_URL'  # Seu dispositivo
```

**Opção B: Usar arquivo .env** (recomendado)
```bash
# .env
CONTROL_URL=http://YOUR_URL
```

**Padrão**: `http://YOUR_URL` (já configurado)

### 2. Configurar Mapeamento de Gestos

No [src/config.py](../src/config.py), edite o dicionário `GESTURE_COMMANDS`:

```python
GESTURE_COMMANDS = {
    'Open Hand': 'forward',      # Mão aberta = avançar
    'Fist': 'stop',              # Punho = parar
    'Pointing': 'turn_right',    # Apontar = virar direita
    'Peace Sign': 'turn_left',   # Sinal de paz = virar esquerda
    'Thumbs Up': 'speed_up',     # Joinha = acelerar
    'Rock On': 'reverse',        # Rock = ré
}
```

**Nota**: Os valores são **comandos**, não endpoints! Serão enviados no JSON.

### 3. Executar o Sistema

```bash
python hand_detection.py
```

### 4. Controles

- **'c'** - Ativar/Desativar envio de comandos HTTP
- **'q'** - Sair
- **'s'** - Salvar frame

**Importante**: O controle começa **DESATIVADO** por segurança. Pressione 'c' para ativar.

## Gestos Disponíveis

Baseado no seu sistema atual de reconhecimento:

| Gesto | Dedos | Comando | JSON Enviado |
|-------|-------|---------|--------------|
| **Open Hand** | Todos levantados | forward | `{"command": "forward", ...}` |
| **Fist** | Todos fechados | stop | `{"command": "stop", ...}` |
| **Pointing** | Só indicador | turn_right | `{"command": "turn_right", ...}` |
| **Peace Sign** | Indicador + médio | turn_left | `{"command": "turn_left", ...}` |
| **Thumbs Up** | Só polegar | speed_up | `{"command": "speed_up", ...}` |
| **Rock On** | Polegar + mindinho | reverse | `{"command": "reverse", ...}` |

## Configurações Avançadas

### Debounce Global (Tempo entre QUALQUER Comando)

Evita enviar comandos muito rápido (global para todos os gestos):

```python
GESTURE_DEBOUNCE = 0.25  # Segundos entre QUALQUER comando (250ms)
```

- **Valor menor** (0.1-0.2s): Mais responsivo, mas pode sobrecarregar
- **Valor maior** (0.5-1s): Menos responsivo, mais estável
- **Padrão**: 0.25s (250ms) - bom balanço

### Timeout HTTP

Tempo máximo de espera por resposta:

```python
HTTP_TIMEOUT = 2  # Segundos
```

## Formato do JSON Enviado

Todos os comandos são enviados como **HTTP POST** com este formato:

```json
{
  "command": "forward",
  "gesture": "Open Hand",
  "timestamp": 1234567890.123
}
```

**Campos**:
- `command`: String do comando (ex: "forward", "stop")
- `gesture`: Nome do gesto reconhecido (ex: "Open Hand")
- `timestamp`: Unix timestamp com precisão de milissegundos

## Exemplo de Uso com ESP32

Se você tem um ESP32, seu código Arduino/ESP32 deve receber POST:

```cpp
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

WebServer server(80);

void handleCommand() {
  // Ler body do POST
  String body = server.arg("plain");

  // Parse JSON
  StaticJsonDocument<200> doc;
  deserializeJson(doc, body);

  String command = doc["command"];
  String gesture = doc["gesture"];

  // Executar comando
  if (command == "forward") {
    // Mover para frente
    Serial.println("Moving forward");
  } else if (command == "stop") {
    // Parar
    Serial.println("Stopped");
  } else if (command == "turn_right") {
    // Virar direita
    Serial.println("Turning right");
  }
  // ... outros comandos

  server.send(200, "application/json", "{\"status\":\"ok\"}");
}

void setup() {
  Serial.begin(115200);

  // Conectar WiFi...

  // Endpoint ÚNICO que recebe todos os comandos
  server.on("/", HTTP_POST, handleCommand);

  server.begin();
  Serial.println("Server started");
}

void loop() {
  server.handleClient();
}
```

## Testando a Conexão

O módulo testa automaticamente a conexão ao inicializar. Você verá:

```
✓ Connection successful to http://YOUR_URL
```

Ou:

```
✗ Connection failed to http://YOUR_URL: ...
```

## Logs de Comandos

Quando um comando é enviado, você verá no terminal:

```
✓ Sent: forward (gesture: Open Hand)
```

Se houver erro:

```
✗ Connection error
✗ Request timeout
✗ Failed. Status: 404
```

## Indicador Visual

Na tela do vídeo:
- **"CONTROL: ON"** (verde) - Comandos sendo enviados
- **"CONTROL: OFF"** (vermelho) - Comandos desativados

## Personalizando Comandos

### Exemplo: Controlar Luzes

```python
GESTURE_COMMANDS = {
    'Open Hand': 'light_on',
    'Fist': 'light_off',
    'Pointing': 'brightness_up',
    'Peace Sign': 'brightness_down',
    'Thumbs Up': 'warm_color',
    'Rock On': 'cool_color',
}
```

Seu servidor receberia: `{"command": "light_on", ...}`

### Exemplo: Controlar Drones

```python
GESTURE_COMMANDS = {
    'Open Hand': 'takeoff',
    'Fist': 'land',
    'Pointing': 'move_right',
    'Peace Sign': 'move_left',
    'Thumbs Up': 'move_up',
    'Rock On': 'move_down',
}
```

Seu servidor receberia: `{"command": "takeoff", ...}`

## Uso Programático

Você também pode usar o `GestureController` em seus próprios scripts:

```python
from src.control import GestureController

# Inicializar
controller = GestureController('http://YOUR_URL')

# Testar conexão
if controller.test_connection():
    # Enviar comando de gesto (POST com JSON)
    controller.send_gesture_command('Open Hand')
    # Envia: {"command": "forward", "gesture": "Open Hand", ...}

    # Ou enviar comando customizado
    controller.send_custom_command('custom_action')
    # Envia: {"command": "custom_action", ...}
```

## Segurança

### Prevenção de Spam
- Sistema de **debounce global** impede envio rápido demais
- **250ms** entre QUALQUER comando (não por gesto)
- Evita sobrecarga do dispositivo receptor

### Controle Manual
- Sistema começa desativado
- Usuário deve ativar manualmente com tecla 'c'
- Indicador visual claro do status

### Tratamento de Erros
- Timeout automático em requisições
- Não trava se dispositivo estiver offline
- Logs claros de sucesso/erro

## Troubleshooting

### "Connection error" constante
1. Verifique se o dispositivo está ligado
2. Confirme o IP no config.py
3. Teste ping: `ping http://YOUR_URL`
4. Verifique se estão na mesma rede

### Comandos não respondem
1. Verifique se controle está ativado (pressione 'c')
2. Observe o debounce (aguarde 250ms entre gestos)
3. Verifique se seu servidor aceita POST com JSON
4. Verifique logs no terminal

### Gestos não reconhecidos
- Isso é problema de detecção, não do controle HTTP
- Ajuste iluminação e posição da mão
- Veja documentação de detecção de mãos

## Performance

- **Latência**: ~50-200ms (depende da rede)
- **Debounce**: 250ms entre comandos
- **Impacto no FPS**: Mínimo (~1-2 FPS)
- **Requisições síncronas**: Podem travar momentaneamente se timeout

## Próximos Passos

Possíveis melhorias:

1. **Requisições assíncronas** - Não bloquear thread principal
2. **WebSockets** - Conexão persistente para menor latência
3. **Feedback visual** - Mostrar resposta do dispositivo na tela
4. **Múltiplos dispositivos** - Controlar vários dispositivos
5. **Gestos customizados** - Criar seus próprios gestos
6. **Ajuste de debounce dinâmico** - Mudar debounce em tempo real
