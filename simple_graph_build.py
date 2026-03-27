"""
Script simplificado para construir grafo de conocimiento.
"""

import json
from pathlib import Path

print('CONSTRUYENDO GRAFO DE CONOCIMIENTO SIMPLIFICADO')
print('=' * 60)

# Cargar archivos procesados
processed_dir = Path('data/processed')
processed_files = list(processed_dir.glob('processed_*.json'))

print(f'Archivos procesados encontrados: {len(processed_files)}')

# Crear datos para el grafo
all_data = []

for file in processed_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraer información clave
        doc_id = data.get('id', file.stem)
        title = data.get('title', 'Untitled')
        source_type = data.get('source_type', 'unknown')
        
        content_summary = data.get('content_summary', {})
        topics = content_summary.get('topics', [])
        concepts = content_summary.get('key_concepts', [])
        
        print(f'\nARCHIVO: {file.name}')
        print(f'   Titulo: {title}')
        print(f'   Temas: {", ".join(topics[:3])}')
        print(f'   Conceptos: {", ".join(concepts[:3])}')
        
        # Añadir a datos
        all_data.append({
            'id': doc_id,
            'title': title,
            'source_type': source_type,
            'topics': topics,
            'concepts': concepts,
            'file': file.name,
        })
        
    except Exception as e:
        print(f'Error procesando {file.name}: {e}')

# Crear estructura de grafo simple
graph_data = {
    'nodes': [],
    'edges': [],
    'metadata': {
        'total_documents': len(all_data),
        'total_concepts': sum(len(d['concepts']) for d in all_data),
        'total_topics': sum(len(d['topics']) for d in all_data),
    }
}

# Añadir nodos de documentos
for doc in all_data:
    graph_data['nodes'].append({
        'id': doc['id'],
        'label': doc['title'],
        'type': 'document',
        'source_type': doc['source_type'],
    })

# Añadir nodos de conceptos y temas (evitando duplicados)
all_concepts = set()
all_topics = set()

for doc in all_data:
    all_concepts.update(doc['concepts'])
    all_topics.update(doc['topics'])

for concept in all_concepts:
    if concept:  # Evitar strings vacíos
        graph_data['nodes'].append({
            'id': f'concept_{hash(concept) % 1000000}',
            'label': concept,
            'type': 'concept',
        })

for topic in all_topics:
    if topic and topic not in all_concepts:  # Evitar duplicados
        graph_data['nodes'].append({
            'id': f'topic_{hash(topic) % 1000000}',
            'label': topic,
            'type': 'topic',
        })

# Añadir relaciones
for doc in all_data:
    doc_id = doc['id']
    
    # Documento -> Conceptos
    for concept in doc['concepts']:
        if concept:
            concept_id = f'concept_{hash(concept) % 1000000}'
            graph_data['edges'].append({
                'source': doc_id,
                'target': concept_id,
                'type': 'mentions',
                'weight': 0.8,
            })
    
    # Documento -> Temas
    for topic in doc['topics']:
        if topic:
            topic_id = f'topic_{hash(topic) % 1000000}'
            graph_data['edges'].append({
                'source': doc_id,
                'target': topic_id,
                'type': 'about',
                'weight': 0.9,
            })

# Guardar grafo
graph_dir = Path('data/graph')
graph_dir.mkdir(exist_ok=True)

output_file = graph_dir / 'simple_knowledge_graph.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(graph_data, f, indent=2, ensure_ascii=False)

print('\n' + '=' * 60)
print('GRAFO CONSTRUIDO EXITOSAMENTE')
print(f'Nodos totales: {len(graph_data["nodes"])}')
print(f'Relaciones totales: {len(graph_data["edges"])}')
print(f'Documentos: {graph_data["metadata"]["total_documents"]}')
print(f'Conceptos unicos: {len(all_concepts)}')
print(f'Temas unicos: {len(all_topics)}')
print(f'\nGrafo guardado en: {output_file}')

# Mostrar resumen
print('\nRESUMEN DEL CONTENIDO:')
print('Documentos procesados:')
for doc in all_data:
    print(f'  • {doc["title"]}')
    print(f'    Temas: {", ".join(doc["topics"][:2])}')

print('\nConceptos clave identificados:')
for i, concept in enumerate(list(all_concepts)[:10], 1):
    print(f'  {i}. {concept}')

print('\nSIGUIENTES PASOS:')
print('1. Visualizar grafo: Abre el archivo JSON en un visualizador de grafos')
print('2. Iniciar API: uvicorn api.main:app --reload')
print('3. Buscar contenido: Usa el modulo de busqueda')
print('4. Extraer mas contenido: Continua con YouTube, podcasts, etc.')