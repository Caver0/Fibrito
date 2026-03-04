import numpy as np
from array import array

class Usuario:
    def __init__(self, id_usuario: int, name: str, email:str, password: str, preferencias: array, alergias: array, celiaco: bool):
        self.id_usuario = id_usuario
        self.name = name
        self.email = email
        self.password = password
        self.preferencias = preferencias
        self.alergias = alergias
        self.celiaco = celiaco
    
    def get(self):
        return {
            "id_usuario": self.id_usuario,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "preferencias": self.preferencias.tolist() if isinstance(self.preferencias, np.ndarray) else self.preferencias,
            "alergias": self.alergias.tolist() if isinstance(self.alergias, np.ndarray) else self.alergias,
            "celiaco": self.celiaco
        }
    
