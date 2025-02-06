INSERT INTO planilla_jerarquia (id, jerarquia) VALUES
(1, 'Bombero'),
(2, 'Sub Ayudante'),
(3, 'Ayudante'),
(4, 'Ayudante de 1ra'),
(5, 'Ayudante Principal'),
(6, 'Ayudante Mayor'),
(7, 'Oficial Auxiliar'),
(8, 'Oficial Auxiliar de Escuadra'),
(9, 'Oficial Aux. de Dotación'),
(10, 'Subcomandante'),
(11, 'Comandante'),
(12, 'Comandante Mayor'),
(13, 'Comandante General')
ON CONFLICT (id) DO NOTHING;

INSERT INTO planilla_base (id, base) VALUES
(1, 'Cuartel Central'),
(2, 'Destacamento N°1'),
(3, 'Destacamento N°2')
ON CONFLICT (id) DO NOTHING;

INSERT INTO planilla_tipomovil (id, tipo) VALUES
(1, 'Primera dotación'),
(2, 'Cisterna'),
(3, 'Hidroelevador'),
(4, 'Cascada'),
(5, 'Unidad Forestal'),
(6, 'Comando'),
(7, 'Rescate Acuático'),
(8, 'Traslado de personal')
ON CONFLICT (id) DO NOTHING;

INSERT INTO planilla_estado (id, estado) VALUES
(1, 'En servicio'),
(2, 'Condicional'),
(3, 'Fuera de servicio')
ON CONFLICT (id) DO NOTHING;

INSERT INTO planilla_compania (id, cuartel) VALUES
(1, '3 de Febrero'),
(2, 'Gral. Sarmiento'),
(3, 'Matanza'),
(4, 'Merlo'),
(5, 'Morón'),
(6, 'Ituzaingó')
ON CONFLICT (id) DO NOTHING;

INSERT INTO planilla_tiposervicio (id, tipo) VALUES
(1, 'Incendio'),
(2, 'Auxilio'),
(3, 'Colaboración'),
(4, 'Forestal'),
(5, 'Mat. Pel.'),
(6, 'Técnico')
ON CONFLICT (id) DO NOTHING;

INSERT INTO planilla_movil (id, numero, litros, intervenciones, "IDBase_id", "IDEstado_id", "IDTipo_id", ultima_carga, ultima_fluidos) VALUES
(1, '1', 100, 0, 1, 1, 8, '2025-01-20 10:21', '2025-01-20 10:21'),
(2, '2', 100, 0, 1, 3, 8, '2025-01-20 10:21', '2025-01-20 10:21'),
(3, '3', 100, 0, 1, 1, 8, '2025-01-20 10:21', '2025-01-20 10:21'),
(4, '4', 100, 0, 1, 1, 1, '2025-01-20 10:21', '2025-01-20 10:21'),
(5, '5', 100, 0, 1, 1, 1, '2025-01-20 10:21', '2025-01-20 10:21'),
(6, '6', 100, 0, 1, 1, 1, '2025-01-20 10:21', '2025-01-20 10:21'),
(7, '8', 100, 0, 1, 1, 1, '2025-01-20 10:21', '2025-01-20 10:21'),
(8, '9', 100, 0, 1, 1, 1, '2025-01-20 10:21', '2025-01-20 10:21'),
(9, '11', 100, 0, 1, 1, 2, '2025-01-20 10:21', '2025-01-20 10:21'),
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.planilla_bombero (id, legajo, nombre, apellido, es_chofer, posicion, activo, "IDBase_id", "IDJerarquia_id") VALUES
(1, '309', 'Fabián Antonio', 'Gareis', true, 1, true, 1, 11),
(2, '285', 'Jorge Adrián', 'Gimenez', true, 1, true, 3, 9),
(3, '292', 'Orlando Flavio', 'Tomasella', false, 1, true, 2, 9),
(4, '574', 'Claudio Fabián', 'Aylagas', false, 2, true, 2, 6),
(5, '297', 'Mauro Ezequiel', 'Silberberg', true, 2, true, 1, 9),
(6, '416', 'Carlos Luis', 'Visconti', true, 2, true, 3, 6),
(7, '67', 'Adalberto', 'Durán', true, 100, true, 2, 9),
(8, '70', 'Pedro Adrián', 'Campo', true, 3, true, 1, 11),
(9, '447', 'Sergio Anibal', 'Gonzalez', true, 3, true, 3, 5),
(10, '373', 'Guillermo Adrián', 'Kovacs', true, 4, true, 2, 6),
(11, '321', 'Juan José', 'Nazaro', false, 4, true, 1, 10),
(12, '324', 'Jorge Omar', 'Valdegaray', true, 5, true, 2, 6),
(13, '390', 'Esteban Andres', 'Alves', true, 5, true, 3, 5),
(14, '156', 'Adalberto Eduardo', 'Canova', true, 7, true, 1, 9),
(15, '503', 'Gustavo Ariel', 'Gutierrez', true, 8, true, 2, 4),
(16, '314', 'Miguel Ángel', 'Retamozo', false, 9, true, 1, 9),
(17, '359', 'Pablo Ariel', 'Rodriguez', false, 11, true, 1, 4),
(18, '308', 'Rubén Darío', 'López', true, 6, true, 3, 4),
(19, '247', 'Sergio Daniel', 'Escalante', false, 8, true, 1, 8),
(20, '422', 'José Ramón', 'Alarcón', true, 7, true, 2, 4),
(21, '405', 'Miguel Ángel', 'Lago', false, 9, true, 3, 4),
(22, '335', 'María Cristina', 'Cuello', false, 10, true, 1, 8),
(23, '368', 'Carlos Miguel', 'Fortunato', true, 11, true, 2, 3),
(24, '431', 'Roque Alfredo', 'Serpa', false, 10, true, 3, 4),
(25, '414', 'Fabián Edgardo', 'Ovejero', false, 11, true, 3, 4),
(26, '319', 'José María', 'Biaiñ', false, 12, true, 1, 8),
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.planilla_tipomaterial (id, tipo) VALUES
(2, 'Escalera'),
(3, 'Acople'),
(4, 'Lanza'),
(5, 'Llave de unión'),
(6, 'Adaptador'),
(7, 'Reductores'),
(8, 'Divergente'),
(9, 'Columna'),
(10, 'Zapa'),
(11, 'De corte'),
(12, 'Efracción'),
(1, 'Manga 25mm'),
(13, 'Manga 38mm'),
(14, 'Manga 45mm'),
(15, 'Manga 63mm'),
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.planilla_tipomotor (id, tipo) VALUES
(1, 'Eléctrico 220V'),
(2, 'Baterías'),
(3, 'Combustión 2T'),
(4, 'Combustion 4T'),
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.planilla_material (id, nombre, cantidad, movil_id, ubicacion_id, cajonera, estado_id, image, potencia, motor_id, tipo_id) VALUES
(8, 'Halligan', 1, 4, NULL, '4', 1, '', NULL, NULL, 12),
(7, 'Manga 25mm', 1, NULL, 1, NULL, 3, '', NULL, NULL, 1),
(6, 'Manga 25mm', 2, 4, NULL, '5', 1, '', NULL, NULL, 1),
(5, 'Manga 25mm', 3, 4, NULL, '2', 1, '', NULL, NULL, 1),
(9, 'Holmatro', 1, 4, NULL, '6', 1, '', '1500W', 4, 11),
(10, 'Manga 63mm', 3, NULL, 1, '4', 3, '', NULL, NULL, 15),
(11, 'Manga 45mm', 3, 4, NULL, '7', 1, '', NULL, NULL, 14),
(12, 'Manga 38mm', 2, NULL, 1, '2', 3, '', NULL, NULL, 13),
(13, 'Manga 63mm', 1, NULL, 1, '7', 2, '', NULL, NULL, 15),
ON CONFLICT (id) DO NOTHING;
