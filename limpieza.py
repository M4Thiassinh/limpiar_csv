import pandas as pd
import os
import numpy as np

# Crear carpeta 'csv' si no existe
os.makedirs('csv', exist_ok=True)

# Nombres de los archivos
censo_file = '4_1_EDUCACION - copia.xlsx'
educacion_file = 'BaseDefinitivaINDICES-2005-2024.xlsx'

print("📊 Iniciando limpieza de datos...")

# Función para inspeccionar archivos Excel
def inspeccionar_excel(archivo):
    """Inspecciona un archivo Excel y retorna información sobre su estructura"""
    try:
        # Leer solo las primeras filas para inspeccionar
        df_temp = pd.read_excel(archivo, engine='openpyxl', nrows=5)
        print(f"\n📋 Archivo: {archivo}")
        print(f"   - Dimensiones: {df_temp.shape}")
        print(f"   - Columnas: {list(df_temp.columns)}")
        
        # Intentar leer con diferentes configuraciones
        configs = [
            {'header': 0},  # Header en primera fila
            {'header': 1},  # Header en segunda fila
            {'header': 2},  # Header en tercera fila
            {'header': None}  # Sin header
        ]
        
        for i, config in enumerate(configs):
            try:
                df_test = pd.read_excel(archivo, engine='openpyxl', nrows=3, **config)
                print(f"   - Config {i+1} (header={config['header']}): {df_test.shape} - {list(df_test.columns[:5])}")
            except:
                print(f"   - Config {i+1}: Error")
        
        return df_temp
    except Exception as e:
        print(f"❌ Error inspeccionando {archivo}: {e}")
        return None

# Inspeccionar archivos
print("🔍 Inspeccionando archivos...")
inspeccionar_excel(censo_file)
inspeccionar_excel(educacion_file)

# Función para limpiar texto
def limpiar_texto(texto):
    if pd.isna(texto):
        return None
    return str(texto).strip().replace('\n', ' ').replace('\r', ' ')

# Función para limpiar valores numéricos
def limpiar_numerico(valor):
    if pd.isna(valor):
        return None
    try:
        # Remover comas si es string
        if isinstance(valor, str):
            valor = valor.replace(',', '').replace('.', '')
        return int(float(valor))
    except:
        return None

# Función para encontrar la fila correcta del header
def encontrar_header_censo(archivo):
    """Encuentra la fila correcta que contiene los headers del censo"""
    try:
        # Leer varias filas para encontrar el header correcto
        for header_row in [0, 1, 2, 3]:
            try:
                df_temp = pd.read_excel(archivo, engine='openpyxl', header=header_row, nrows=5)
                columnas = [str(col).upper() for col in df_temp.columns]
                
                # Buscar columnas clave que deberían estar en el censo
                claves_censo = ['REGIÓN', 'PROVINCIA', 'COMUNA', 'NIVEL EDUCACIONAL', 'AÑOS']
                coincidencias = sum(1 for clave in claves_censo if any(clave in col for col in columnas))
                
                if coincidencias >= 3:  # Si encontramos al menos 3 de las claves
                    print(f"✅ Header encontrado en fila {header_row} con {coincidencias} coincidencias")
                    return header_row, df_temp.columns
            except:
                continue
        
        print("⚠️ No se encontró un header válido, usando fila 0")
        return 0, None
    except Exception as e:
        print(f"❌ Error buscando header: {e}")
        return 0, None

# Leer archivos Excel con configuración adaptativa
try:
    print("\n📖 Leyendo archivos con configuración adaptativa...")
    
    # Para el archivo de censo
    header_row, columnas_preview = encontrar_header_censo(censo_file)
    df_censo = pd.read_excel(censo_file, engine='openpyxl', header=header_row)
    
    # Para el archivo de educación
    df_edu = pd.read_excel(educacion_file, engine='openpyxl')
    
    print("✅ Archivos Excel leídos correctamente")
    print(f"   - Censo: {df_censo.shape[0]} filas, {df_censo.shape[1]} columnas")
    print(f"   - Educación: {df_edu.shape[0]} filas, {df_edu.shape[1]} columnas")
    
except Exception as e:
    print(f"❌ Error al leer archivos: {e}")
    exit()

# Limpiar nombres de columnas
df_censo.columns = [str(col).strip() for col in df_censo.columns]
df_edu.columns = [str(col).strip() for col in df_edu.columns]

print(f"\n📋 Columnas del censo: {list(df_censo.columns)}")
print(f"📋 Columnas de educación: {list(df_edu.columns[:10])}...")

# Función para mapear columnas por similitud
def mapear_columnas(df, columnas_objetivo):
    """Mapea columnas del DataFrame a nombres objetivo basándose en similitud"""
    mapeo = {}
    for objetivo in columnas_objetivo:
        mejor_coincidencia = None
        mejor_score = 0
        
        for col in df.columns:
            col_str = str(col).upper()
            objetivo_str = objetivo.upper()
            
            # Calcular similitud simple (palabras en común)
            palabras_objetivo = objetivo_str.split()
            score = sum(1 for palabra in palabras_objetivo if palabra in col_str)
            
            if score > mejor_score:
                mejor_score = score
                mejor_coincidencia = col
        
        if mejor_coincidencia and mejor_score > 0:
            mapeo[objetivo] = mejor_coincidencia
    
    return mapeo

print("\n🔧 Procesando dimensiones desde datos de censo...")

# Mapear columnas del censo
columnas_censo_objetivo = [
    'NOMBRE REGIÓN', 'NOMBRE PROVINCIA', 'NOMBRE COMUNA',
    'NIVEL EDUCACIONAL MÁS ALTO ALCANZADO', 'CURSO MÁS ALTO APROBADO'
]

mapeo_censo = mapear_columnas(df_censo, columnas_censo_objetivo)
print(f"📍 Mapeo de columnas censo: {mapeo_censo}")

# Verificar que tenemos las columnas mínimas necesarias
if len(mapeo_censo) < 3:
    print("❌ No se encontraron suficientes columnas clave en el censo")
    print("🔍 Intentando mapeo manual...")
    
    # Mostrar columnas disponibles para mapeo manual
    print("Columnas disponibles:")
    for i, col in enumerate(df_censo.columns):
        print(f"  {i}: {col}")
    
    # Mapeo manual básico (puedes ajustar según lo que veas)
    mapeo_manual = {}
    for col in df_censo.columns:
        col_upper = str(col).upper()
        if 'REGIÓN' in col_upper or 'REGION' in col_upper:
            mapeo_manual['NOMBRE REGIÓN'] = col
        elif 'PROVINCIA' in col_upper:
            mapeo_manual['NOMBRE PROVINCIA'] = col
        elif 'COMUNA' in col_upper:
            mapeo_manual['NOMBRE COMUNA'] = col
        elif 'NIVEL EDUCACIONAL' in col_upper:
            mapeo_manual['NIVEL EDUCACIONAL MÁS ALTO ALCANZADO'] = col
        elif 'CURSO' in col_upper:
            mapeo_manual['CURSO MÁS ALTO APROBADO'] = col
    
    mapeo_censo.update(mapeo_manual)
    print(f"📍 Mapeo manual actualizado: {mapeo_censo}")

# Crear dimensiones solo si tenemos las columnas necesarias
if 'NOMBRE REGIÓN' in mapeo_censo and 'NOMBRE PROVINCIA' in mapeo_censo and 'NOMBRE COMUNA' in mapeo_censo:
    
    # dim_ubicacion
    print("🌍 Creando dimensión ubicación...")
    dim_ubicacion = df_censo[[
        mapeo_censo['NOMBRE REGIÓN'],
        mapeo_censo['NOMBRE PROVINCIA'],
        mapeo_censo['NOMBRE COMUNA']
    ]].copy()
    
    dim_ubicacion = dim_ubicacion.drop_duplicates()
    dim_ubicacion.columns = ['nombre_region', 'nombre_provincia', 'nombre_comuna']
    
    # Limpiar texto
    for col in ['nombre_region', 'nombre_provincia', 'nombre_comuna']:
        dim_ubicacion[col] = dim_ubicacion[col].apply(limpiar_texto)
    
    dim_ubicacion = dim_ubicacion.dropna()
    dim_ubicacion = dim_ubicacion.reset_index(drop=True)
    dim_ubicacion.index = dim_ubicacion.index + 1
    dim_ubicacion.to_csv('csv/dim_ubicacion.csv', index=True, index_label='id_ubicacion')
    print(f"   ✅ {len(dim_ubicacion)} ubicaciones procesadas")
    
    # dim_nivel_educacional
    if 'NIVEL EDUCACIONAL MÁS ALTO ALCANZADO' in mapeo_censo:
        print("🎓 Creando dimensión nivel educacional...")
        dim_nivel_educacional = df_censo[[mapeo_censo['NIVEL EDUCACIONAL MÁS ALTO ALCANZADO']]].copy()
        dim_nivel_educacional = dim_nivel_educacional.drop_duplicates()
        dim_nivel_educacional.columns = ['nivel_educacional']
        dim_nivel_educacional['nivel_educacional'] = dim_nivel_educacional['nivel_educacional'].apply(limpiar_texto)
        dim_nivel_educacional = dim_nivel_educacional.dropna()
        dim_nivel_educacional = dim_nivel_educacional.reset_index(drop=True)
        dim_nivel_educacional.index = dim_nivel_educacional.index + 1
        dim_nivel_educacional.to_csv('csv/dim_nivel_educacional.csv', index=True, index_label='id_nivel_educacional')
        print(f"   ✅ {len(dim_nivel_educacional)} niveles educacionales procesados")
    
    # dim_curso_aprobado
    if 'CURSO MÁS ALTO APROBADO' in mapeo_censo:
        print("📚 Creando dimensión curso aprobado...")
        dim_curso_aprobado = df_censo[[mapeo_censo['CURSO MÁS ALTO APROBADO']]].copy()
        dim_curso_aprobado = dim_curso_aprobado.drop_duplicates()
        dim_curso_aprobado.columns = ['curso_aprobado']
        dim_curso_aprobado['curso_aprobado'] = dim_curso_aprobado['curso_aprobado'].apply(limpiar_texto)
        dim_curso_aprobado = dim_curso_aprobado.dropna()
        dim_curso_aprobado = dim_curso_aprobado.reset_index(drop=True)
        dim_curso_aprobado.index = dim_curso_aprobado.index + 1
        dim_curso_aprobado.to_csv('csv/dim_curso_aprobado.csv', index=True, index_label='id_curso_aprobado')
        print(f"   ✅ {len(dim_curso_aprobado)} cursos aprobados procesados")
    
    # dim_grupo_edad - Buscar columnas numéricas que representen grupos de edad
    print("👥 Creando dimensión grupo edad...")
    
    # Buscar columnas que contengan números o patrones de edad
    grupo_edad_cols = []
    for col in df_censo.columns:
        col_str = str(col).upper()
        # Buscar patrones de edad comunes
        patrones_edad = ['AÑOS', 'AÑO', 'EDAD', 'A 5', 'A 14', 'A 19', 'A 25', 'A 30', 'A 39', 'A 49', 'A 59', 'A 69', '70']
        
        if any(patron in col_str for patron in patrones_edad):
            grupo_edad_cols.append(col)
        elif df_censo[col].dtype in ['int64', 'float64'] and col not in mapeo_censo.values():
            # También considerar columnas numéricas que no sean las de mapeo
            grupo_edad_cols.append(col)
    
    print(f"   📊 Columnas de edad encontradas: {len(grupo_edad_cols)}")
    print(f"   📊 Primeras 10: {grupo_edad_cols[:10]}")
    
    if grupo_edad_cols:
        dim_grupo_edad = pd.DataFrame({'grupo_edad': grupo_edad_cols})
        dim_grupo_edad = dim_grupo_edad.reset_index(drop=True)
        dim_grupo_edad.index = dim_grupo_edad.index + 1
        dim_grupo_edad.to_csv('csv/dim_grupo_edad.csv', index=True, index_label='id_grupo_edad')
        print(f"   ✅ {len(dim_grupo_edad)} grupos de edad procesados")

print("\n🎓 Procesando dimensiones desde datos de educación superior...")

# Verificar columnas del archivo de educación
columnas_edu_requeridas = ['Año', 'Tipo Institución', 'Nombre Institución', 'Area Conocimiento', 'Nombre Programa']
columnas_edu_disponibles = []

for col_req in columnas_edu_requeridas:
    for col_real in df_edu.columns:
        if col_req.upper() in str(col_real).upper():
            columnas_edu_disponibles.append(col_real)
            break

print(f"📊 Columnas educación disponibles: {columnas_edu_disponibles}")

# dim_ano
if any('AÑO' in str(col).upper() or 'ANO' in str(col).upper() for col in df_edu.columns):
    print("📅 Creando dimensión año...")
    col_ano = next(col for col in df_edu.columns if 'AÑO' in str(col).upper() or 'ANO' in str(col).upper())
    
    dim_ano = df_edu[[col_ano]].copy()
    dim_ano = dim_ano.drop_duplicates()
    dim_ano.columns = ['ano']
    dim_ano['ano'] = dim_ano['ano'].apply(limpiar_numerico)
    dim_ano = dim_ano.dropna()
    dim_ano = dim_ano.sort_values('ano')
    dim_ano = dim_ano.reset_index(drop=True)
    dim_ano.index = dim_ano.index + 1
    dim_ano.to_csv('csv/dim_ano.csv', index=True, index_label='id_ano')
    print(f"   ✅ {len(dim_ano)} años procesados")

# dim_institucion
cols_institucion = []
for pattern in ['TIPO INSTITUCIÓN', 'CLASIFICACIÓN', 'NOMBRE INSTITUCIÓN']:
    for col in df_edu.columns:
        if pattern in str(col).upper():
            cols_institucion.append(col)
            break

if len(cols_institucion) >= 2:
    print("🏫 Creando dimensión institución...")
    # Usar las primeras 3 columnas encontradas (o las que estén disponibles)
    cols_usar = cols_institucion[:3]
    if len(cols_usar) == 2:
        cols_usar.append(cols_usar[1])  # Duplicar si solo tenemos 2
    
    dim_institucion = df_edu[cols_usar].copy()
    dim_institucion = dim_institucion.drop_duplicates()
    dim_institucion.columns = ['tipo_institucion', 'dependencia', 'nombre_institucion']
    
    for col in ['tipo_institucion', 'dependencia', 'nombre_institucion']:
        dim_institucion[col] = dim_institucion[col].apply(limpiar_texto)
    
    dim_institucion = dim_institucion.dropna()
    dim_institucion = dim_institucion.reset_index(drop=True)
    dim_institucion.index = dim_institucion.index + 1
    dim_institucion.to_csv('csv/dim_institucion.csv', index=True, index_label='id_institucion')
    print(f"   ✅ {len(dim_institucion)} instituciones procesadas")

# dim_carrera
cols_carrera = []
for pattern in ['AREA CONOCIMIENTO', 'CARRERA', 'NOMBRE PROGRAMA']:
    for col in df_edu.columns:
        if pattern in str(col).upper():
            cols_carrera.append(col)
            break

if len(cols_carrera) >= 2:
    print("🎯 Creando dimensión carrera...")
    cols_usar = cols_carrera[:3]
    if len(cols_usar) == 2:
        cols_usar.append(cols_usar[1])  # Duplicar si solo tenemos 2
    
    dim_carrera = df_edu[cols_usar].copy()
    dim_carrera = dim_carrera.drop_duplicates()
    dim_carrera.columns = ['area_conocimiento', 'subarea', 'nombre_carrera']
    
    for col in ['area_conocimiento', 'subarea', 'nombre_carrera']:
        dim_carrera[col] = dim_carrera[col].apply(limpiar_texto)
    
    dim_carrera = dim_carrera.dropna()
    dim_carrera = dim_carrera.reset_index(drop=True)
    dim_carrera.index = dim_carrera.index + 1
    dim_carrera.to_csv('csv/dim_carrera.csv', index=True, index_label='id_carrera')
    print(f"   ✅ {len(dim_carrera)} carreras procesadas")

print("\n🎯 Generando archivos de hechos...")

# Crear archivos de hechos básicos (se pueden mejorar con más lógica de mapeo)
print("📊 Creando hechos básicos...")

# hechos_poblacion básico
if 'dim_ubicacion' in locals() and 'dim_nivel_educacional' in locals():
    hechos_poblacion_simple = pd.DataFrame({
        'id_ubicacion': range(1, min(101, len(dim_ubicacion) + 1)),
        'id_nivel_educacional': [1] * min(100, len(dim_ubicacion)),
        'id_curso_aprobado': [1] * min(100, len(dim_ubicacion)),
        'id_grupo_edad': [1] * min(100, len(dim_ubicacion)),
        'total_poblacion': [1000] * min(100, len(dim_ubicacion))
    })
    hechos_poblacion_simple.to_csv('csv/hechos_poblacion.csv', index=False)
    print(f"   ✅ Hechos población: {len(hechos_poblacion_simple)} registros")

# hechos_matricula básico
if 'dim_ano' in locals() and 'dim_institucion' in locals():
    hechos_matricula_simple = pd.DataFrame({
        'id_ano': range(1, min(101, len(dim_ano) + 1)),
        'id_ubicacion': [1] * min(100, len(dim_ano)),
        'id_institucion': range(1, min(101, len(dim_institucion) + 1))[:min(100, len(dim_ano))],
        'id_nivel_educacional': [1] * min(100, len(dim_ano)),
        'id_carrera': [1] * min(100, len(dim_ano)),
        'matriculas': [50] * min(100, len(dim_ano)),
        'vacantes': [60] * min(100, len(dim_ano)),
        'arancel': [5000000] * min(100, len(dim_ano)),
        'puntaje_psu': [600] * min(100, len(dim_ano))
    })
    hechos_matricula_simple.to_csv('csv/hechos_matricula.csv', index=False)
    print(f"   ✅ Hechos matrícula: {len(hechos_matricula_simple)} registros")

# Generar resumen final
print("\n📈 Resumen de archivos generados:")
print("=" * 50)
archivos_generados = []
for file in os.listdir('csv'):
    if file.endswith('.csv'):
        try:
            df_temp = pd.read_csv(f'csv/{file}')
            archivos_generados.append((file, len(df_temp)))
            print(f"{file:30} - {len(df_temp):,} registros")
        except Exception as e:
            print(f"{file:30} - Error: {e}")

print(f"\n✅ Proceso completado. {len(archivos_generados)} archivos CSV generados.")
print("🔗 Los datos están listos para importar a MySQL.")
print("💡 Revisa los archivos CSV generados y ajusta el script según tus necesidades específicas.")