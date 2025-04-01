# -----------------------------------------------------------------------
#   Copyright (C) 2018 shaoziyang
#   Copyright (C) 2019 Omar BENHAMID
#   Copyright (C) 2025 Guilherme Fernandes
# -----------------------------------------------------------------------
#   Arquivo: ds1302.py
#            Biblioteca de comunicação com o RTC DS1302 para Raspberry Pi
#   Autor:   Guilherme Fernandes de Oliveira
#            d2021005067 at unifei.edu.br
#   Licença: MIT License
# -----------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------

import RPi.GPIO as GPIO
import time

class DS1302:
  # Definição dos endereços dos registradores do DS1302
  _REG_SECOND_WRITE          = (0x80)
  _REG_MINUTE_WRITE          = (0x82)
  _REG_HOUR_WRITE            = (0x84)
  _REG_DAY_WRITE             = (0x86)
  _REG_MONTH_WRITE           = (0x88)
  _REG_DAYOFWEEK_WRITE       = (0x8A)
  _REG_YEAR_WRITE            = (0x8C)
  _REG_WP_WRITE              = (0x8E)
  _REG_TRICKLE_CHARGER_WRITE = (0x90)
  _REG_CLK_BURST_WRITE       = (0xBE)
  _REG_RAM_START_WRITE       = (0xC0)
  _REG_RAM_END_WRITE         = (0xFC)
  _REG_RAM_BURST_WRITE       = (0xFE)
  _REG_RAM_BURST_READ        = (0xFF)
  _CLK_PERIOD                = 0.000002  # 2us
  _DAYOFWEEK = [ "Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado" ]
  _MASK_TIME = {
    "SECOND": 0b01111111,
    "MINUTE": 0b01111111,
    "HOUR":   0b00111111,
    "DAY":    0b00111111,
    "MONTH":  0b00011111,
    "DAYOFWEEK": 0b00000111,
  }

  def __init__(self, clk_pin, dat_pin, rst_pin):
    self.clk_pin = clk_pin
    self.dat_pin = dat_pin
    self.rst_pin = rst_pin
    
    # Desliga GPIO warnings.
    GPIO.setwarnings(False)
    # Usa a numeração dos pinos GPIO da Raspberry Pi
    GPIO.setmode(GPIO.BCM)
    # Configura os pinos como saida
    GPIO.setup(self.clk_pin, GPIO.OUT)
    GPIO.setup(self.dat_pin, GPIO.OUT)
    GPIO.setup(self.rst_pin, GPIO.OUT)
    # Nível baixo nos pinos ao iniciar
    GPIO.output(self.clk_pin, 0)
    GPIO.output(self.rst_pin, 0)
    GPIO.output(self.dat_pin, 0)
    # Desativa o carregamento de bateria
    self._disableTrickleCharge()

  # ---------------- #
  # Funções privadas #
  # ---------------- #
  def _disableTrickleCharge(self):
    """ Desativa o trickle charge, usado para bateria recarregável """
    self._start()                               
    self._writeByte(self._REG_TRICKLE_CHARGER_WRITE)  
    self._writeByte(0x00)                       
    self._stop()                                

  def _start(self):
    """ Inicia a transmissão de dados """
    GPIO.output(self.clk_pin, 0)
    GPIO.output(self.dat_pin, 0)
    time.sleep(self._CLK_PERIOD) 
    GPIO.output(self.rst_pin, 1)

  def _stop(self):
    """ Finaliza a transmissão de dados """
    GPIO.output(self.clk_pin, 0)
    GPIO.output(self.dat_pin, 0)
    time.sleep(self._CLK_PERIOD) 
    GPIO.output(self.rst_pin, 0)
    GPIO.setup(self.dat_pin, GPIO.OUT)

  def _toggleClk(self):
    GPIO.output(self.clk_pin, 1)
    time.sleep(self._CLK_PERIOD)
    GPIO.output(self.clk_pin, 0)
    time.sleep(self._CLK_PERIOD)
  
  def _writeByte(self, byte):
    '''Envia um byte para o DS1302'''
    GPIO.setup(self.dat_pin, GPIO.OUT)
    for i in range(8):
      GPIO.output(self.dat_pin, (byte >> i) & 1)
      self._toggleClk()

  def _readByte(self):
    """ Lê um byte do DS1302 """
    GPIO.setup(self.dat_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    byte = 0
    for i in range(8):
      bit = GPIO.input(self.dat_pin)
      byte |= (bit << i) 
      self._toggleClk() 
    GPIO.setup(self.dat_pin, GPIO.OUT)
    return byte

  def _disableWP(self):
    """ Desativa o Write Protect """
    self._start()
    self._writeByte(self._REG_WP_WRITE)
    self._writeByte(0x00) # Desativa
    self._stop()

  def _enableWP(self):
    """ Ativa o Write Protect """
    self._start()
    self._writeByte(self._REG_WP_WRITE)
    self._writeByte(0x80) # Ativa
    self._stop()

  def _writeReg(self, address, byte):
    """ Escreve um valor em um registrador do DS1302 """
    self._disableWP()
    self._start()
    self._writeByte(address & 0xFE) #1111_1110 Máscara para zerar o LSB (bit R/W = 0 para escrita)
    self._writeByte(byte)
    self._enableWP()
    self._stop()

  def _readReg(self, address):
    """ Lê um valor de um registrador do DS1302 """
    self._start()
    self._writeByte(address | 0x01) #0000_0001 Máscara para leitura LSB (bit R/W = 1 para leitura)
    value = self._readByte()
    self._stop()
    return value

  def _dec2bcd(self, dec):
    ''' Converte um número decimal para BCD '''
    return ((dec // 10) << 4) | (dec % 10)

  def _bcd2dec(self, bcd):
    ''' Converte um número BCD para decimal '''
    return (bcd >> 4) * 10 + (bcd & 0x0F)
  
  def _validateDateTime(self, dateTime):
    """Valida os valores de data e hora"""
    if len(dateTime) != 7:
        raise ValueError("Formato inválido. Use: [segundo, minuto, hora, dia, mês, dia da semana, ano]")
    
    second, minute, hour, day, month, weekday, year = dateTime
    
    if not (0 <= second <= 59):
        raise ValueError("Segundos devem estar entre 0 e 59")
    if not (0 <= minute <= 59):
        raise ValueError("Minutos devem estar entre 0 e 59")
    if not (0 <= hour <= 23):
        raise ValueError("Hora deve estar entre 0 e 23")
    if not (1 <= day <= 31):
        raise ValueError("Dia deve estar entre 1 e 31")
    if not (1 <= month <= 12):
        raise ValueError("Mês deve estar entre 1 e 12")
    if not (0 <= weekday <= 6):
        raise ValueError("Dia da semana deve estar entre 0 e 6")
    if not (0 <= year <= 99):
        raise ValueError("Ano deve estar entre 0 e 99")

  # ---------------- #
  # Funções públicas #
  # ---------------- #
  def setRAM(self,data):
    ''' Escreve os dados na RAM do DS1302 (máximo de 31 bytes) '''
    if len(data) > 31:
      raise ValueError("Máximo de 31 bytes permitidos na RAM")
    self._start()
    self._writeByte(self._REG_RAM_BURST_WRITE)  
    for char in data:
      self._writeByte(ord(char))
    # Preenche o restante com espaços caso os dados sejam menores que 31 bytes
    for _ in range(31 - len(data)):
        self._writeByte(ord(" "))
    self._stop()

  def getRAM(self):
    ''' Lê os dados da RAM do DS1302 '''
    self._start()
    self._writeByte(self._REG_RAM_BURST_READ)
    # Lê os 31 bytes da RAM
    data = ""
    for _ in range(31):
        byte = self._readByte()
        data += chr(byte)
    self._stop()
    return data

  def cleanupGPIO(self):
    """ Limpa os pinos GPIO """
    GPIO.cleanup([self.clk_pin, self.dat_pin, self.rst_pin])

  def second(self, second=None):
    """ Lê ou define os segundos do DS1302 """
    if second == None:
        return self._bcd2dec(self._readReg(self._REG_SECOND_WRITE) & self._MASK_TIME["SECOND"])
    else:
      if not (0 <= second <= 59):
        raise ValueError("Segundos devem estar entre 0 e 59")
      self._writeReg(self._REG_SECOND_WRITE, self._dec2bcd(second))

  def minute(self, minute=None):
    """ Lê ou define os minutos do DS1302 """
    if minute == None:
      return self._bcd2dec(self._readReg(self._REG_MINUTE_WRITE) & self._MASK_TIME["MINUTE"])
    else:
      if not (0 <= minute <= 59):
        raise ValueError("Minutos devem estar entre 0 e 59")
      self._writeReg(self._REG_MINUTE_WRITE, self._dec2bcd(minute))

  def hour(self, hour=None):
    """ Lê ou define a hora do DS1302 """
    if hour is None:
      return self._bcd2dec(self._readReg(self._REG_HOUR_WRITE) & self._MASK_TIME["HOUR"])
    else:
      if not (0 <= hour <= 23):
        raise ValueError("Hora deve estar entre 0 e 23")
      self._writeReg(self._REG_HOUR_WRITE, self._dec2bcd(hour))

  def day(self, day=None):
    """ Lê ou define o dia do DS1302 """
    if day is None:
      return self._bcd2dec(self._readReg(self._REG_DAY_WRITE) & self._MASK_TIME["DAY"])
    else:
      if not (1 <= day <= 31):
        raise ValueError("Dia deve estar entre 1 e 31")
      self._writeReg(self._REG_DAY_WRITE, self._dec2bcd(day))

  def month(self, month=None):
    """ Lê ou define o mês do DS1302 """
    if month is None:
      return self._bcd2dec(self._readReg(self._REG_MONTH_WRITE) & self._MASK_TIME["MONTH"])
    else:
      if not (1 <= month <= 12):
        raise ValueError("Mês deve estar entre 1 e 12")
      self._writeReg(self._REG_MONTH_WRITE, self._dec2bcd(month))

  def weekday(self, weekday=None):
    """ Lê ou define o dia da semana do DS1302 """
    if weekday is None:
      return self._bcd2dec(self._readReg(self._REG_DAYOFWEEK_WRITE) & self._MASK_TIME["DAYOFWEEK"])
    else:
      if not (0 <= weekday <= 6):
        raise ValueError("Dia da semana deve estar entre 0 e 6")
      self._writeReg(self._REG_DAYOFWEEK_WRITE, self._dec2bcd(weekday))

  def year(self, year=None):
    """ Lê ou define o ano do DS1302 """
    if year is None:
      return self._bcd2dec(self._readReg(self._REG_YEAR_WRITE))
    else:
      if not (0 <= year <= 99):
        raise ValueError("Ano deve estar entre 0 e 99")
      self._writeReg(self._REG_YEAR_WRITE, self._dec2bcd(year))

  def setDateTime(self, dateTime):
    """ Define a data e hora do DS1302
        Formato: [segundo, minuto, hora, dia, mês, dia da semana, ano]
        Hora: formato 24h (0-23)
        Dia da semana: 0-6 (0 = Domingo)
    """
    try:

      self._validateDateTime(dateTime)

      self._start()
      self._writeByte(self._REG_CLK_BURST_WRITE)
      
      for value in [dateTime[0], dateTime[1], dateTime[2], dateTime[3], 
                    dateTime[4], dateTime[5], dateTime[6]]:
        self._writeByte(self._dec2bcd(value))

      self._writeByte(0x00) # Desativa WP
      self._writeByte(0x00) # Desativa TRICKLE_CHARGER

      self._stop()

      print("Data e hora configuradas com sucesso")

    except Exception as e:
      raise Exception(f"Erro ao configurar RTC: {e}")

  def getDateTime(self, format_type=None):
    """
    Lê a data e hora do DS1302

    :param str format_type: Define o formato da data e hora retornada.
    - getDateTime(): "Terça 2025-04-01 16 : 04:58"
    - getDateTime("file"): "2025-04-01_16-14-47"
    """
    try:
        self._start()
        self._writeByte((self._REG_CLK_BURST_WRITE | 0x01)) # 10111111 leitura
        raw_data = [self._readByte() for _ in range(7)]
        self._stop()

        second = format(self._bcd2dec(raw_data[0] & self._MASK_TIME["SECOND"]), "02d")
        minute = format(self._bcd2dec(raw_data[1] & self._MASK_TIME["MINUTE"]), "02d")
        hour = format(self._bcd2dec(raw_data[2] & self._MASK_TIME["HOUR"]), "02d")
        day = format(self._bcd2dec(raw_data[3] & self._MASK_TIME["DAY"]), "02d")
        month = format(self._bcd2dec(raw_data[4] & self._MASK_TIME["MONTH"]), "02d")
        dayofweek = self._DAYOFWEEK[self._bcd2dec(raw_data[5] & self._MASK_TIME["DAYOFWEEK"])]
        year = format(self._bcd2dec(raw_data[6]) + 2000, "04d")

        if format_type is None:
          data = f"{dayofweek} {year}-{month}-{day} {hour}:{minute}:{second}"
        elif format_type == "file":
          data = f"{year}-{month}-{day}_{hour}-{minute}-{second}"
        else:
          raise ValueError("Formato desconhecido. Use 'default' ou 'file'.")  

        return data
        
    except Exception as e:
      raise Exception(f"Erro ao acessar RTC: {e}")