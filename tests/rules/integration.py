rules = [
    {
        "nombre_propio": ["dependencia"]
    },
    {
        "string": [
            "dependencia",
            "lugar_audiencia",
            "sujeto_obligado",
            "solicitante"
        ]
    },
    {
        "fecha_completa": [
            ["fecha_completa_audiencia", "DD-MM-YYYY HH:mm"]
        ]
    },
    {
        "fecha_separada": [
            [[["fecha_audiencia", "DD-MM-YYYY"], ["hora_audiencia", "HH:mm"]],
             "audiencia"]
        ]
    },
    {
        "string_simple_split": [
            ["sujeto_obligado", [", Cargo:", "Cargo:"], ["nombre", "cargo"]]
        ]
    },
    {
        "string_regex_split": []
    },
    {
        "string_peg_split": [
            ["solicitante",
             """
            allowed_char = anything:x ?(x not in '1234567890() ')
            nombre = ~('DNI') <allowed_char+>:n ws -> n.strip()
            number = <digit+>:num -> int(num)

            nom_comp = <nombre+>:nc -> nc.strip()
            cargo = '(' <nombre+>:c ')' -> c.strip()
            dni = ','? ws 'DNI' ws number:num -> num

            values = nom_comp:n ws cargo?:c ws dni?:d ws anything* -> [n, c, d]
            """,
             ["nombre", "cargo", "dni"]
             ]
        ]
    }
]
