grupo_radio=15
tick=125 #ms
pausa_derecho=tick*4
pausa_giro=tick*2
pausa_actual=0
Vmax=255
mismoSentido=False
reposoInhibido=True
recibir_texto_claro=True
traccion_izq=robotbit.Motors.M1A
traccion_der=robotbit.Motors.M2B

class comandosClase():
    def __init__(self,texto_claro):
        self.cola=[] #self.borrar_cola()
        self.ultimo_comando=""
        self.texto_claro=texto_claro
        self.comandos_validos=["izquierda","derecha","adelante","atrás"] #los primeros 4 son para mover_motores(), en "texto claro"
        self.comienza=len(self.comandos_validos) #comentar
        self.comandos_validos=self.comandos_validos+["zqr", "drc", "dln", "trs"] #los segunos 4 son el código SECRETO correspondiente a los primeros 4
        self.ultimo_comando="reposo" #ojo, esto es ultimo_comando "recibido"
        self.comandos_validos.append(str(self.ultimo_comando)) #el último elemento de comandos_validos siemrpe es para reposo


    def desencriptar(self,comando):
        desencriptado=False
        # for indice in range(self.comienza,len(self.comandos_validos)):
        #                         if self.comandos_validos[indice]==comando:
        #                             comando=self.comandos_validos[indice-self.comienza]
        #                             desencriptado=True
        for indice in range(self.comienza,len(self.comandos_validos)): #el ultimo es reposo y NO va encriptado
            #if indice >= self.comienza and self.comandos_validos[indice]==comando:
            if self.comandos_validos[indice]==comando:
                comando=self.comandos_validos[indice-self.comienza]
                desencriptado=True
        return comando #no puedo dvolver tupla... 

    def encriptar(self,comando:str):
        #resultado=comando
        resultado=""
        indice=0
        while len(resultado)<3 and indice<len(comando):
            letra=comando[indice]
            if letra not in ["a","e","i","o","u","á"]:
                resultado+=letra
            indice+=1
        return resultado

    def borrar_cola(self):
        self.cola=[]

    def procesar(self):
        if len(self.cola) > 0:
            desencriptado=False
            modo_ráfaga=False
            #inhibir botones - no hace falta
            comando=self.cola[0]
            if len(self.cola) > 1 and comando==self.cola[1]:
                modo_ráfaga=True
            else:
                modo_ráfaga=False
            self.cola=self.cola[1:]
            #activar botones - no hace falta
            comando_en_claro=comando in self.comandos_validos[:self.comienza]
            if comando_en_claro and self.texto_claro:
                desencriptado=True
            elif comando in self.comandos_validos[self.comienza:-1]:
                #desencripto
                comando=self.desencriptar(comando)
                if comando in self.comandos_validos[:self.comienza]:
                    desencriptado=True
                else:
                    desencriptado=False
            else:
                print(",comandos.procesar()->ErrorNoExisteComando:"+comando)
            if desencriptado:
                if modo_ráfaga:
                    pass
                    #if comando not in ["izquierda","derecha"]: #los giros deben repetirse
                    #    print(",comandos.procesar()->CmdRepetido:"+comando)
                else:
                    #self.ultimo_comando == comando #mismo error que en Máquina de Voto Electrónico
                    self.ultimo_comando = comando
                    print(",comandos.procesar()->CmdNuevo:"+comando)
                mover_motores(comando,modo_ráfaga)
            else:
                print(",comandos.procesar()->ErrorDesencriptar:"+comando)
        else:
            print(",comandos.procesar()->ErrorColaVacia")
            



def on_received_string(comando):
    print("on_received_string()->"+comando)
    comandos.cola.append(comando)

def enviar_por_radio(comando):
    radio.send_string(comando)


def reposo():
    global pausa_actual
    #basic.show_icon(IconNames.DIAMOND)
    #robotbit.motor_run(traccion_izq, 0)
    #robotbit.motor_run(traccion_der, 0)
    robotbit.motor_stop_all()
    comandos.borrar_cola()
    comando="reposo"
    print(","+comando)
    comandos.ultimo_comando=comando
    pausa_actual=0
    mostrarModo()
    

def mover_motores(comando:str, modo_ráfaga:bool):
    global pausa_actual
    comando_válido=True
    pausa=0
    if comando=="izquierda":
        basic.show_arrow(ArrowNames.NORTH_WEST)
        robotbit.motor_run_dual(traccion_izq, Vmax,
                                traccion_der, Vmax)
        pausa=pausa_giro
    elif comando=="derecha":
        basic.show_arrow(ArrowNames.NORTH_EAST)
        robotbit.motor_run_dual(traccion_izq, -Vmax,
                                    traccion_der, -Vmax)
        pausa=pausa_giro
    elif comando=="adelante":
        basic.show_arrow(ArrowNames.NORTH)
        robotbit.motor_run_dual(traccion_izq, Vmax,
                                        traccion_der, -Vmax)
        pausa=pausa_derecho
    elif comando=="atrás":
        basic.show_arrow(ArrowNames.SOUTH)
        robotbit.motor_run_dual(traccion_izq, -Vmax,
                                        traccion_der, Vmax)
        pausa=pausa_derecho
    else:
        print(",mover_motores():ErrorNoExisteComando:"+comando)
        comando_válido=False
    pausa_actual=+pausa

def mostrarModo():
    if mismoSentido:
            basic.show_leds("""
            . . . # .
            . . # # #
            . . . . .
            # # # . .
            . # . . .
            """)
    else:
            basic.show_leds("""
            . . . . .
            . # . # .
            # # . # #
            . # . # .
            . . . . .
            """)




def cambiarModo():
    global mismoSentido
    mismoSentido=not(mismoSentido)
    mostrarModo()

def interfaz_de_usuario_a():  #atrás o izquierda
    if mismoSentido: #atrás
        indice=3
    else: #izquierda
        indice=0
    comando=comandos.comandos_validos[indice]
    if not comandos.texto_claro:
            #TODO: pasar a enviar_por_radio()
            #indice+=comandos.comienza #version encriptada
            #comando=comandos.comandos_validos[indice]
            comando=comandos.encriptar(comando)
    print(",botonA()->"+comando)
    comandos.cola.append(comando)
    enviar_por_radio(comando)
    pass


def interfaz_de_usuario_b():  #adelant o derecha
    if mismoSentido: #adelante
        indice=2
    else: #derecha
        indice=1
    comando=comandos.comandos_validos[indice]
    if not comandos.texto_claro:
        #TODO: pasar a enviar_por_radio()
        #indice+=comandos.comienza #version encriptada
        #comando=comandos.comandos_validos[indice]
        comando=comandos.encriptar(comando)
    print(",botonB()->"+comando)
    comandos.cola.append(comando)
    enviar_por_radio(comando)
    pass



def on_button_pressed_b_pruebas():
    comando=comandos.comandos_validos[0] #es "izquierda" en claro
    print(",botonB()->"+comando)
    comandos.cola.append(comando)
    pass


def interfaz_de_usuario_texto_claro():
    global recibir_texto_claro
    global comandos
    recibir_texto_claro=not(recibir_texto_claro)
    comandos.texto_claro=recibir_texto_claro
    if recibir_texto_claro:
        basic.show_icon(IconNames.YES)
    else:
        basic.show_icon(IconNames.NO)


def onEvery_interval():
    global comandos,tick,pausa_actual
    if pins.digital_read_pin(DigitalPin.P0):
        interfaz_de_usuario_texto_claro() #aceptar texto_claro o no (encriptado siempre acepta)

    pausa_actual=max(pausa_actual-tick,0)
    if pausa_actual<tick and comandos.ultimo_comando != "reposo":
        reposo()

    if len(comandos.cola)>0:
        if "reposo" in comandos.cola:
            reposo()
        else:
            comandos.procesar()
#elif comandos.ultimo_comando != "reposo":
#    reposo()

def interfaz_de_usuario_reposo():
    #comandos.cola.push("reposo")
    #onEvery_interval()
    reposo()
    enviar_por_radio("reposo")

comandos=comandosClase(texto_claro=recibir_texto_claro)
loops.every_interval(tick, onEvery_interval)
radio.on_received_string(on_received_string)
input.on_button_pressed(Button.A, interfaz_de_usuario_a)
input.on_button_pressed(Button.B, interfaz_de_usuario_b)
input.on_button_pressed(Button.AB, interfaz_de_usuario_reposo)
input.on_logo_event(TouchButtonEvent.PRESSED, cambiarModo) #reposo

cambiarModo()
radio.set_group(grupo_radio)

