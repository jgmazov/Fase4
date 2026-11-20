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
# Definimos exepciones 


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

        self.__identificador = str(identificador)


    #Creamos el metodo para consultar el identificador
    @property
    def identificador(self):
        return self.__identificador

    #Creamos el metodo astracto, las clases hijas deden implementarlo
    @abstractmethod
    def mostrar_informacion(self):
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
    def mostrar_informacion(self):

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
    def calcular_tarifa(self, duracion):
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

        if self.__estado != "Pending":
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
            if self.__estado != "Pending":
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
            ServicioSala("01", "Room Reservation", 50000),
            ServicioEquipo("02", "Equipment Rental", 15000),
            ServicioAsesoria("03", "Specialized Consulting", 60000)
        ]

        #Incorporamos los servicios a la lista principal.
        self.servicios.extend(servicios_iniciales)

        #Registramos el evento.
        logging.info("Initial services loaded successfully.")


    #Creamos el metodo para registrar el cliente
    def registrar_cliente(self, cliente):

        #Validamos que el objeto recibido sea un cliente.
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("The object received is not a valid client.")

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
        self.ventana.configure(bg="#16A085")
        self.crear_interfaz()

        self.actualizar_listas()

        logging.info("FJ Software Application Launched.")


    #Creamos el metodo de la interfaz grafica principal
    def crear_interfaz(self):

        encabezado = tk.Frame(self.ventana, bg="#0E4D45", height=90)
        encabezado.pack(fill="x")

        tk.Label(encabezado, text="SOFTWARE FJ", font=("Arial", 24, "bold"), fg="white", bg="#0E4D45").pack(pady=(12, 0))

        tk.Label(encabezado, text="Customer, Services, and Reservations Management System", font=("Arial", 11), fg="#DCE6F1", bg="#0E4D45").pack()


        #Crecamos un notebook para organizar la interfaz por pestañas
        self.notebook = ttk.Notebook(self.ventana)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        #Creamos la pestaña de cliente y la incorporamos
        self.tabla_clientes = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tabla_clientes, text="Customers")

        #Creamos la pestaña de servicios y la incorporamos
        self.tabla_servicios = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tabla_servicios, text="Services")

        # Creamos la pestaña de reservas y la incorporamos
        self.tabla_reservas = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tabla_reservas, text="Reservations")

        # Creamos la pestaña de consultas y la incorporamos
        self.tabla_consultas = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tabla_consultas, text="Inquiries")

        #Creamos los metodos que construyen cada pestaña.
        self.crear_tabla_clientes()
        self.crear_tabla_servicios()
        self.crear_tabla_reservas()
        self.crear_tabla_consultas()

        #Creamos el pie de pagina
        pie = tk.Label(self.ventana, text="FJ Software | Management System", bg="#172B4D", fg="white", font=("Arial", 9), pady=8)
        pie.pack(fill="x")


    #Creamos el metodo de la interfaz de registro de clientes
    def crear_tabla_clientes(self):
                
        tk.Label(self.tabla_clientes, text="CUSTOMER REGISTRATION", font=("Arial", 16, "bold"), bg="white", fg="#172B4D").pack(pady=15)

        formulario = tk.Frame(self.tabla_clientes, bg="white")

        formulario.pack(pady=10)

        #Creamos los campos para el resgistro del cliente
        self.ent_id = self.campo(formulario, "Identification:", 0)
        self.ent_nombre = self.campo(formulario, "Full Name:", 1)
        self.ent_correo = self.campo(formulario, "Email:", 2)
        self.ent_telefono = self.campo(formulario, "Phone:", 3)

        tk.Button(formulario,text="Register a Customer",command=self.registrar_cliente,bg="#218838",fg="white",font=("Arial", 10, "bold"),width=22).grid(row=4, column=1, pady=15)

        #Creamos una tabla para mostrar los datos del cliente registrado
        self.lista_clientes = self.crear_tabla(self.tabla_clientes,("ID", "Name", "Email", "Phone"))


    #Creamos el metodo de la interfaz de servicios
    def crear_tabla_servicios(self):

        tk.Label(self.tabla_servicios, text="AVAILABLE SERVICES", font=("Arial", 16, "bold"), bg="white", fg="#172B4D").pack(pady=15)

        #Creamos el contenedor del formulario
        formulario = tk.Frame(self.tabla_servicios, bg="white")
        formulario.pack(pady=10)

        self.ent_serv_id = self.campo(formulario, "Service Code:", 0)
        self.ent_serv_nombre = self.campo(formulario, "Service Name:", 1)
        self.ent_serv_tarifa = self.campo(formulario, "Hourly Rate:", 2)

        tk.Label(formulario, text="Service Type:", bg="white", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=7)
        self.combo_tipo_servicio = ttk.Combobox(formulario, values=["Room", "Equipment", "Consulting"], width=32, state="readonly")
        self.combo_tipo_servicio.grid(row=3, column=1, padx=10, pady=7)

        tk.Button(formulario, text="Register Service", command=self.registrar_servicio, bg="#218838", fg="white", font=("Arial", 10, "bold"), width=20).grid(row=4, column=0, pady=15, padx=5)

        tk.Button(formulario, text="Toggle Availability", command=self.cambiar_estado_servicio, bg="#E67E22", fg="white", font=("Arial", 10, "bold"), width=20).grid(row=4, column=1, pady=15, padx=5)
        
        #Creamos una tabla para mostrar los servicios
        self.lista_servicios = self.crear_tabla(self.tabla_servicios, ("Code", "Service", "Type", "Hourly Rate", "Status"))


    #Creamos el metodo de la interfaz de reservas
    def crear_tabla_reservas(self):

        tk.Label( self.tabla_reservas, text="RESERVATION MANAGEMENT", font=("Arial", 16, "bold"), bg="white", fg="#172B4D").pack(pady=15)

        #Creamos el contenedor del formulario
        formulario = tk.Frame(self.tabla_reservas, bg="white")
        formulario.pack(pady=10)


        tk.Label(formulario, text="Reservation Code:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_reserva = tk.Entry( formulario, width=30)
        self.ent_reserva.grid( row=0, column=1, pady=5)


        tk.Label( formulario, text="Client:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_cliente = ttk.Combobox( formulario, width=28, state="readonly")
        self.combo_cliente.grid( row=1, column=1, pady=5)


        tk.Label( formulario, text="Service:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_servicio = ttk.Combobox( formulario, width=28, state="readonly")
        self.combo_servicio.grid( row=2, column=1, pady=5)

  
        tk.Label( formulario, text="Duration (hours):", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_duracion = tk.Entry( formulario, width=30)
        self.ent_duracion.grid( row=3, column=1, pady=5)

        #Contenedor superior para los 3 botones en el mismo renglón
        frame_botones = tk.Frame(self.tabla_reservas, bg="white")
        frame_botones.pack(fill="x", padx=15, pady=(10, 0))
        
        #Configuramos 3 columnas
        frame_botones.columnconfigure(0, weight=1, uniform="extremos")
        frame_botones.columnconfigure(1, weight=0)
        frame_botones.columnconfigure(2, weight=1, uniform="extremos")

        frame_centro = tk.Frame(frame_botones, bg="white")
        frame_centro.grid(row=0, column=1)

        tk.Button(frame_centro, text="Make a reservation", command=self.crear_reserva, bg="#176B87", fg="white", width=20).pack(side="left", padx=5)

        tk.Button(frame_centro, text="Confirm Reservation", command=self.confirmar_reserva, bg="#218838", fg="white", width=20).pack(side="left", padx=5)

        tk.Button(frame_botones, text="Cancel Reservation", command=self.cancelar_reserva, bg="#C0392B", fg="white", width=20).grid(row=0, column=2, sticky="e")

        #Creamos la tabla de reservas
        self.lista_reservas = self.crear_tabla(self.tabla_reservas, ("Code", "Customer", "Service", "Hours", "Total", "Status"))

        #Contenedor inferior para el botón de actualizar
        frame_inferior = tk.Frame(self.tabla_reservas, bg="white")
        frame_inferior.pack(fill="x", padx=15, pady=(0, 15))

        tk.Button(frame_inferior, text="Update Information", command=self.actualizar_listas, width=20).pack(side="right")

    
    #Creamos el metodo de la interfaz de consultas
    def crear_tabla_consultas(self):

        tk.Label(self.tabla_consultas,text="SYSTEM QUERIES",font=("Arial", 16, "bold"),bg="white",fg="#172B4D").pack(pady=20)

        #Boton para ejecutar las diez pruebas
        tk.Button(self.tabla_consultas, text="Run 10 test operations", command=self.simular_operaciones, bg="#176B87", fg="white", font=("Arial", 11, "bold"), width=35).pack(pady=10)

        #Boton para actualizar las tablas
        tk.Button( self.tabla_consultas, text="Update Queries", command=self.actualizar_listas, width=25).pack(pady=10)

        #Informacion sobre el archivo de registros
        tk.Label(self.tabla_consultas, text="Events and errors are logged in “Softwarefj.log”", bg="white", fg="#555555", font=("Arial", 10)).pack(pady=20)


    #Crecamos el metodo auxiliar para crear campos
    def campo(self, padre, texto, fila):

        # Creamos la etiqueta del campo.
        tk.Label(padre, text=texto, bg="white", font=("Arial", 10)).grid( row=fila, column=0, sticky="w", padx=10, pady=7)
        entrada = tk.Entry( padre, width=35)
        entrada.grid(row=fila, column=1, padx=10, pady=7)

        return entrada


    #Crecamos el metodo auxiliar para crear tablas
    def crear_tabla(self, padre, columnas):

        #Creamos un contenedor para la tabla
        contenedor = tk.Frame(padre, bg="white")
        contenedor.pack(fill="both", expand=True, padx=15, pady=15)

        #Creamos los scroll para el desplazamiento dentro de la tabla
        scroll_y = ttk.Scrollbar(contenedor, orient="vertical")
        scroll_x = ttk.Scrollbar(contenedor, orient="horizontal")

        #Creamos una tabla Treeview
        tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=10, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.config(command=tabla.yview)
        scroll_x.config(command=tabla.xview)

        #Recorremos las columnas recibidas
        for columna in columnas:

            tabla.heading(columna, text=columna)
            tabla.column( columna, width=145, anchor="center")

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        tabla.pack(side="left", fill="both", expand=True)

        return tabla


    #Creamos el metodo para registrar el cliente desde la interfaz
    def registrar_cliente(self):

        #Utilizamos try para controlar posibles errores
        try:

            #Creamos un objeto Cliente con los datos ingresados
            cliente = Cliente(
                self.ent_id.get().strip(),
                self.ent_nombre.get().strip(),
                self.ent_telefono.get().strip(),
                self.ent_correo.get().strip()
            )

            #Enviamos el objeto al sistema principal
            self.sistema.registrar_cliente(cliente)

            #Generamos el mensaje de registro exitoso
            messagebox.showinfo("Registration Successful", "Customer successfully registered.")

            #Limpiamos los campos del formulario
            for entrada in (self.ent_id, self.ent_nombre, self.ent_correo, self.ent_telefono):
                entrada.delete(0, tk.END)

            #Actualizamos la informacion de las tablas
            self.actualizar_listas()

        #Capturamos los errores personalizados del sistema y los registramos
        except ErrorSistema as error:
            logging.exception("Error registering a customer.")
            messagebox.showerror("Validation error", str(error))

        #Capturamos cualquier otro error inesperado y lo registramos
        except Exception as error:
            logging.exception("Unexpected error while registering a customer.")
            messagebox.showerror("Unexpected error", str(error))


    #Creamos el metodo para crear un nuevo servicio
    def registrar_servicio(self):

        #Utilizamos try para controlar posibles errores
        try:
            codigo = self.ent_serv_id.get().strip()
            nombre = self.ent_serv_nombre.get().strip()
            tarifa = float(self.ent_serv_tarifa.get().strip())
            tipo = self.combo_tipo_servicio.get()

            if not tipo:
                raise DatosInvalidosError("Please select a service type.")

            #Creamos la instancia según el tipo seleccionado
            if tipo == "Room":
                nuevo_servicio = ServicioSala(codigo, nombre, tarifa)
            elif tipo == "Equipment":
                nuevo_servicio = ServicioEquipo(codigo, nombre, tarifa)
            else:
                nuevo_servicio = ServicioAsesoria(codigo, nombre, tarifa)

            #Registramos en el sistema
            self.sistema.registrar_servicio(nuevo_servicio)

            messagebox.showinfo("Registration Successful", "Service successfully registered.")

            #Limpiamos los campos
            self.ent_serv_id.delete(0, tk.END)
            self.ent_serv_nombre.delete(0, tk.END)
            self.ent_serv_tarifa.delete(0, tk.END)
            self.combo_tipo_servicio.set("")

            #Actualizamos tablas y listas desplegables
            self.actualizar_listas()

        except ValueError:
            logging.exception("Rate validation error.")
            messagebox.showerror("Validation error", "The hourly rate must be a valid number.")

        except ErrorSistema as error:
            logging.exception("Error creating the new service.")
            messagebox.showerror("Validation error", str(error))

        except Exception as error:
            logging.exception("Unexpected error while registering the service.")
            messagebox.showerror("Unexpected error", str(error))


    #Creamos el metodo para cambiar el estado del servicio
    def cambiar_estado_servicio(self):

        #Utilizamos try para controlar posibles errores
        try:

            #Obtenemos la fila seleccionada en la tabla de servicios
            seleccion = self.lista_servicios.selection()

            if not seleccion:
                raise DatosInvalidosError("Please select a service from the table.")

            #Extraemos el código del servicio
            valores = self.lista_servicios.item(seleccion[0], "values")
            codigo = valores[0]

            #Buscamos el objeto servicio en el sistema
            servicio = self.sistema.buscar_servicio(codigo)

            #Invertimos su estado actual
            nuevo_estado = not servicio.disponible
            servicio.cambio_disponibilidad(nuevo_estado)

            estado_texto = "Available" if nuevo_estado else "Not available"
            messagebox.showinfo("Status Updated", f"Service '{servicio.nombre}' is now: {estado_texto}")

            # Actualizamos la tabla
            self.actualizar_listas()

        except ErrorSistema as error:
            logging.exception("Error changing service availability.")
            messagebox.showerror("Error", str(error))

        except Exception as error:
            logging.exception("Unexpected error changing service availability.")
            messagebox.showerror("Unexpected error", str(error))


    #Creamos el metodo para crear la reserva desde la interfaz
    def crear_reserva(self):

        #Utilizamos try para controlar posibles errores
        try:

            #Obtenemos el codigo de reserva
            codigo = self.ent_reserva.get().strip()

            #Validamos que se haya ingresado un codigo valido
            if not codigo:
                raise DatosInvalidosError("Please enter the reservation code.")

            #Validamos que exista un cliente seleccionado
            if not self.combo_cliente.get():
                raise DatosInvalidosError("Please select a client.")

            #Validamos que exista un servicio seleccionado
            if not self.combo_servicio.get():
                raise DatosInvalidosError("Please select a service.")

            #Convertimos la duracion ingresada a entero
            duracion = int(self.ent_duracion.get())

            #Buscamos el cliente
            cliente = self.sistema.buscar_cliente(self.combo_cliente.get().split(" - ")[0])

            #Buscamos el servicio
            servicio = self.sistema.buscar_servicio(self.combo_servicio.get().split(" - ")[0])

            #Creamos la reserva en el sistema
            reserva = self.sistema.crear_reserva(codigo, cliente, servicio, duracion)

            #Generamos el mensaje de reserva exitosa
            messagebox.showinfo(
                "Reserve Created",
                f"Reservation created successfully.\n\n"
                f"Total including tax: ${reserva.total:,.0f}"
            )

            #Limpiamos los campos utilizados
            self.limpiar_campos_reserva()

            #Actualizamos las tablas
            self.actualizar_listas()

        #Capturamos los errores al convertir la duracion y los registramos
        except ValueError:
            logging.exception("Error during conversion.")
            messagebox.showerror("Incorrect data", "The duration must be a whole number.")

        #Capturamos los errores de excepciones personalizadas y los registramos
        except ErrorSistema as error:
            logging.exception("Error creating the reservation.")
            messagebox.showerror("Booking Error", str(error))

        #Capturamos cualquier otro error inesperado y lo registramos
        except Exception as error:
            logging.exception("Unexpected error while creating a reservation.")
            messagebox.showerror("Unexpected error", str(error))


    def limpiar_campos_reserva(self):
        self.ent_reserva.delete(0, tk.END)
        self.combo_cliente.set("")
        self.combo_servicio.set("")
        self.ent_duracion.delete(0, tk.END)
    
        # Opcional: pone el cursor listo para escribir en el primer campo
        self.ent_reserva.focus()


    #Creamos el metodo para confirmar la reserva
    def confirmar_reserva(self):

        #Utilizamos try para controlar posibles errores
        try:

            #Obtenemos la seleccion de la tabla
            seleccion = self.lista_reservas.selection()

            #Validamos que exista una seleccion
            if not seleccion:
                raise DatosInvalidosError("Please select a reservation.")

            #Obtenemos los datos de la fila seleccionada
            valores = self.lista_reservas.item(seleccion[0], "values")

            #Extraemos el codigo de reserva
            codigo = valores[0]

            #Buscamos el objeto correspondiente
            reserva = self.sistema.buscar_reserva(codigo)

            #Procesamos y confirmamos la reserva
            reserva.procesar()
            messagebox.showinfo("Reservation Confirmed", "The reservation was successfully confirmed.")
            self.actualizar_listas()

        #Capturamos los errores controlados y los registramos
        except ErrorSistema as error:
            logging.exception("Error Confirming Reservation.")
            messagebox.showerror("Error", str(error))

        #Capturamos cualquier otro error inesperado y lo registramos
        except Exception as error:
            logging.exception("Unexpected error while confirming reservation.")
            messagebox.showerror("Unexpected error", str(error))


    #Creamos el metodo para cancelar la reserva
    def cancelar_reserva(self):

        #Utilizamos try para controlar posibles errores
        try:

            #Obtenemos la fila seleccionada
            seleccion = self.lista_reservas.selection()

            #Validamos que exista una reserva seleccionada
            if not seleccion:
                raise DatosInvalidosError("Select a valid reservation.")

            #Obtenemos los datos de la reserva
            valores = self.lista_reservas.item(seleccion[0], "values")

            #Obtenemos el codigo
            codigo = valores[0]

            #Buscamos la reserva
            reserva = self.sistema.buscar_reserva(codigo)

            #Cancelamos la reserva
            reserva.cancelar()
            messagebox.showinfo("Reservation Canceled", "The reservation was successfully canceled.")
            self.actualizar_listas()

        #Capturamos los errores personalizados del sistema y los registramos
        except ErrorSistema as error:
            logging.exception("Error canceling reservation.")
            messagebox.showerror("Error", str(error))

        #Capturamos cualquier otro error inesperado y lo registramos
        except Exception as error:
            logging.exception("Unexpected error while canceling a reservation.")
            messagebox.showerror("Unexpected error", str(error))


    #Creamos el metodo para actualizar las tablas y las listas desplegables
    def actualizar_listas(self):

        #Recorremos todas las tablas
        for tabla in (self.lista_clientes, self.lista_servicios, self.lista_reservas):

            #Eliminamos los registros anteriores
            for elemento in tabla.get_children():
                tabla.delete(elemento)


        #Recorremos los clientes almacenados
        for cliente in self.sistema.clientes:

            #Insertamos cada cliente en la tabla
            self.lista_clientes.insert("",tk.END,values=(cliente.identificador, cliente.nombre, cliente.correo, cliente.telefono))


        #Recorremos los servicios almacenados
        for servicio in self.sistema.servicios:

            estado = ("Available" if servicio.disponible else "Not available")


            if isinstance(servicio, ServicioSala):
                tipo = "Room"
            elif isinstance(servicio, ServicioEquipo):
                tipo = "Equipment"
            elif isinstance(servicio, ServicioAsesoria):
                tipo = "Consulting"
            else:
                tipo = "Another"

            #Insertamos el servicio en la tabla.
            self.lista_servicios.insert("", tk.END, values=( servicio.identificador, servicio.nombre, tipo, f"${servicio.tarifa:,.0f}", estado))


        #Recorremos las reservas almacenadas
        for reserva in self.sistema.reservas:

            #Insertamos cada reserva en la tabla
            self.lista_reservas.insert( "", tk.END, values=(reserva.identificador, reserva.cliente.nombre, reserva.servicio.nombre, reserva.duracion, f"${reserva.total:,.0f}", reserva.estado))

     
        #Construimos una lista con identificacion y nombre, para actualizar la lista desplegable de clientes.
        self.combo_cliente["values"] = [
            f"{c.identificador} - {c.nombre}"
            for c in self.sistema.clientes
        ]


        #Construimos una lista con codigo y nombre, para actualizar la lista desplegable de clientes.
        self.combo_servicio["values"] = [
            f"{s.identificador} - {s.nombre}"
            for s in self.sistema.servicios
        ]


    #Creamos el metodo para realizar la simulación de diez operaciones
    def simular_operaciones(self):

        exitos = 0
        errores = 0


        def ejecutar(nombre, operacion):

            #Utilizamos los contadores
            nonlocal exitos, errores

            try:
                operacion()

            except Exception:
                errores += 1

                #Registramos el error
                logging.exception("Simulation Error: %s", nombre)

            else:
                exitos += 1

                #Registramos la operacion exitosa
                logging.info("Successful simulation: %s", nombre)

            finally:

                #Registramos la finalizacion de la prueba
                logging.info("Simulation completed: %s", nombre)


        def simulacion_1():

            #Creamos un cliente con informacion valida
            cliente = Cliente("1047695969", "Daniela Vélez", "daniela@hotmail.com", "3225697896")
            self.sistema.registrar_cliente(cliente)

        def simulacion_2():

            #Creamos un cliente con informacion valida
            cliente = Cliente("1047478156", "Esteban Ruiz", "esteban@gmail.com", "3101469875")
            self.sistema.registrar_cliente(cliente)

        def simulacion_3():

            #Creamos un cliente con identificacion repetida
            cliente = Cliente("1047695969", "Cliente Duplicado", "duplicado@gmail.com", "3154763215")
            self.sistema.registrar_cliente(cliente)

        def simulacion_4():

            #Intentamos crear un cliente sin el nombre
            Cliente( "1039456975","", "correo@hotmail.com", "3204561297")

        def simulacion_5():

            #Creamos un nuevo servicio de salas
            servicio = ServicioSala("04", "Sala adicional", 50000)
            self.sistema.registrar_servicio(servicio)

        def simulacion_6():

            #Creamos un servicio con el codigo repetido
            servicio = ServicioEquipo("02", "Equipo duplicado", 15000)
            self.sistema.registrar_servicio(servicio)

        def simulacion_7():

            #Buscamos el cliente registrado
            cliente = self.sistema.buscar_cliente("1047695969")

            #Buscamos el servicio de salas
            servicio = self.sistema.buscar_servicio("01")

            #Creamos una reserva por siete horas
            self.sistema.crear_reserva("R001", cliente, servicio, 7)

        def simulacion_8():

            #Buscamos el cliente registrado
            cliente = self.sistema.buscar_cliente("1047695969")

            #Buscamos el servicio
            servicio = self.sistema.buscar_servicio("02")

            #Intentamos crear una reserva con las horas negativas
            self.sistema.crear_reserva("R002", cliente, servicio, -2)

        def simulacion_9():

            #Buscamos la reserva creada
            reserva = self.sistema.buscar_reserva("R001")

            #Confirmamos la reserva
            reserva.confirmar()

        def simulacion_10():

            #Buscamos nuevamente la reserva
            reserva = self.sistema.buscar_reserva("R001")

            #Cancelamos la reserva
            reserva.cancelar()


        operaciones = [

            ("Registro de cliente valido", simulacion_1),
            ("Segundo registro de cliente", simulacion_2),
            ("Registro de cliente duplicado", simulacion_3),
            ("Registro de cliente invalido", simulacion_4),
            ("Registro de servicio valido", simulacion_5),
            ("Registro de servicio duplicado", simulacion_6),
            ("Creacion de reserva valida", simulacion_7),
            ("Creacion de reserva invalida", simulacion_8),
            ("Confirmacion de reserva", simulacion_9),
            ("Cancelacion de reserva", simulacion_10)
        ]

        #Recorremos la lista y ejecutamos cada operacion
        for nombre, operacion in operaciones:
            ejecutar(nombre, operacion)

        #Actualizamos las tablas de la interfaz
        self.actualizar_listas()

        #Generamos el mensaje de la opercaiones realizadas
        messagebox.showinfo(
            "Simulation completed",
            f"10 operations were carried out.\n\n"
            f"Successful Operations: {exitos}\n"
            f"Controlled Error Operations: {errores}\n\n"
            f"The system continues to operate.\n"
            f"Check the software_fj.log file."
        )


#--------------------------------------------------------------------------------------------------------
# Definimos el punto de entrada de la aplicacion
if __name__ == "__main__":


    try:

        ventana = tk.Tk()
        aplicacion = AplicacionSoftwareFJ(ventana)
        ventana.mainloop()


    except Exception as error:
        logging.critical("Critical error while starting the application.", exc_info=True)

        try:

            messagebox.showerror("Critical error", f"It was not possible to start FJ Software:\n{error}")

        except Exception:

            print("Error starting FJ Software:", error)


    finally:

        logging.info("Completion of the FJ Software Application.")


