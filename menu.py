from neo4j import GraphDatabase

class PonyDatabase:
    def __init__(self, uri, user, password, database_name):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database_name = database_name

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session(database=self.database_name) as session:
            result = session.run(query, parameters)
            return [record for record in result]

    # 1.
    def agregar_pony(self, nombre, color, tipo, habilidad, cutiemark, gustos, bebida):
        query = """
        MERGE (p:Pony { nombre: $nombre, color: $color, tipo: $tipo, habilidad: $habilidad, cutiemark: $cutiemark, gusto: $gustos, bebida: $bebida })
        """
        self.run_query(query, {
            "nombre": nombre, 
            "color": color, 
            "tipo": tipo, 
            "habilidad": habilidad, 
            "cutiemark": cutiemark, 
            "gustos": gustos, 
            "bebida": bebida
        })
        self.run_query("""
        MATCH (p:Pony { nombre: $nombre }), (v:Pony { nombre: 'Vinyl Scratch' })
        MERGE (p)-[:AMIGOS]->(v)
        """, {"nombre": nombre})

    # 2.
    def city_population(self, ciudad):
        query = """
        MATCH (c:Ciudad {nombre: $ciudad})<-[:VIVE_EN]-(p:Pony)
        WHERE p.tipo = 'Unicornio' OR p.tipo = 'Pony terrestre' OR p.tipo = 'Pegaso'
        RETURN 
            COUNT(DISTINCT CASE WHEN p.tipo = 'Unicornio' THEN p END) AS unicornios,
            COUNT(DISTINCT CASE WHEN p.tipo = 'Pony terrestre' THEN p END) AS pony_terrestres,
            COUNT(DISTINCT CASE WHEN p.tipo = 'Pegaso' THEN p END) AS pegasos
        """
        result = self.run_query(query, {"ciudad": ciudad})
        return result

    # 3.
    def actualizar_anexo(self):
        query = """
        MATCH (p:Pony)
        OPTIONAL MATCH (p)-[r:AMIGOS]->(amigos)
        WITH p, COUNT(r) AS num_amigos
        SET p.anexo = CASE
            WHEN p.tipo = 'Unicornio' AND num_amigos >= 3 THEN 'Sociable'
            WHEN p.tipo = 'Unicornio' AND num_amigos = 2 THEN 'Reservado'
            WHEN p.tipo = 'Unicornio' AND num_amigos = 1 THEN 'Solitario'
            WHEN p.tipo = 'Alicornio' THEN 'Realeza'
            WHEN p.tipo = 'Pony terrestre' AND num_amigos >= 4 THEN 'Hipersociable'
            WHEN p.tipo = 'Pony terrestre' AND num_amigos <= 2 THEN 'Reservado'
            ELSE 'Por completar'
        END;
        """
        self.run_query(query)
    
    # 4.
    def camino_mas_corto(self):
        nombre_pony1 = input("Ingrese el nombre del primer pony: ")
        nombre_pony2 = input("Ingrese el nombre del segundo pony: ")

        query = """
        MATCH (p1:Pony {nombre: $nombre_pony1}), (p2:Pony {nombre: $nombre_pony2}),
                path = shortestPath((p1)-[:AMIGOS*]-(p2))
        RETURN length(path) AS longitud, [n IN nodes(path) | n.nombre] AS nodos
        """

        result = self.run_query(query, {"nombre_pony1": nombre_pony1, "nombre_pony2": nombre_pony2})

        return result

    # 5.
    def amigos_de_amigos(self, nombre):
        query = """
        MATCH (p:Pony {nombre: $nombre})-[:AMIGOS]->(amigo)-[:AMIGOS]->(amigos_de_amigos)
        WHERE NOT (p)-[:AMIGOS]->(amigos_de_amigos)
          AND amigos_de_amigos <> p
        RETURN DISTINCT amigos_de_amigos.nombre AS nombre;
        """
        result = self.run_query(query, {"nombre": nombre})
        return result
    
    # 6.
    def ponis_con_habilidad_magia(self):
        query = """
        MATCH (p:Pony)
        WHERE toLower(p.habilidad) CONTAINS 'magia'
        RETURN p.nombre AS nombre, p.habilidad AS habilidad;
        """
        result = self.run_query(query)
        return result
    
    # 7.
    def amigos_unidireccionales(self):
        query = """
        MATCH (p1:Pony)-[:AMIGOS]->(p2:Pony)
        WHERE NOT (p2)-[:AMIGOS]->(p1)
        RETURN p1.nombre AS pony, p2.nombre AS amigo;
        """
        result = self.run_query(query)
        return result
    
    # 8.
    def ponis_con_gustos(self, tipo_pony):
        query = """
        MATCH (p:Pony {tipo: $tipo_pony})
        RETURN
            COUNT(DISTINCT CASE WHEN p.bebida = 'Coca Cola' THEN p END) AS coca_cola,
            COUNT(DISTINCT CASE WHEN p.bebida = 'Sprite' THEN p END) AS sprite;
        """
        result = self.run_query(query, {"tipo_pony": tipo_pony})
        return result

    # 9.
    def enemigos_vs_colaboraciones(self):
        query = """
        MATCH (p:Pony)
        MATCH (p)-[:ENEMIGOS]->(enemigos)
        WITH p, COUNT(enemigos) AS num_enemigos
        WHERE NOT (p)-[:COLABORACION]->()
        RETURN p.nombre AS pony, num_enemigos, 0 AS num_colaboraciones;
        """
        resultado_1 = self.run_query(query)

        query= """
        MATCH (p:Pony)
        MATCH (p)-[:ENEMIGOS]->(enemigos)
        WITH p, COUNT(enemigos) AS num_enemigos
        MATCH (p)-[:COLABORACION]->(colaboradores)
        WITH p, num_enemigos, COUNT(colaboradores) AS num_colaboraciones
        WHERE num_enemigos > num_colaboraciones
        RETURN p.nombre AS pony, num_enemigos, num_colaboraciones;
        """
        resultado_2 = self.run_query(query)
        
        return resultado_1 + resultado_2
    
    # 10.
    def ponis_con_gusto_coca_y_amigo_sprite(self):
        query = """
        MATCH (p1:Pony)-[:AMIGOS]->(p2:Pony {bebida: 'Sprite'})
        WHERE p1.bebida = 'Coca Cola'
        RETURN p1.nombre AS nombre;
        """
        result = self.run_query(query)
        return result


def menu():
    print("")
    print("Selecciona una de las opciones:")
    print("1. Agregar un pony amigo de Vinyl Scratch")
    print("2. Ver la cantidad de pegasos, ponis terrestres y unicornios en una ciudad")
    print("3. Actualizar el campo 'anexo'")
    print("4. Encontrar el camino más corto entre dos ponys")
    print("5. Encontrar los amigos de los amigos de un pony")
    print("6. Ponis con habilidades relacionadas a la magia")
    print("7. Relaciones Unidireccionales")
    print("8. Ponis con gustos de bebida Coca Cola o Sprite")
    print("9. Ponis con más enemigos que colaboraciones")
    print("10. Ponis que tienen preferencia por Coca-Cola y que tengan al menos un amigo pony terrestre que prefiera Sprite")
    print("11. Salir")
    opcion = input("Seleccione una opción: ")
    return opcion


def solicitar_datos_pony():
    nombre = input("Ingrese el nombre del pony: ")
    color = input("Ingrese el color del pony: ")
    tipo = input("Ingrese el tipo de pony (Alicornio, Pegaso, Unicornio, Pony terrestre): ")
    habilidad = input("Ingrese la habilidad del pony: ")
    cutiemark = input("Ingrese la cutie mark del pony: ")
    gustos = input("Ingrese los gustos del pony: ")
    bebida = input("Ingrese la bebida favorita del pony (Coca Cola o Sprite): ")
    return nombre, color, tipo, habilidad, cutiemark, gustos, bebida


if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"
    database_name = "ponydb"
    
    db = PonyDatabase(uri, user, password, database_name)
    
    while True:
        opcion = menu()
        
        if opcion == "1":
            nombre, color, tipo, habilidad, cutiemark, gustos, bebida = solicitar_datos_pony()
            db.agregar_pony(nombre, color, tipo, habilidad, cutiemark, gustos, bebida)
            print("")
            print(f"Pony {nombre} agregado y ahora es amigo de Vinyl Scratch.")
        
        elif opcion == "2":
            nombre_ciudad = input("Ingrese el nombre de la ciudad para ver la población de ponys: ")
            resultado = db.city_population(nombre_ciudad)
            if resultado:
                print("")
                print(f"Población de ponys en {nombre_ciudad}:")
                print(f"Unicornios: {resultado[0]['unicornios']}")
                print(f"Pony terrestres: {resultado[0]['pony_terrestres']}")
                print(f"Pegasos: {resultado[0]['pegasos']}")
            else:
                print(f"No se encontraron ponys en la ciudad {nombre_ciudad}.")

        elif opcion == "3":
            db.actualizar_anexo()
            print("")
            print("Campo 'anexo' actualizado para todos los ponys.")

        elif opcion == "4":
            resultado = db.camino_mas_corto()
            if resultado:
                print("")
                print("Camino más corto entre los ponys:")
                for record in resultado:
                    print(f"Longitud del camino: {record['longitud']}")
                    print(f"Nodos en el camino: {record['nodos']}")
            else:
                print("No existe relación")

        elif opcion == "5":
            nombre = input("Ingrese el nombre del pony para encontrar sus amigos de los amigos: ")
            resultado = db.amigos_de_amigos(nombre)
            if resultado:
                print("")
                print(f"Amigos de los amigos de {nombre}:")
                for record in resultado:
                    print(record['nombre'])
            else:
                print(f"{nombre} no tiene amigos de amigos para mostrar.")

        elif opcion == "6":
            resultado = db.ponis_con_habilidad_magia()
            if resultado:
                print("")
                print("Ponis con habilidades relacionadas a la magia:")
                for record in resultado:
                    print(f"{record['nombre']} tiene la habilidad {record['habilidad']}.")
            else:
                print("No se encontraron ponis con habilidades relacionadas a la magia.")

        elif opcion == "7":
            resultado = db.amigos_unidireccionales()
            if resultado:
                print("")
                print("Relaciones de amistad unidireccionales:")
                for record in resultado:
                    print(f"{record['pony']} es amigo de {record['amigo']} pero no viceversa.")
            else:
                print("No se encontraron relaciones de amistad unidireccionales.")

        elif opcion == "8":
            tipo_pony = input("Ingrese el tipo de pony (Alicornio, Pegaso, Unicornio, Pony terrestre): ")
            resultado = db.ponis_con_gustos(tipo_pony)
            if resultado:
                print("")
                print(f"Ponis de tipo {tipo_pony} con gustos de bebida Coca Cola o Sprite:")
                print(f"Coca Cola: {resultado[0]['coca_cola']}")
                print(f"Sprite: {resultado[0]['sprite']}")
            else:
                print(f"No se encontraron ponis de tipo {tipo_pony} con gustos de bebida Coca Cola o Sprite.")

        elif opcion == "9":
            resultado = db.enemigos_vs_colaboraciones()
            if resultado:
                print("")
                print("Ponis con más enemigos que colaboraciones:")
                for record in resultado:
                    print(f"{record['pony']} tiene {record['num_enemigos']} enemigos y {record['num_colaboraciones']} colaboraciones.")
            else:
                print("No se encontraron ponis con más enemigos que colaboraciones.")

        elif opcion == "10":
            resultado = db.ponis_con_gusto_coca_y_amigo_sprite()
            datos = [record[0] for record in resultado]
            no_repetidos = list(set(datos))

            if resultado:
                print("")
                print("Ponis que prefieren Coca-Cola y tienen al menos un amigo que prefiere Sprite:")
                for pony in no_repetidos:
                    print(pony)
            else:
                print("No se encontraron ponis que prefieren Coca-Cola y tienen al menos un amigo que prefiere Sprite.")

        elif opcion == "11":
            print("")
            print("Saliendo del programa...")
            break
    
    db.close()
