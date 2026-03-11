class Usuario:
    def __init__(self, id_usuario: int, name: str, email: str, password: str, preferencias: list, alergias: list, celiaco: bool):
        self.id_usuario = id_usuario
        self.name = name
        self.email = email
        self.password = password
        self.preferencias = list(preferencias) if preferencias is not None else []
        self.alergias = list(alergias) if alergias is not None else []
        self.celiaco = celiaco
    
    def get(self):
        return {
            "id_usuario": self.id_usuario,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "preferencias": self.preferencias,
            "alergias": self.alergias,
            "celiaco": self.celiaco
        }
    
