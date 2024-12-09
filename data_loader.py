import pandas as pd

class DataLoader:
    """
    DataLoader final, con configuración de impresión y corrección de warnings.

    Atributos de impresión:
    - self.print_data (bool): si False, no imprime nada.
    - self.print_all (bool): si True, imprime todas las filas de las tablas.
    - self.print_limit (int): número de filas máximas a imprimir si print_all es False.

    Uso:
    data_loader = DataLoader(file_multas='...', file_pot='...', file_rutas='...')
    data_loader.set_print_options(print_data=True, print_all=False, print_limit=5)
    data_loader.load_all_data()
    """

    def __init__(self, file_multas=None, file_pot=None, file_rutas=None):
        self.file_multas = file_multas
        self.file_pot = file_pot
        self.file_rutas = file_rutas

        self.multas_data = {}
        self.pot_data = {}
        self.rutas_data = {}

        self.pot_parsed = {}

        # Configuración de impresión por defecto
        self.print_data = True
        self.print_all = False
        self.print_limit = 5

    def set_print_options(self, print_data=True, print_all=False, print_limit=5):
        self.print_data = print_data
        self.print_all = print_all
        self.print_limit = print_limit

    def _cargar_excel(self, filename):
        data = {}
        xls = pd.ExcelFile(filename)
        for sheet in xls.sheet_names:
            df = pd.read_excel(filename, sheet_name=sheet)
            data[sheet] = df
        return data

    def _print_rows(self, df):
        """
        Imprime filas de df según la configuración:
        - Si self.print_data es False, no imprime nada.
        - Si self.print_all es True, imprime todo el df.
        - Si self.print_all es False, imprime min(len(df), self.print_limit) filas.
        """
        if not self.print_data:
            return
        if self.print_all:
            print(df)
        else:
            filas_mostrar = min(len(df), self.print_limit)
            if filas_mostrar > 0:
                print(df.head(filas_mostrar))
            else:
                print("No hay datos en esta hoja.")

    def _print_list_of_dicts(self, data_list):
        """
        Imprime una lista de diccionarios según la configuración.
        """
        if not self.print_data:
            return
        if self.print_all:
            for d in data_list:
                print(d)
        else:
            for d in data_list[:self.print_limit]:
                print(d)

    def _mostrar_informacion(self, data_dict, nombre_archivo):
        if not self.print_data:
            return
        if not data_dict:
            print(f"No se cargó información para {nombre_archivo}.")
            return

        print(f"\n=== Información del archivo (Crudo): {nombre_archivo} ===")
        print(f"Hojas disponibles: {list(data_dict.keys())}")

        for sheet_name, df in data_dict.items():
            print(f"\nHoja: {sheet_name}")
            print("Columnas:", df.columns.tolist())
            print("Primeras filas:")
            self._print_rows(df)

    def _mostrar_informacion_pot_parsed(self):
        if not self.print_data:
            return
        print(f"\n=== Información del POT (PARSEADA) - {self.file_pot} ===")
        # TAPA
        print("\n--- TAPA ---")
        if self.pot_parsed.get("TAPA"):
            for k,v in self.pot_parsed["TAPA"].items():
                print(f"{k}: {v}")
        else:
            print("No se extrajo información TAPA.")

        # Servicios
        print("\n--- Servicios ---")
        servicios_info = self.pot_parsed.get("Servicios", {})
        operador = servicios_info.get("operador", "No encontrado")
        rut = servicios_info.get("rut", "No encontrado")
        print(f"Operador: {operador}")
        print(f"RUT: {rut}")
        servicios_df = servicios_info.get("tabla_servicios", pd.DataFrame())
        if not servicios_df.empty:
            print("Columnas:", servicios_df.columns.tolist())
            print("Primeras filas:")
            self._print_rows(servicios_df)
        else:
            print("No se extrajo tabla de servicios.")

        # Hojas 80X
        otras_hojas = [h for h in self.pot_parsed.keys() if h not in ["TAPA","Servicios"]]
        if otras_hojas:
            print("\n--- Hojas de Programas de Operación (80X) ---")
            for hoja in otras_hojas:
                print(f"\nHoja: {hoja}")
                data_80x = self.pot_parsed[hoja]
                info_servicio = data_80x.get("info_servicio", {})
                frecuencias = data_80x.get("frecuencias", [])

                print("Info del Servicio:")
                for k,v in info_servicio.items():
                    print(f"  {k}: {v}")

                print("Frecuencias (muestra según configuración):")
                self._print_list_of_dicts(frecuencias)
        else:
            print("\nNo se encontraron hojas tipo 80X.")

    def load_multas_data(self):
        if self.file_multas is None:
            if self.print_data:
                print("No se especificó archivo de multas. Omitiendo carga.")
            return
        self.multas_data = self._cargar_excel(self.file_multas)
        self._mostrar_informacion(self.multas_data, self.file_multas)

    def load_pot_data(self):
        if self.file_pot is None:
            if self.print_data:
                print("No se especificó archivo POT. Omitiendo carga.")
            return
        self.pot_data = self._cargar_excel(self.file_pot)
        self._parse_pot_data()
        self._mostrar_informacion_pot_parsed()

    def load_rutas_data(self):
        if self.file_rutas is None:
            if self.print_data:
                print("No se especificó archivo de Rutas_Operacion. Omitiendo carga.")
            return
        self.rutas_data = self._cargar_excel(self.file_rutas)
        self._mostrar_informacion(self.rutas_data, self.file_rutas)

    def load_all_data(self):
        self.load_multas_data()
        self.load_pot_data()
        self.load_rutas_data()

    def get_multas_data(self):
        return self.multas_data

    def get_pot_data(self):
        return self.pot_data

    def get_rutas_data(self):
        return self.rutas_data

    def get_pot_parsed(self):
        return self.pot_parsed

    def _parse_pot_data(self):
        self.pot_parsed["TAPA"] = self._parse_tapa(self.pot_data.get("TAPA", pd.DataFrame()))
        self.pot_parsed["Servicios"] = self._parse_servicios(self.pot_data.get("Servicios", pd.DataFrame()))
        otras_hojas = [h for h in self.pot_data.keys() if h not in ["TAPA","Servicios"]]
        
        # Crear un diccionario para programas
        programas_dict = {}
        for hoja in otras_hojas:
            programas_dict[hoja] = self._parse_80X_sheet(self.pot_data[hoja])
        
        # Guardar en pot_parsed["Programas"]
        self.pot_parsed["Programas"] = programas_dict

    def _to_upper_df(self, df):
        # Reemplazo de applymap por apply col-wise
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip().str.upper()
        return df

    def _parse_tapa(self, df):
        info = {}
        if df.empty:
            return info

        buscar = {
            "TIPO REGULACIÓN": "TIPO REGULACIÓN",
            "TIPO ANEXO": "TIPO ANEXO",
            "TIPO PROGRAMA": "TIPO PROGRAMA",
            "REGIÓN": "REGIÓN",
            "ZONA REGULADA": "ZONA REGULADA",
            "UNIDAD DE NEGOCIO": "UNIDAD DE NEGOCIO",
            "CON VERSIONES DE TRAZADO": "CON VERSIONES DE TRAZADO",
            "FECHA INICIO": "FECHA INICIO",
            "FECHA FIN": "FECHA FIN",
            "RES N°": "RES N°",
            "ESTACIONALIDAD": "ESTACIONALIDAD",
            "CORRELATIVO A1": "CORRELATIVO A1"
        }

        df_str = df.copy()
        df_str = self._to_upper_df(df_str)

        for key, texto in buscar.items():
            texto_up = texto.upper()
            valor_encontrado = None
            for i, row in df_str.iterrows():
                if any((pd.notna(val) and texto_up in val) for val in row.values):
                    fila_original = df.iloc[i]
                    non_empty_vals = [x for x in fila_original.values if pd.notna(x) and str(x).strip() != ""]
                    if non_empty_vals:
                        valor_encontrado = str(non_empty_vals[-1]).strip()
                    break
            info[key] = valor_encontrado if valor_encontrado is not None else "No encontrado"
        return info

    def _parse_servicios(self, df):
        info = {
            "operador": "No encontrado",
            "rut": "No encontrado",
            "tabla_servicios": pd.DataFrame()
        }

        if df.empty:
            return info

        df_str = df.copy()
        df_str = self._to_upper_df(df_str)

        # Buscar 1. Descripción del Operador
        fila_desc_op = None
        for i, row in df_str.iterrows():
            if any(pd.notna(val) and "1. DESCRIPCIÓN DEL OPERADOR" in val for val in row.values):
                fila_desc_op = i
                break

        if fila_desc_op is not None:
            info["operador"] = self._buscar_valor_en_fila(df, fila_desc_op, "OPERADOR DE TRANSPORTE")
            info["rut"] = self._buscar_valor_cercano(df, fila_desc_op, "RUT")

        # Buscar 2. Resumen de servicios (tabla)
        fila_resumen = None
        for i, row in df.iterrows():
            for val in row.values:
                if pd.notna(val) and isinstance(val, str) and "2. RESUMEN DE SERVICIOS" in val.upper():
                    fila_resumen = i
                    break
            if fila_resumen is not None:
                break

        if fila_resumen is not None:
            fila_encabezados = None
            for start_row in range(fila_resumen, len(df)):
                fila = df.iloc[start_row].dropna().astype(str).str.strip().values
                if all(k in fila for k in ["Servicio","Sentido","Origen","Destino"]):
                    fila_encabezados = start_row
                    break

            if fila_encabezados is not None:
                headers = df.iloc[fila_encabezados].values
                headers = [str(x).strip() if pd.notna(x) else "" for x in headers]
                rows = []
                for j in range(fila_encabezados+1, len(df)):
                    row_vals = df.iloc[j].values
                    if all(pd.isna(x) for x in row_vals):
                        break
                    rows.append(row_vals)

                servicios_df = pd.DataFrame(rows, columns=headers)
                servicios_df = servicios_df.loc[:, servicios_df.columns != ""]
                info["tabla_servicios"] = servicios_df

        return info

    def _buscar_valor_en_fila(self, df, start_row, keyword):
        df_str = df.copy()
        df_str = self._to_upper_df(df_str)
        if start_row < len(df_str):
            row = df_str.iloc[start_row]
            if any(pd.notna(x) and keyword in x for x in row.values):
                fila_original = df.iloc[start_row]
                non_empty_vals = [x for x in fila_original.values if pd.notna(x) and str(x).strip() != ""]
                if non_empty_vals:
                    return str(non_empty_vals[-1]).strip()
        return "No encontrado"

    def _buscar_valor_cercano(self, df, start_row, keyword):
        df_str = df.copy()
        df_str = self._to_upper_df(df_str)
        max_rows = min(start_row+10, len(df_str))
        for i in range(start_row, max_rows):
            row = df_str.iloc[i]
            if any(pd.notna(x) and keyword in x for x in row.values):
                fila_original = df.iloc[i]
                non_empty_vals = [x for x in fila_original.values if pd.notna(x) and str(x).strip() != ""]
                if non_empty_vals:
                    return str(non_empty_vals[-1]).strip()
        return "No encontrado"

    def _parse_80X_sheet(self, df):
        info_servicio = {}
        frecuencias_list = []

        # Buscar info del servicio
        fila_enc_info = None
        for i, row in df.iterrows():
            vals = [str(x).strip() for x in row.dropna().values if pd.notna(x)]
            if all(k in vals for k in ["Servicio","Sentido","Origen","Destino","Estacionalidad"]):
                fila_enc_info = i
                break

        if fila_enc_info is not None and fila_enc_info+1 < len(df):
            fila_valores = df.iloc[fila_enc_info+1]
            headers = df.iloc[fila_enc_info].values
            headers = [str(h).strip() if pd.notna(h) else "" for h in headers]
            for h,v in zip(headers, fila_valores.values):
                if h in ["Servicio","Sentido","Origen","Destino","Estacionalidad"]:
                    if pd.notna(v):
                        info_servicio[h] = str(v).strip()

        # Buscar la sección "2. Frecuencias"
        fila_frec = None
        for i, row in df.iterrows():
            for val in row.values:
                if pd.notna(val) and isinstance(val, str) and "2. FRECUENCIAS" in val.upper():
                    fila_frec = i
                    break
            if fila_frec is not None:
                break

        if fila_frec is not None:
            fila_enc_frec = None
            fila_enc_frec2 = None
            for start_row in range(fila_frec, len(df)):
                vals = [str(x).strip().upper() for x in df.iloc[start_row].dropna().values if pd.notna(x)]
                if "PERIODO" in vals and "HORARIO" in vals:
                    fila_enc_frec = start_row
                    # La siguiente fila para sub-encabezados
                    if start_row+1 < len(df):
                        vals2 = [x for x in df.iloc[start_row+1].values if pd.notna(x)]
                        if len(vals2) > 0:
                            fila_enc_frec2 = start_row+1
                    break

            if fila_enc_frec is not None and fila_enc_frec2 is not None:
                row1 = df.iloc[fila_enc_frec].values
                row2 = df.iloc[fila_enc_frec2].values

                combined_headers = []
                for c1, c2 in zip(row1, row2):
                    h1 = str(c1).strip() if pd.notna(c1) else ""
                    h2 = str(c2).strip() if pd.notna(c2) else ""
                    if h1 and h2:
                        combined_headers.append(f"{h1}_{h2}")
                    else:
                        combined_headers.append(h1 if h1 else h2)

                for j in range(fila_enc_frec2+1, len(df)):
                    row_vals = df.iloc[j].values
                    if any(isinstance(x, str) and "Total" in x for x in row_vals if pd.notna(x)):
                        break
                    if all(pd.isna(x) for x in row_vals):
                        break
                    fila_dict = {}
                    for col_name, val in zip(combined_headers, row_vals):
                        if col_name:
                            # Si Periodo es número, convirtamos a int
                            if col_name == "Periodo" and pd.notna(val):
                                fila_dict[col_name] = int(val)
                            else:
                                fila_dict[col_name] = val if pd.notna(val) else None
                    frecuencias_list.append(fila_dict)

        return {
            "info_servicio": info_servicio,
            "frecuencias": frecuencias_list
        }
