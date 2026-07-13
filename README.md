# 🚀 i2c-daqmx-bitbang

Un script în Python pentru emularea protocolului **I2C prin Bit-Banging** folosind pinii de Digital I/O ai unei plăci de achiziție de date **National Instruments NI USB-6008** (via driverul `nidaqmx`).

> ⚠️ **Notă:** Proiectul este în stadiu de dezvoltare (netestat pe hardware real). Implementează logica I2C complet software, optimizată pentru a reduce latența pe magistrala USB.

---

## 🛠️ Structura Proiectului

Proiectul este complet modularizat, separând logica de bit-banging de driverele senzorilor:

*   `bitbang_i2c.py`: Nucleul proiectului. Gestionează task-urile NI-DAQmx și controlează pinii SCL/SDA într-un mod eficient.
*   `bmp280.py`: Driver pentru senzorul de presiune și temperatură Bosch BMP280.
*   `htu21d.py`: Driver pentru senzorul de umiditate și temperatură HTU21D (include validare CRC8).
*   `main.py`: Scriptul principal care instanțiază conexiunea și citește datele în buclă.

---

## 📐 Schema de Conexiune (Hardware Setup)

Deoarece NI USB-6008 nu are pini Open-Drain nativi și nici rezistențe de pull-up interne pe liniile digitale, **trebuie neapărat** să adaugi rezistențe de pull-up externe (recomandat $4.7\text{ k}\Omega$) către linia de $3.3\text{V}$ sau $5\text{V}$ a senzorilor.

| Funcție I2C | Pin NI USB-6008 (Configurație Standard) | Conexiune Hardware |
| :--- | :--- | :--- |
| **SCL** (Clock) | `Dev1/port0/line0` | Rezistență $4.7\text{ k}\Omega$ la VCC + Pin SCL Senzori |
| **SDA** (Data) | `Dev1/port0/line1` | Rezistență $4.7\text{ k}\Omega$ la VCC + Pin SDA Senzori |
| **GND** | `GND` (Oricare pin de masă digitală) | GND Senzori |

---

## 🚀 Instalare și Rulare

### 1. Prerechizite
Sistemul gazdă trebuie să aibă instalat driverul oficial **NI-DAQmx Run-Time** sau Full Driver de la National Instruments.

### 2. Clonarea și configurarea mediului
```bash
# Clonează repository-ul
git clone https://github.com
cd i2c-daqmx-bitbang

# Instalează wrapper-ul de Python pentru NI-DAQmx
pip install nidaqmx
```

### 3. Execuția
Modifică pinii în `main.py` dacă folosești alt port, apoi rulează:
```bash
python main.py
```

---

## ⚙️ Detalii de Implementare Tehnică (Optimizare Latență)

*   **Evitarea Driver Overhead:** Versiunile inițiale apelau `.start()` și `.stop()` pe task-urile DAQmx la fiecare bit trimis, provocând o latență catastrofală din cauza tranzacțiilor USB repetitive. 
*   **Persistent Tasks:** În implementarea curentă, ambele task-uri (`write_task` și `read_task`) sunt pornite o singură dată la inițializarea clasei `DigitalPin` și sunt distruse abia la finalizarea scriptului prin metoda `.close()`.
*   **Pseudo Open-Drain:** Emularea stării `High` pe magistrală se face prin scrierea valorii logice `1`, permițând rezistenței de pull-up externe să ridice linia. Starea `Low` este forțată activ prin scrierea valorii `0`.

---

## 📋 Stadiu Features & TODO

- [x] Clasă abstractă optimizată pentru control digital pin (fără reinstanțiere de task-uri).
- [x] Driver software I2C (Start, Stop, Read Byte, Write Byte, ACK/NACK handling).
- [x] Driver senzor BMP280 cu compensare pe 16/32 biți pentru temperatură.
- [x] Driver senzor HTU21D cu calcul de checksum CRC.
- [ ] **Testare pe hardware real și calibrare delay ($1\text{ ms}$).**
