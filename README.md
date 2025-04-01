# DS1302 RTC Library for Raspberry Pi

## 📌 Visão Geral

Esta biblioteca permite a comunicação com o RTC DS1302 usando a Raspberry Pi via GPIO.
O DS1302 é um chip de relógio em tempo real (RTC) que mantém a data e a hora mesmo quando a Raspberry Pi está desligada.

## 📦 Instalação

Antes de usar a biblioteca, certifique-se de que a Raspberry Pi tenha o `RPi.GPIO` instalado:

```bash
pip install RPi.GPIO
```

# Mapeamento dos Pinos para o DS1302

A tabela abaixo descreve o mapeamento dos pinos GPIO da Raspberry Pi usados para se comunicar com o módulo DS1302:

| **Sinal** | **Pino no DS1302** | **GPIO na Raspberry Pi** |
| --------- | ------------------ | ------------------------ |
| VCC       | 1                  | 3.3V ou 5V               |
| GND       | 2                  | GND                      |
| CLK       | 6                  | GPIO4 (Pino 7)           |
| DAT       | 7                  | GPIO5 (Pino 29)          |
| RST       | 8                  | GPIO6 (Pino 31)          |

## 🚀 Exemplo de Uso

```python
from ds1302 import DS1302

# Definição dos pinos GPIO
CLK_PIN = 4   # GPIO4 -> Pino 7
DAT_PIN = 5   # GPIO5 -> Pino 29
RST_PIN = 6   # GPIO6 -> Pino 31

try:
    rtc = DS1302(CLK_PIN, DAT_PIN, RST_PIN)
    print("DS1302 inicializado com sucesso.")

    # Definir data e hora [segundo, minuto, hora, dia, mês, dia da semana, ano]
    date = [25, 20, 19, 31, 3, 1, 25]
    rtc.setDateTime(date)

    print(f"Tempo atual: {rtc.getDateTime()}")
except KeyboardInterrupt:
    print("Programa interrompido pelo usuário.")
finally:
    rtc.cleanupGPIO()
```

## 🚀 Funções Públicas

### `setRAM(self, data)`

Escreve dados na memória RAM do DS1302 (máximo de 31 bytes).

**Parâmetros:**

- `data`: Uma lista de caracteres que você deseja armazenar na RAM. A quantidade de dados não pode exceder 31 bytes.

---

### `getRAM(self)`

Lê os dados armazenados na RAM do DS1302.

**Retorno:**

- Retorna os dados armazenados na RAM como uma string de até 31 caracteres.

---

### `cleanupGPIO(self)`

Limpa os pinos GPIO.

Esta função deve ser chamada quando os pinos GPIO não forem mais necessários, garantindo que os pinos não fiquem em um estado indeterminado.

---

### `second(self, second=None)`

Lê ou define os segundos do DS1302.

**Parâmetros:**

- `second`: Se fornecido, define o valor dos segundos (de 0 a 59). Caso contrário, retorna o valor atual dos segundos.

**Retorno:**

- Se `second` não for fornecido, retorna o valor atual dos segundos.

---

### `minute(self, minute=None)`

Lê ou define os minutos do DS1302.

**Parâmetros:**

- `minute`: Se fornecido, define o valor dos minutos (de 0 a 59). Caso contrário, retorna o valor atual dos minutos.

**Retorno:**

- Se `minute` não for fornecido, retorna o valor atual dos minutos.

---

### `hour(self, hour=None)`

Lê ou define a hora do DS1302.

**Parâmetros:**

- `hour`: Se fornecido, define o valor da hora (de 0 a 23). Caso contrário, retorna o valor atual da hora.

**Retorno:**

- Se `hour` não for fornecido, retorna o valor atual da hora.

---

### `day(self, day=None)`

Lê ou define o dia do DS1302.

**Parâmetros:**

- `day`: Se fornecido, define o valor do dia (de 1 a 31). Caso contrário, retorna o valor atual do dia.

**Retorno:**

- Se `day` não for fornecido, retorna o valor atual do dia.

---

### `month(self, month=None)`

Lê ou define o mês do DS1302.

**Parâmetros:**

- `month`: Se fornecido, define o valor do mês (de 1 a 12). Caso contrário, retorna o valor atual do mês.

**Retorno:**

- Se `month` não for fornecido, retorna o valor atual do mês.

---

### `weekday(self, weekday=None)`

Lê ou define o dia da semana do DS1302.

**Parâmetros:**

- `weekday`: Se fornecido, define o valor do dia da semana (de 0 a 6, onde 0 = Domingo). Caso contrário, retorna o valor atual do dia da semana.

**Retorno:**

- Se `weekday` não for fornecido, retorna o valor atual do dia da semana.

---

### `year(self, year=None)`

Lê ou define o ano do DS1302.

**Parâmetros:**

- `year`: Se fornecido, define o valor do ano (de 0 a 99). Caso contrário, retorna o valor atual do ano.

**Retorno:**

- Se `year` não for fornecido, retorna o valor atual do ano.

---

### `setDateTime(self, dateTime)`

Define a data e hora do DS1302.

**Parâmetros:**

- `dateTime`: Uma lista no formato `[segundo, minuto, hora, dia, mês, dia da semana, ano]`.
  - Hora no formato 24h (0-23)
  - Dia da semana: 0-6 (0 = Domingo)

**Exemplo:**

```python
ds1302.setDateTime([0, 30, 14, 15, 4, 3, 22])
```

### `getDateTime(self)`

Lê a data e hora do DS1302.

**Retorno:**

- Retorna a data e hora completa

**Exemplo:**

```python
print(ds1302.getDateTime())
# Segunda 2025-04-01 00:00:00
```

---

## 📜 Licença

Este projeto é licenciado sob a [MIT License](LICENSE) - consulte o arquivo `LICENSE` para mais detalhes.

## 🦾 Créditos

Essa biblioteca foi baseada no microbit-lib (https://github.com/shaoziyang/microbit-lib)

## 💻 Autor

Desenvolvido por Guilherme Fernandes

---
