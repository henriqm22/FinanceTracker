import os
import sys

print("Diretório atual:", os.getcwd())
print("Caminho do script:", os.path.dirname(os.path.abspath(__file__)))

# Verificar se a pasta data existe
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
print("Caminho da pasta data:", data_path)
print("Pasta data existe?", os.path.exists(data_path))

from ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()