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

    def actualizar_anexo(self):
        query = """
        MATCH (p:Pony)
        WHERE NOT (p)-[:AMIGOS]->()
        SET p.anexo = 'Por completar';
        """
        self.run_query(query)

        query = """
        MATCH (p:Pony)
        MATCH (p)-[:AMIGOS]->(amigos)
        WITH p, COUNT(amigos) AS num_amigos
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


    def amigos_de_amigos(self, nombre):
        query = """
        MATCH (p:Pony {nombre: $nombre})-[:AMIGOS]->(amigo)-[:AMIGOS]->(amigos_de_amigos)
        WHERE NOT (p)-[:AMIGOS]->(amigos_de_amigos)
          AND amigos_de_amigos <> p
        RETURN DISTINCT amigos_de_amigos.nombre AS nombre;
        """
        result = self.run_query(query, {"nombre": nombre})
        return result
    
    def amigos_unidireccionales(self):
        query = """
        MATCH (p1:Pony)-[:AMIGOS]->(p2:Pony)
        WHERE NOT (p2)-[:AMIGOS]->(p1)
        RETURN p1.nombre AS pony, p2.nombre AS amigo;
        """
        result = self.run_query(query)
        return result
    
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

def menu():
    print("")
    print("Selecciona una de las opciones:")
    print("1. Agregar un pony amigo de Vinyl Scratch")
    print("3. Actualizar el campo 'anexo'")
    print("5. Encontrar los amigos de los amigos de un pony")
    print("7. Relaciones Unidireccionales")
    print("9. Ponis con más enemigos que colaboraciones")
    print("10. Salir")
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

        elif opcion == "3":
            db.actualizar_anexo()
            print("")
            print("Campo 'anexo' actualizado para todos los ponys.")

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

        elif opcion == "7":
            resultado = db.amigos_unidireccionales()
            if resultado:
                print("")
                print("Relaciones de amistad unidireccionales:")
                for record in resultado:
                    print(f"{record['pony']} es amigo de {record['amigo']} pero no viceversa.")
            else:
                print("No se encontraron relaciones de amistad unidireccionales.")

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
            print("")
            print("Saliendo del programa...")
            break
    
    db.close()
