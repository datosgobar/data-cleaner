"""Ejemplo integrador de una lista de reglas de limpieza."""

rules = [
    {
        "nombre_propio": [
            {"field": "dependencia", "keep_original": False}
        ]
    },
    {
        "string": [
            {"field": "dependencia", "keep_original": False},
            {"field": "lugar_audiencia", "keep_original": False},
            {"field": "sujeto_obligado", "keep_original": False},
            {"field": "solicitante", "keep_original": False}
        ]
    },
    {
        "fecha_completa": [
            {"field": "fecha_completa_audiencia",
             "time_format": "DD-MM-YYYY HH:mm",
             "keep_original": True}
        ]
    },
    {
        "fecha_separada": [
            {"fields": [["fecha_audiencia", "DD-MM-YYYY"],
                        ["hora_audiencia", "HH:mm"]],
             "new_field_name": "audiencia",
             "keep_original": True}
        ]
    },
    {
        "string_simple_split": [
            {"field": "sujeto_obligado",
             "separators": [", Cargo:", "Cargo:"],
             "new_field_names": ["nombre", "cargo"],
             "keep_original": True}
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
             "new_field_names": ["nombre", "cargo", "dni"],
             "keep_original": True}
        ]
    }
]
