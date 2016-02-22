"""Ejemplo integrador de una lista de reglas de limpieza."""

rules = [
    {
        "nombre_propio": [
            {"field": "dependencia"}
        ]
    },
    {
        "string": [
            {"field": "dependencia"},
            {"field": "lugar_audiencia"},
            {"field": "sujeto_obligado"},
            {"field": "solicitante"}
        ]
    },
    {
        "fecha_completa": [
            {"field": "fecha_completa_audiencia",
             "time_format": "DD-MM-YYYY HH:mm"}
        ]
    },
    {
        "fecha_separada": [
            {"fields": [["fecha_audiencia", "DD-MM-YYYY"],
                        ["hora_audiencia", "HH:mm"]],
             "new_field_name": "audiencia"}
        ]
    },
    {
        "string_simple_split": [
            {"field": "sujeto_obligado",
             "separators": [", Cargo:", "Cargo:"],
             "new_field_names": ["nombre", "cargo"]}
        ]
    },
    {
        "string_peg_split": [
            {"field": "solicitante",
             "grammar": """
            allowed_char = anything:x ?(x not in '1234567890() ')
            nombre = ~('DNI') <allowed_char+>:n ws -> n.strip()
            number = <digit+>:num -> int(num)

            nom_comp = <nombre+>:nc -> nc.strip()
            cargo = '(' <nombre+>:c ')' -> c.strip()
            dni = ','? ws 'DNI' ws number:num -> num

            values = nom_comp:n ws cargo?:c ws dni?:d ws anything* -> [n, c, d]
             """,
             "new_field_names": ["nombre", "cargo", "dni"]}
        ]
    }
]
