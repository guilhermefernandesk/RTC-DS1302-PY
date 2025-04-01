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