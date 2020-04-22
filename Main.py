import sys
from PyQt5.QtWidgets import QApplication
from Controlador import senal
from Vistas import InterfazGrafico

#Desde aqui se corre el codigo para que exista comunicacion entre vistas y el controlador
class Coordinador(object):
 
    def __init__(self, vista, senal):
        self.__mi_vista = vista
        self.__mi_senal = senal
    
    def recibirConjunto_Puntos(self, data):
        self.__mi_senal.asignarDatos(data)
    def devolverConjunto_Puntos(self, x_min, x_max):
        return self.__mi_senal.devolver_segmento(x_min, x_max)
    

class Principal(object):
    def __init__(self):
        self.__app=QApplication(sys.argv)
        self.__mi_vista=InterfazGrafico()
        self.__mi_senal=senal()
        self.__mi_controlador=Coordinador(self.__mi_vista, self.__mi_senal)
        self.__mi_vista.SetCoordinador(self.__mi_controlador)
        
    def main(self):
        self.__mi_vista.show()
        sys.exit(self.__app.exec_())

p=Principal()
p.main() 
        
    

        
        