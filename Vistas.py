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

#%%
class MyGraphCanvas(FigureCanvas):#define la ventana
    def __init__(self, parent= None,width=5, height=4, dpi=100):#configuraciones parte grafica de la ventana
        
        self.__fig = Figure(figsize=(width, height), dpi=dpi);
        self.__axes = self.__fig.add_subplot(111);
        FigureCanvas.__init__(self,self.__fig);
        
#%%
    def set_data(self,data):#referencias de manera global a datos
        global datos;
        datos=data;

#%%
    def grafique(self,datos,min,max):#graficar en campo grafico
        print (datos)
        
        #global datos;#datos son los datos del .mat
        
        self.__axes.clear();#borra 
        self.__axes.set_xlim(min, max);  

        for c in range(datos.shape[0]):
            self.__axes.plot(datos[c,:]+c*10)
        
        #formato del eje de coordenadas
        self.__axes.set_xlabel('Muestras',color="#525a8d",size=6);
        self.__axes.set_ylabel('Voltaje (uV)',color="#525a8d",size=6);        
        self.__axes.set_title('Señal',color="#525a8d",size=10);
        self.__axes.grid();
        #fija los datos en la imagen
        self.__axes.figure.canvas.draw();

#%%        
    def grafique2(self,time, freqs, power):
        #primero se necesita limpiar la grafica anterior
        self.__axes.clear()
        #ingresamos los datos a graficar
        scalogram = self.__axes.contourf(time,
                 freqs[(freqs >= 4) & (freqs <= 40)],
                 power[(freqs >= 4) & (freqs <= 40),:],
                 100, # Especificar 20 divisiones en las escalas de color 
                 extend='both')
        #y lo graficamos
        print("datos")
        #self.__axes.set_ylim(4,40);
        self.__axes.set_ylabel('Frecuencia [Hz]',color="#525a8d",size=6);
        self.__axes.set_xlabel('Tiempo [s]',color="#525a8d",size=6); 
        self.__axes.set_title('Filtrado Wavelet',color="#525a8d",size=10);
        cbar = plt.colorbar(scalogram)
        self.__axes.figure.canvas.draw();#ordenamos que dibuje
        
#%%    
    def grafique3(self,f,Pxx,nivel):
        print("graficando")
        print(f)
        print("pxx")
        print(Pxx)
        self.__axes.clear()#limpia
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
        self.__axes.figure.canvas.draw();
 #%%   
class MyToolbar(NavigationToolbar):#clase barra de herramientas
  def __init__(self, figure_canvas, parent= None):
    self.toolitems = (('Home', 'Home', 'home', 'home'),#inicio
        (None, None, None, None),
        ('Pan', 'Mover imagen', 'move', 'pan'),#mover en tiempo
        ('Zoom', 'Zoom', 'zoom_to_rect', 'zoom'),#zoom grafica
        (None, None, None, None), 
        ('Save', 'Guardar figura', 'filesave', 'save_figure'))#guardar imagen
    NavigationToolbar.__init__(self, figure_canvas, parent= None) 

#%%
class InterfazGrafico(QMainWindow):#hereda de QMainWindow
    def __init__(self):
        super(InterfazGrafico,self).__init__();
        
        loadUi ('Principal.ui',self);#llama al .ui        
        self.setup();      
        self.show();
#%%       
    def SetCoordinador(self, coordinador):#coordina vista y senal
        self.__coordinador=coordinador;
#%%        
    def setup(self):#conficguracion inicial del programa 
        #Grafico 1
        layout = QVBoxLayout();      
        self.campo_grafico.setLayout(layout);   
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=80); 
        #Grafico 2
        layout2 = QVBoxLayout();
        self.campo_grafico_2.setLayout(layout2); 
        self.__sc2 = MyGraphCanvas(self.campo_grafico_2, width=5, height=4, dpi=80); 
        
        #barra ampliar, guardar y mover imagen
        self.navigation_toolbar = MyToolbar(self.__sc, self)
        self.navigation_toolbar.update()
        layout.addWidget(self.navigation_toolbar)
        
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
                

        self.boton_wavelet.setEnabled(False);
        self.boton_welch.setEnabled(False);

        self.combo_opciones.setEnabled(True);
        self.combo_nivel_ventana.setEnabled(False);
        self.combo_tipo_ventana.setEnabled(False);
        self.combo_nivel_super.setEnabled(False);
        
    
#    def Cambiar_estado(self):#cambio de canal
#        global lista;
#        lista=[self.canal1.isChecked(),self.canal2.isChecked(),self.canal3.isChecked(),self.canal4.isChecked(),self.canal5.isChecked(),self.canal6.isChecked(),self.canal7.isChecked(),self.canal8.isChecked()];
#        self.__sc.grafique(lista,self.__x_min, self.__x_max); 

#%%
    def conf(self):
        #Activamos despues de cargar señal
        self.boton_wavelet.setEnabled(True);

        self.boton_welch.setEnabled(True);

        self.combo_nivel_ventana.setEnabled(True);
        self.combo_tipo_ventana.setEnabled(True);
        self.combo_nivel_super.setEnabled(True);
    
        self.__x_min=0;
        self.__x_max=12500;

#%%
    def load_file(self):#carga el archivo .mat
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Todos los archivos (*);;Archivos mat (*.mat)*");
        if archivo_cargado != '':
            print('Archivo cargado con éxito .mat')
            global data;

            data = sio.loadmat(archivo_cargado);
            
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
            
            self.conf();
            self.__coordinador.recibirConjunto_Puntos(senal_continua);#llama al coordinador
            self.__sc.set_data(self.__coordinador.devolverConjunto_Puntos(self.__x_min, self.__x_max));
            self.__sc.grafique(datos,self.__x_min, self.__x_max);#grafica
            self.__x_min=0;
            self.__x_max=1000;
            
#%%                 
    def welch(self):
        print("welch")
        global datos
        nivel=self.combo_nivel_ventana.currentText();
        tipo=self.combo_tipo_ventana.currentText();
        superposicion=self.combo_nivel_super.currentText();
    
        if superposicion=='0%':
            superposicion=0;
            print("0%")
        elif superposicion=='25%':
            superposicion=0.25;
            print("25%")
        elif superposicion=='50%':
            superposicion=0.5;
            print("50%")
        else:
            superposicion=0.75;
            print("75%")
        
        f,Pxx=self.filtrar_welch(datos[0],nivel,tipo,superposicion);#funcion filtrado
        print('Filtrando_welch .mat')
        self.__sc2.grafique3(f,Pxx,nivel);
#%%        
    def filtrar_welch(self,datos,nivel,tipo,superposicion):
        fs = 250
        
        if nivel=='256':
            print("256")
            if tipo=='Hamming':
                f, Pxx = signal.welch(datos,fs,'hamming', 256, 256*(superposicion), 256, scaling='density');#leve
                
        elif nivel=='512':
            print("512")
            if tipo=='Hamming':
                f, Pxx = signal.welch(datos,fs,'hamming', 512, 512*(superposicion), 512, scaling='density');#detallado
        else:
            print("1024")
            if tipo=='Hamming':
                f, Pxx = signal.welch(datos,fs,'hamming', 1024, 1024*(superposicion), 1024, scaling='density');#medio
        return f,Pxx
#%%      
    def wavelet(self):#funcion si esta seleccionado solo un canal se puede hacer el filtrado de lo contrario sale error
        global datos
        tiempo, freq, power = self.calcularWavelet(datos[0])
        self.__sc.grafique2(tiempo, freq, power)
#%%
    def calcularWavelet(self, datos):
        #analisis usando wavelet continuo
        import pywt 
        #fs = 250;
        sampling_period =  1/1000
        Frequency_Band = [4, 30] # Banda de frecuencia a analizar

        # Métodos de obtener las escalas para el Complex Morlet Wavelet  
        # Método 1:
        # Determinar las frecuencias respectivas para una escalas definidas
        scales = np.arange(1, 250)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])] 
        
        N = len(datos)
        print(N)
        #N = datos.shape()
    
        # Obtener el tiempo correspondiente a una epoca de la señal (en segundos)
        time_epoch = sampling_period*N

        # Analizar una epoca de un montaje (con las escalas del método 1)
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
        time = np.arange(0, time_epoch, sampling_period)
        # Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet

        [coef, freqs] = pywt.cwt(datos, scales, 'cmor', sampling_period)
        # Calcular la potencia 
        power = (np.abs(coef)) ** 2
        
        return time, freqs, power
        
