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

if __name__ == "__main__":
    db = PonyDatabase("bolt://localhost:7687", "neo4j", "12345678", "ponydb")
    query = "MATCH (n:Pony) RETURN n LIMIT 5"
    result = db.run_query(query)
    if result:
        for record in result:
            node = record['n']
            print("Atributos del nodo:")
            for key, value in node.items():
                print(f"{key}: {value}")
            print("-" * 40)
    else:
        print("No se encontraron nodos.")
    db.close()
