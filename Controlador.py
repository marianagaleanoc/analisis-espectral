
class senal(object):
    def __init__(self, data = None):
        if data is not None:
            self.__asignarDatos(data)
        else:
            self.__data = []
            self.__canales = 0
            self.__puntos = 0
            
            
    def asignarDatos(self, data):
        self.__data = data
        self.__canales = data.shape[0]
        self.__puntos = data.shape[1]
        
    def devolver_segmento(self, x_min, x_max):
        if x_min >= x_max:
            return None
        return self.__data[:,x_min:x_max]
    

        
        