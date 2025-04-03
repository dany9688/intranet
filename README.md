# Intranet Moron



## Comenzando

El sistema se encuentra dockerizado con tres imagenes: una de python, una de redis y otra de la base de datos postgres.

Todo esto se encuentra en un docker compose con sus respectivos volúmenes.

## Instalaciones previas

Para que funciones se debe tener instalado  [Docker](https://www.docker.com/) en la pc para poder montar los containers necesarios.

- [ ] Clonar el proyecto con git clone https://github.com/dany9688/intranet.git
- [ ] Posicionarse dentro la carpeta del proyecto y abrir una terminal de sistema (CMD)
- [ ] Correr el comando "docker-compose up --build"
- [ ] Una vez finalizado la carga de las imagenes abrir una nueva ventana de la terminal
- [ ] Dentro de la carpeta del proyecto correr el "comando docker ps" a fin de ver los containers que se están ejecutando. Debemos centrarnos en alguno que diga "intranet"
- [ ] Una vez ubicado el nombre del container corremos el comando "docker exec -it 'nombre del container' /bin/sh"
- [ ] Esto nos va a ubicar dentro del container en la carpeta "/usr/scr/planilla" en donde podremos trabajar con el proyecto.
- [ ] A fin de migrar todas las tablas de la base de datos del container al volumen local vamos a correr el comando "python3 manage.py migrate"
- [ ] Una vez finalizada la migración vamos a crear un super usuario con el comando "python3 manage.py createsuperuser". Los datos del mismo son locales, por lo que se puede elegir cualquiera.
- [ ] Ingresar en el navegador "localhost:8000/admin" y ya deberíamos poder loguearnos con el usuario creado anteriormente.

## Orden de carga de datos

Lo ideal es cargar la base de datos con los siguientes datos y de la siguiente forma a fin de no tener problemas.

- ### Bases
-    Cuartel Central
-    Destacamento N°1
-    Destacamento N°2

- ### Cuarteles
-    Mariano Acosta
-	José C. Paz
-	Ituzaingo
-	Tortuguitas
-	Morón
-	Hurlingham
-	Villa Ballester
-	3 de Febrero
-	Merlo
-	Moreno
-	General Sarmiento
-	San Isidro
-	Matanza
-	VIcente López
-	General San Martín

- ### Jerarquías
-    Comandante General
-	Comandante Mayor
-	Comandante
-	Subcomandante
-	Oficial Auxiliar de Dotación
-	Oficial Auxiliar de Escuadra
-	Oficial Auxiliar
-	Ayudante Mayor
-	Ayudante Principal
-	Ayudante de 1ra
-	Ayudante
-	Subayudante
-	Bombero

- ### Tipos de movil
-    En servicio
-    Condicional
-    Fuera de servicio
-    Ocupado

- ### Tipos de movil
-    Hidroelevador
-	Cascada
-	Transporte de personal
-	Comando
-	Cisterna
-	Primera dotación

- ### Tipos de servicios
-    Técnico
-	Comando
-	Suministro de agua
-	Materiales Peligrosos
-	Forestal
-	Colaboración
-	Auxilio
-	Incendio

- ### Móviles
-   Móvil 1
-   Móvil 2
-   Móvil 3
-   Móvil 4
-   Móvil 5
-   Móvil 6
-   Móvil 7
-   Móvil 8

- ### Bomberos
**Asignarle cualquier jerarquía y demás opciones. Por lo menos uno debe ser OFicial**
-   Tito Puente
-   Homero Simpson
-   Ned Flanders
-   Apu Nahasapeemapetilon
-   Moe Szyslak

- ### Tipo de motores
-    Eléctrico 220v
-    Eléctrico 19v
-    Combustión 2T
-    Combustión 4T

- ### Tipo de materiales
-    Manga
-    Corte
-    Acople

- ### Ubicaciones
-    Sección materiales - Cuartel Central
-    Sección materiales - Destacamento N°1
-    Sección materiales - Destacamento N°2

- ### Grupos
-    Cuartel Central
-    Destacamento N°1
-    Destacamento N°2
-    Jefatura

- ### Usuarios
-    usuario: central - password: guardia147 - grupo: Cuartel Central
-    usuario: destacamento1 - password: guardia147 - grupo: Destacamento N°1
-    usuario: destacamento2 - password: guardia147 - grupo: Destacamento N°2
-    usuario: jefatura - password: jguardia147 - grupo: Jefatura

Con estos datos ya podemos tener en funcionamiento el proyecto. Cerrar sesión en el panel de administración para finalizar.

## Ingreso

Una vez cargados los datos ingresar a [localhost:8000](http://localhost:8000) e ingresar con alguno de los usuarios que no es el super user.

Puede haber ocaciones en dónde arroje un error luego de haber trabajado en el panel de administración con el superuser. Presionar Ctrl-Shift-R para borrar las cookies y sesión y recargar la página para loguearte correctamente.