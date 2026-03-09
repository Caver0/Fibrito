import numpy as np

class Alimento:
    def __init__(self, id_alimento: int, nombre: str, calorias: float, carbohidratos: float, proteinas: float, grasas: float, azucar: float, fibra: float, celiaco: bool):
        self.id_alimento = id_alimento
        self.nombre = nombre
        self.calorias = calorias
        self.carbohidratos = carbohidratos
        self.proteinas = proteinas
        self.grasas = grasas
        self.azucar = azucar
        self.fibra = fibra
        self.celiaco = celiaco

    def get(self):
        return {
            "id_alimento": self.id_alimento,
            "nombre": self.nombre,
            "calorias": self.calorias,
            "carbohidratos": self.carbohidratos,
            "proteinas": self.proteinas,
            "grasas": self.grasas,
            "azucar": self.azucar,
            "fibra": self.fibra,
            "celiaco": self.celiaco
        }
    
