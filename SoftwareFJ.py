# importamos la librería y le colocamos un alias 
import tkinter as tk
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
from tkinter import simpledialog
from datetime import datetime
from abc import ABC, abstractmethod
import logging
import traceback



#--------------------------------------------------------------------------------------------------------
# Definimos el sistema de logs


#Archivo donde se guardan los resgitros Softwarefj.log
#INFO permite resgitrar los fallos
#Configuramos utf-8 para que se admitan caracteres especiales
logging.basicConfig(
    filename="Softwarefj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
    )


#--------------------------------------------------------------------------------------------------------
# Definimos excapciones 


class ErrorSistema(Exception):
    pass


class DatosInvalidosError(ErrorSistema):
    pass


class ClienteDuplicadoError(ErrorSistema):
    pass


class ServicioNoDisponibleError(ErrorSistema):
    pass


class ReservaError(ErrorSistema):
    pass


class OperacionNoPermitidaError(ErrorSistema):
    pass



#--------------------------------------------------------------------------------------------------------
# Definimos la clase abstracta entidad
class Entidad(ABC):

    #Creamos el constructor para la clase
    def __init__(self, identificador):

        if not identificador:
            raise DatosInvalidosError("Identification is required")

        self.__identficador = str(identificador)


    #Creamos el metodo para consultar el identificador
    @property
    def identificador(self):
        return self.__identificador

    #Creamos el metodo astracto, las clases hijas deden implementarlo
    @abstractmethod
    def mostrar_información(self):
        pass    


#--------------------------------------------------------------------------------------------------------
# Definimos la clase cliente
class Cliente(Entidad):

    #Creamos el constructor para la clase
    def __init__(self, identificacion, nombre, telefono, correo):

        super().__init__(identificacion)

        #Validamos que el nombre no este vacio
        if not nombre.strip():
            raise DatosInvalidosError("The customer's name is required")

        #Validamos que el correo tenga una estructura valida
        if "@" not in correo or "." not in correo:
            raise DatosInvalidosError("The email address is invalid.")

        #Validamos que el telefono solo tenga números y mas de 7 caracteres
        if not telefono.isdigit() or len(telefono) <7:
            raise DatosInvalidosError("The phone number must be at least 7 digits long.")


        #Guardamos los datos
        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = telefono.strip()


    #Creamos el metodo para consultar el nombre
    @property
    def nombre(self):
        return self.__nombre

    #Creamos el metodo para consultar el correo
    @property
    def correo(self):
        return self.__correo

    #Creamos el metodo para consultar el telefono
    @property
    def telefono(self):
        return self.__telefono


    #Se sobrescribe el metodo de la clase Entidad y devuelve la información del cliente
    def mostrar_información(self):

        return (
            f"Identification: {self.identificador} | "
            f"Name: {self.nombre} | "
            f"Email: {self.correo} | "
            f"Phone: {self.telefono}"
            )


#--------------------------------------------------------------------------------------------------------
# Definimos la clase abstracta servicio
class Servicio(Entidad, ABC):

    def __init__(self, identificador, nombre, tarifa):

        super().__init__(identificador)

        #Validamos que el nombre del servicio no este vacio
        if not nombre.strip():
            raise DatosInvalidosError("Service is mandatory")

        #Validamos que la tarifa sea mayor que 0
        if tarifa <=0:
            raise DatosInvalidosError("The rate must be greater than 0")


        #Guardamos los datos
        self.__nombre = nombre
        self.__tarifa = float(tarifa)
        self.__disponible = True


    #Creamos el metodo para consultar el nombre del servicio
    @property
    def nombre(self):
        return self.__nombre

    #Creamos el metodo para consultar la tarifa
    @property
    def tarifa(self):
        return self.__tarifa

    #Creamos el metodo para consultar la dispobilidad
    @property
    def disponible(self):
        return self.__disponible

    #Creamos el metodo para modificar la disponibilidad
    def cambio_disponibilidad(self, estado):

        if not isinstance(estado, bool):
            raise DatosInvalidosError("The statement must be either false or true")

        self.__disponible = estado


    #Creamos el metodo para calcular algunos paraemetros opcionales
    def calcular_costo( self, duracion, impuesto=0, descuento=0):

        if duracion <= 0:
            raise DatosInvalidosError("The dwell time must be greater than 0")

        if not 0 <= impuesto <= 1:
            raise DatosInvalidosError("The tax calculated must be between 0 and 1")

        if not 0 <= descuento <= 1:
            raise DatosInvalidosError("The discount calculated must be between 0 and 1")

        subtotal = self.calcular_tarifa(duracion)

        total = subtotal * (1 - descuento)

        total = total * (1 + impuesto)

        return round(total, 2)


    #Creamos el metodo abstracto para calcular la tarifa
    @abstractmethod
    def calcular_tarifa(self, duración):
        pass

    #Creamos el metodo abstracto para la descripción del servicio
    @abstractmethod
    def describir_servicio(self):
        pass

    #Creamos el metodo para validar el tiempo de duración
    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    def mostrar_informacion(self):
        return (
            f"{self.identificador} - {self.nombre} "
            f"- Tarifa: ${self.tarifa:,.0f}"
        )

#--------------------------------------------------------------------------------------------------------
# Definimos la clase del servicio de alquiler de salas
class ServicioSala(Servicio):

    def calcular_tarifa(self, duracion):
        self.validar_parametros(duracion)
        return self.tarifa * duracion


    def validar_parametros(self, duracion):
        if duracion > 24:
            raise DatosInvalidosError("A room reservation cannot exceed 24 hours.")

    # Describimos el servicio.
    def describir_servicio(self):
        return "Room Reservations by the Hour."


#--------------------------------------------------------------------------------------------------------
# Definimos la clase del servicio de alquiler de equipos
class ServicioEquipo(Servicio):

    def calcular_tarifa(self, duracion):
        self.validar_parametros(duracion)
        return self.tarifa * duracion

    def validar_parametros(self, duracion):
        if duracion > 24:
            raise DatosInvalidosError("The equipment rental may not exceed 24 hours.")

    # Describimos el servicio.
    def describir_servicio(self):

        return "Technology Equipment Rental."


#--------------------------------------------------------------------------------------------------------
# Definimos la clase del servicio de asesorias especializadas
class ServicioAsesoria(Servicio):

    def calcular_tarifa(self, duracion):
        self.validar_parametros(duracion)
        return self.tarifa * duracion

    def validar_parametros(self, duracion):
        if duracion > 8:
            raise DatosInvalidosError("Consulting services may not exceed 8 hours.")

    def describir_servicio(self):

        return "Specialized Consulting Services by the Hour."


#--------------------------------------------------------------------------------------------------------
# Definimos la clase de reserva
class Reserva(Entidad):

    #Creamos el constructor para la clase
    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        #Realizamos la validación que el objeto recibido sea un cliente.
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("Please select a valid client.")

        #Realizamos la validación que el objeto recibido sea un servicio.
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Please select a valid service.")

        #Realizamos la comprobación la disponibilidad del servicio.
        if not servicio.disponible:
            raise ServicioNoDisponibleError("The selected service is not available.")

        #Realizamos la validación que la duracion sea mayor que 0.
        if duracion <= 0:
            raise DatosInvalidosError("The duration must be greater than 0.")

        #Ejecutamos las validaciones propias del servicio.
        servicio.validar_parametros(duracion)

        #Guardamos el cliente asociado a la reserva.
        self.__cliente = cliente

        #Guardamos el servicio seleccionado.
        self.__servicio = servicio

        #Guardamos la duracion de la reserva.
        self.__duracion = duracion

        #Establecemos el estado inicial.
        self.__estado = "Pending"

        #Registramos la fecha y hora de creacion.
        self.__fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        #Calculamos el costo incluyendo el impuesto del 19%.
        self.__total = servicio.calcular_costo(duracion, impuesto=0.19)

    #Propiedad para consultar el cliente.
    @property
    def cliente(self):
        return self.__cliente

    #Propiedad para consultar el servicio.
    @property
    def servicio(self):
        return self.__servicio

    #Propiedad para consultar la duracion.
    @property
    def duracion(self):
        return self.__duracion

    #Propiedad para consultar el estado.
    @property
    def estado(self):
        return self.__estado

    #Propiedad para consultar el total.
    @property
    def total(self):
        return self.__total


    #Creamos el metodo para confirmar una reserva
    def confirmar(self):

        if self.__estado != "Pendiente":
            raise OperacionNoPermitidaError("Only reservations with a “pending” status can be confirmed..")

        #Actualizamos el estado de la reserva.
        self.__estado = "Confirmed"

        #Registramos el evento en el archivo de logs.
        logging.info(
            "Reservation %s Confirmed.", self.identificador)


    #Creamos el metodo para confirmar una reserva
    def cancelar(self):

        #Evitamos cancelar una reserva que ya esta cancelada.
        if self.__estado == "Canceled":
            raise OperacionNoPermitidaError("This reservation has already been canceled.")

        #Actualizamos el estado de la reserva.
        self.__estado = "Canceled"

        #Registramos el evento en el archivo de logs.
        logging.info("Reservation %s canceled.", self.identificador)


    #Creamos el metodo para procesar la reserva
    def procesar(self):

        try:
            if self.__estado != "Pendiente":
                raise ReservaError("The reservation listed is not pending.")

            self.confirmar()

        #Capturamos los errores relacionados con reservas.
        except ReservaError as error:

            #Guardamos el error en el archivo de logs.
            logging.exception("Error processing the reservation.")

            raise ErrorSistema("We were unable to process the reservation.") from error

        finally:
            logging.info("The reservation is now complete %s.",self.identificador)


    #Creamos el metodo para mostrar la información y sobrescribimos el metodo abstracto de Entidad
    def mostrar_informacion(self):

        return (
            f"Reserva: {self.identificador} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duracion: {self.duracion} horas | "
            f"Total: ${self.total:,.0f} | "
            f"Estado: {self.estado} | "
            f"Fecha: {self.__fecha}"
        )


#--------------------------------------------------------------------------------------------------------
# Definimos la clase principal del Sistema Software
class SistemaSoftwareFJ:

    #Creamos el constructor para la clase
    def __init__(self):

        self.clientes = []
        self.servicios = []
        self.reservas = []
        self.cargar_servicios()

    #Creamos el metodo para cargar los servicios y su costo
    def cargar_servicios(self):

        servicios_iniciales = [
            ServicioSala("01", "Reserva de sala", 50000),
            ServicioEquipo("02", "Alquiler de equipos", 15000),
            ServicioAsesoria("03", "Asesoria especializada", 60000)
        ]

        #Incorporamos los servicios a la lista principal.
        self.servicios.extend(servicios_iniciales)

        #Registramos el evento.
        logging.info("Initial services loaded successfully.")


    #Creamos el metodo para registrar el cliente
    def registrar_cliente(self, cliente):

        #Validamos que el objeto recibido sea un cliente.
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto recibido no es un cliente valido.")

        for existente in self.clientes:

            if existente.identificador == cliente.identificador:
                raise ClienteDuplicadoError("There is already a customer registered with that ID..")

        #Agregamos el cliente cunado todo esta correcto
        self.clientes.append(cliente)

        logging.info("Registered Customer: %s", cliente.nombre)

        return True


    #Creamos el metodo para registrar el cliente
    def registrar_servicio(self, servicio):

        #Validamos que el servicio sea valido.
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("The service you entered is invalid.")

        for existente in self.servicios:

            if existente.identificador == servicio.identificador:
                raise ErrorSistema("A service with that code already exists.")

        #Agregamos el nuevo servicio a la lista      
        self.servicios.append(servicio)

        logging.info("Registered service: %s", servicio.nombre)

        return True


    #Creamos el metodo para registrar el cliente
    def crear_reserva(self, identificador, cliente, servicio, duracion):

        #Validamos que el codigo de reserva no exista.
        for reserva in self.reservas:

            if reserva.identificador == identificador:
                raise ReservaError("The reservation code already exists.")

        # Creamos el objeto Reserva.
        reserva = Reserva(identificador, cliente, servicio, duracion)

        # Agregamos la reserva a la lista.
        self.reservas.append(reserva)

        # Registramos la creacion de la reserva.
        logging.info("Reservation %s created correctly.", identificador)

        return reserva


    #Creamos el metodo para registrar buscar el cliente
    def buscar_cliente(self, identificacion):

        # Recorremos la lista de clientes.
        for cliente in self.clientes:

            if cliente.identificador == identificacion:
                return cliente

        raise ErrorSistema("The correct customer was not found.")


    #Creamos el metodo para registrar buscar el servicio
    def buscar_servicio(self, identificador):

        for servicio in self.servicios:

            if servicio.identificador == identificador:
                return servicio

        raise ErrorSistema("The specified service was not found.")


    #Creamos el metodo para registrar buscar el cliente
    def buscar_reserva(self, identificador):

        for reserva in self.reservas:

            if reserva.identificador == identificador:
                return reserva

        raise ErrorSistema("The specified reservation could not be found.")


#--------------------------------------------------------------------------------------------------------
# Definimos la clase de la interfaz grafica
class AplicacionSoftwareFJ:

    #Creamos el constructor para la clase
    def __init__(self, ventana):

        self.sistema = SistemaSoftwareFJ()
        self.ventana = ventana

        self.ventana.title("SOFTWARE FJ")
        self.ventana.geometry("1100x700")
        self.ventana.minsize(950, 600)
        self.ventana.configure(bg="#1F63B5")
        self.crear_interfaz()

        self.actualizar_listas()

        logging.info("FJ Software Application Launched.")

