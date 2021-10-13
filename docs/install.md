# Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar los paquetes del propio programa (en modo developer)
sudo python setup.py develop

# Instalación de paquetes necesarios
pip install python-decouple
pip3 install sqlalchemy
pip3 install pyqt5
pip3 install mysql-connector-python
pip3 install pandas

# variable de entorno que referencia la raíz del proyecto (para acceder a los módulos)
export PYTHONPATH="${PYTHONPATH}:/home/luis/Documentos/Escritorio/portfolio/apartments"

# encender mysql
sudo systemctl start mysql.service
