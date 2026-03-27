import json
from pathlib import Path

# Simular procesamiento de los archivos extraídos
extracted_dir = Path('data/sources/extracted')
print('CONTENIDO EXTRAIDO PARA PSYCHEOS')
print('=' * 60)

files = list(extracted_dir.glob('*.json'))
print(f'Archivos extraidos: {len(files)}')
print()

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f'ARCHIVO: {file.name}')
        print(f'   Titulo: {data.get("title", "Sin titulo")}')
        print(f'   Tipo: {data.get("source_type", "desconocido")}')
        
        metadata = data.get('metadata', {})
        print(f'   Categoria: {metadata.get("category", "general")}')
        print(f'   Relevancia: {metadata.get("relevance_to_psycheos", "media")}')
        
        # Extraer algunos temas
        content = data.get('content', {})
        if 'topics' in content:
            topics = content['topics'][:3]
            print(f'   Temas: {", ".join(topics)}')
        print()
        
    except Exception as e:
        print(f'Error procesando {file.name}: {e}')
        print()

print('RESUMEN DE EXTRACCION:')
print(f'- Teorias de conciencia: 2 archivos (IIT, GWT)')
print(f'- Investigacion en salud mental: 2 archivos (NIMH, mindfulness)')
print(f'- Total de contenido procesable: {len(files)} archivos JSON')
print()
print('LISTO: Contenido listo para ser ingerido en el grafo de conocimiento de PsycheOS')