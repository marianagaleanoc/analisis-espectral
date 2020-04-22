from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5 import QtCore, QtWidgets
from matplotlib.figure import Figure
from PyQt5.uic import loadUi
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import scipy.io as sio
import matplotlib.pyplot as plt;
import numpy as np

from IPython import get_ipython
import scipy.signal as signal;

#%%Definimos la ventana
class MyGraphCanvas(FigureCanvas):
    def __init__(self, parent= None,width=5, height=4, dpi=100):#configuraciones parte grafica de la ventana
        
        self.__fig = Figure(figsize=(width, height), dpi=dpi);
        self.__axes = self.__fig.add_subplot(111);
        FigureCanvas.__init__(self,self.__fig);
        
#%%Referencia de manera global a los dats cargados .mat
    def set_data(self,data):
        global datos;
        datos=data;
        datos = datos - np.mean(datos)#se elimina el efecto del la baja frecuencia, se elimina nivel DC de la señal

#%%
    def grafique(self,datos,min,max):#graficar en campo grafico la señal original
        
        self.__axes.clear();#borra 
        self.__axes.set_xlim(min, max);#acotando eje x

        for c in range(datos.shape[0]):
            self.__axes.plot(datos[c,:]+c*10)
        
        #formato del eje de coordenadas
        self.__axes.set_xlabel('Muestras',color="#525a8d",size=6);
        self.__axes.set_ylabel('Voltaje (uV)',color="#525a8d",size=6);        
        self.__axes.set_title('Señal',color="#525a8d",size=10);
        self.__axes.grid();
        #fija los datos en la imagen
        self.__axes.figure.canvas.draw();

#%%Grafica wavelet continuo
    def grafique2(self,time, freqs, power):
        #se limpia, por si hay alguna grafica anterior
        self.__axes.clear()
        #ingresamos los datos a graficar
        scalogram = self.__axes.contourf(time,
                 freqs[(freqs >= 4) & (freqs <= 40)],
                 power[(freqs >= 4) & (freqs <= 40),:],
                 100, # Especificar 20 divisiones en las escalas de color 
                 extend='both')
        self.__axes.set_ylabel('Frecuencia [Hz]',color="#525a8d",size=6);
        self.__axes.set_xlabel('Tiempo [s]',color="#525a8d",size=6); 
        self.__axes.set_title('Wavelet Continuo',color="#525a8d",size=10);
        cbar = plt.colorbar(scalogram)
        #fija los datos en la imagen
        self.__axes.figure.canvas.draw();
        
#%%Grafica welch
    def grafique3(self,f,Pxx,nivel):
        self.__axes.clear()#limpia
        #dependiendo del nivel de venana graficamos los puntos necesarios
        if nivel=='256':
            self.__axes.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)],'m')
        elif nivel=='512':
            self.__axes.plot(f,Pxx,'m')
        else:
            self.__axes.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)],'m')
        
        self.__axes.grid()
        self.__axes.set_xlabel('x',color="#525a8d",size=6);
        self.__axes.set_ylabel('y',color="#525a8d",size=6); 
        self.__axes.set_title('Filtrado Welch',color="#525a8d",size=10);
        #fija los datos en la imagen
        self.__axes.figure.canvas.draw();
 #%%Barra de herramientas para las dos graficas
class MyToolbar(NavigationToolbar):#clase barra de herramientas
  def __init__(self, figure_canvas, parent= None):
    self.toolitems = (('Home', 'Home', 'home', 'home'),#inicio
        (None, None, None, None),
        ('Pan', 'Mover imagen', 'move', 'pan'),#mover en tiempo
        ('Zoom', 'Zoom', 'zoom_to_rect', 'zoom'),#zoom grafica
        (None, None, None, None), 
        ('Save', 'Guardar figura', 'filesave', 'save_figure'))#guardar imagen
    NavigationToolbar.__init__(self, figure_canvas, parent= None) 

#%%Clase que llama a la ventana .ui
class InterfazGrafico(QMainWindow):#hereda de QMainWindow
    def __init__(self):
        super(InterfazGrafico,self).__init__();
        
        loadUi ('Principal.ui',self);#llama al .ui        
        self.setup();      
        self.show();
#%%llamamos a coordinador
    def SetCoordinador(self, coordinador):#coordina vista y senal
        self.__coordinador=coordinador;
#%%#configuracion inicial del programa
    def setup(self): 
        #Grafico 1
        layout = QVBoxLayout();      
        self.campo_grafico.setLayout(layout);   
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=80); 
        #Grafico 2
        layout2 = QVBoxLayout();
        self.campo_grafico_2.setLayout(layout2); 
        self.__sc2 = MyGraphCanvas(self.campo_grafico_2, width=5, height=4, dpi=80); 
        
        #barra ampliar, guardar y mover imagen, campo 1
        self.navigation_toolbar = MyToolbar(self.__sc, self)
        self.navigation_toolbar.update()
        layout.addWidget(self.navigation_toolbar)
        #barra ampliar, guardar y mover imagen, campo 2
        self.navigation_toolbar = MyToolbar(self.__sc2, self)
        self.navigation_toolbar.update()
        layout2.addWidget(self.navigation_toolbar)
        
        layout.addWidget(self.__sc)       
        layout2.addWidget(self.__sc2)
        
        #conectar botones con funciones, a traves de la accion click
        self.boton_cargar.clicked.connect(self.load_file);
        self.boton_wavelet.clicked.connect(self.wavelet);
        self.boton_welch.clicked.connect(self.welch);
        #combo box y sus opciones
        self.combo_opciones.addItem("Ojos abiertos");
        self.combo_opciones.addItem("Ojos cerrados");
        self.combo_opciones.addItem("Anestesia");
        
        self.combo_nivel_ventana.addItem("1024");
        self.combo_nivel_ventana.addItem("512");
        self.combo_nivel_ventana.addItem("256");
        
        self.combo_tipo_ventana.addItem("Hamming");
        
        self.combo_nivel_super.addItem("0%");
        self.combo_nivel_super.addItem("25%");
        self.combo_nivel_super.addItem("50%");
        self.combo_nivel_super.addItem("75%");
                
        #se desabilitan antes de cargar una señal
        self.boton_wavelet.setEnabled(False);
        self.boton_welch.setEnabled(False);

        self.combo_opciones.setEnabled(True);
        self.combo_nivel_ventana.setEnabled(False);
        self.combo_tipo_ventana.setEnabled(False);
        self.combo_nivel_super.setEnabled(False);
        

#%%se llama esta funcion al cargar una señal
    def conf(self,datos):
        #Activamos despues de cargar señal
        self.boton_wavelet.setEnabled(True);
        self.boton_welch.setEnabled(True);
        self.combo_nivel_ventana.setEnabled(True);
        self.combo_tipo_ventana.setEnabled(True);
        self.combo_nivel_super.setEnabled(True);
    
        self.__x_min=0;
        self.__x_max=len(datos[0]);#grafica el total de los puntos de la señal

#%%#carga el archivo .mat
    def load_file(self):
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Todos los archivos (*);;Archivos mat (*.mat)*");
        if archivo_cargado != '':
            print('Archivo cargado con éxito .mat')
            global data;

            data = sio.loadmat(archivo_cargado);#abrimos archivo
            
            opcion=self.combo_opciones.currentText();
            
            if len(data)!=4:                
                if opcion=='Ojos abiertos':
                    print("ojos_abiertos")
                    data=data["ojos_abiertos"];
                if opcion=='Ojos cerrados':
                    data=data["ojos_cerrados"];
                    print("ojos_cerrados")
                if opcion=='Anestesia':
                    data=data["anestesia"];
                    print("anestesia")
                
                sensores, puntos = data.shape;
                senal_continua = np.reshape(data, (sensores, puntos), order = 'F');
            else:
                data = data["data"]
                sensores, puntos, ensayos = data.shape;
                senal_continua = np.reshape(data, (sensores, puntos*ensayos), order = 'F')
            
            self.conf(data);
            self.__coordinador.recibirConjunto_Puntos(senal_continua);#llama al coordinador
            self.__sc.set_data(self.__coordinador.devolverConjunto_Puntos(self.__x_min, self.__x_max));
            self.__x_min=0;
            self.__x_max=1000;
            self.__sc.grafique(datos,self.__x_min, self.__x_max);#grafica señal original
            
#%%llamado a la funcion filtrar_welch
    def welch(self):
        print("welch")
        global datos
        #coge lo que este seleccionado en los combo box
        nivel=self.combo_nivel_ventana.currentText();
        tipo=self.combo_tipo_ventana.currentText();
        superposicion=self.combo_nivel_super.currentText();
    
        if superposicion=='0%':
            superposicion=0;
        elif superposicion=='25%':
            superposicion=0.25;
        elif superposicion=='50%':
            superposicion=0.5;
        else:
            superposicion=0.75;
        
        f,Pxx=self.filtrar_welch(datos[0],nivel,tipo,superposicion);#funcion filtrado
        print('Filtrando_welch .mat')
        self.__sc2.grafique3(f,Pxx,nivel);#se grafica
#%%Welch, retorna f y Pxx
    def filtrar_welch(self,datos,nivel,tipo,superposicion):
        fs = 250
        
        if nivel=='256':
            if tipo=='Hamming':
                f, Pxx = signal.welch(datos,fs,'hamming', 256, 256*(superposicion), 256, scaling='density');#leve
                
        elif nivel=='512':
            if tipo=='Hamming':
                f, Pxx = signal.welch(datos,fs,'hamming', 512, 512*(superposicion), 512, scaling='density');#detallado
        else:
            if tipo=='Hamming':
                f, Pxx = signal.welch(datos,fs,'hamming', 1024, 1024*(superposicion), 1024, scaling='density');#medio
        return f,Pxx
#%%Llamado a la funcion calcularwavelet
    def wavelet(self):
        global datos
        tiempo, freq, power = self.calcularWavelet(datos[0])
        self.__sc.grafique2(tiempo, freq, power)
#%%Wavelet contunio, retorna tiempo, frecuencia y potencia
    def calcularWavelet(self, datos):
        #analisis usando wavelet continuo
        import pywt 
        fs = 250;
        sampling_period =  1/fs
        Frequency_Band = [4, 30] # Banda de frecuencia a analizar

        # Determinar las frecuencias respectivas para una escalas definidas
        scales = np.arange(1, 250)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])] 
        N = len(datos)    
        # Obtener el tiempo correspondiente a una epoca de la señal (en segundos)
        time_epoch = sampling_period*N
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
        time = np.arange(0, time_epoch, sampling_period)

        [coef, freqs] = pywt.cwt(datos, scales, 'cmor', sampling_period)
        # Calcular la potencia 
        power = (np.abs(coef)) ** 2
        
        return time, freqs, power
        
