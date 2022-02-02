
from PyQt5.QtWidgets import QApplication

import sys

from app.window import MainWindow


    



if __name__ == "__main__" :
    
  # create pyqt5 app
  App = QApplication(sys.argv)
  
  # create the instance of our Window
  window = MainWindow()
  window.show()
  # start the app
  sys.exit(App.exec())

  