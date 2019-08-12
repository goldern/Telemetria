# Aplicativo de Telemetria

Projeto produzido na Framework multiplataforma Kivy utilizando as bibliotecas:
- Dronekit-Python
- OpenCV
- Socket.io
Projeto feito durante o período da Iniciação Científica - bolsista ICB (2018-2019)

Capacidades:
- Obter dados de telemetria de alguns[¹](http://ardupilot.org/copter/docs/common-autopilots.html) modelos de controladores de drones.
- Possibilidade de ter uma visão em tempo real da câmera do drone.
- Possibilidade de selecionar as informações de telemetria desejadas na tela de câmera.
- Possibilidade de mover as informações de telemetria pela tela de câmera.
- Servidor com suporte a múltiplos clientes, capaz de projetar a imagem do aplicativo principal em mais de um dispositivo compatível.

# Tutorial:

Primeiro é necessário ter o Python instalado(preferência pela versão [2.7.15](https://www.python.org/downloads/release/python-2715/)), depois disso, são necessárias algumas bibliotecas no Python, que podem ser importadas usando o Prompt de Comando(Windows) ou o Terminal(Linux e Mac)
* Dronekit: `pip install dronekit`
* OpenCV: `pip install opencv-python`
* Serial: `pip install pyserial`

Opcional:
* Dronekit SITL(simulador): `pip install dronekit-sitl`

Após a instalação das bibliotecas, é necessário apenas navegar até a pasta do projeto no Terminal/Prompt de Comando e utilizar o comando:
`python main.py`
