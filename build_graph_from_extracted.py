"""
Construir grafo de conocimiento a partir del contenido extraído.
"""

import json
import logging
from pathlib import Path

# Importar módulos de PsycheOS
try:
    from graph.builder import KnowledgeGraphBuilder
    from graph.relations import RelationshipType
    logger = logging.getLogger(__name__)
except ImportError as e:
    print(f"Error importando módulos de PsycheOS: {e}")
    print("Asegúrate de que los módulos estén correctamente instalados.")
    exit(1)


def load_processed_files():
    """Cargar archivos procesados."""
    processed_dir = Path('data/processed')
    processed_files = []
    
    for file in processed_dir.glob('processed_*.json'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            processed_files.append((file, data))
            logger.info(f'Cargado: {file.name}')
        except Exception as e:
            logger.error(f'Error cargando {file.name}: {e}')
    
    return processed_files


def extract_entities_from_content(content_data):
    """Extraer entidades del contenido procesado."""
    entities = []
    
    # Extraer del contenido procesado
    content_summary = content_data.get('content_summary', {})
    
    # Conceptos clave
    concepts = content_summary.get('key_concepts', [])
    for concept in concepts:
        if concept:  # Evitar strings vacíos
            entities.append({
                'id': f"concept_{hash(concept) % 1000000}",
                'name': concept,
                'type': 'concept',
                'source': content_data.get('source_file', 'unknown'),
            })
    
    # Temas
    topics = content_summary.get('topics', [])
    for topic in topics:
        if topic and topic not in concepts:  # Evitar duplicados
            entities.append({
                'id': f"topic_{hash(topic) % 1000000}",
                'name': topic,
                'type': 'topic',
                'source': content_data.get('source_file', 'unknown'),
            })
    
    # Documento principal
    title = content_data.get('title', 'Untitled')
    entities.append({
        'id': f"doc_{content_data.get('id', 'unknown')}",
        'name': title,
        'type': 'document',
        'source_type': content_data.get('source_type', 'unknown'),
        'url': content_data.get('url', ''),
    })
    
    return entities


def extract_relationships(entities, content_data):
    """Extraer relaciones entre entidades."""
    relationships = []
    
    # Obtener el documento principal
    doc_entity = next((e for e in entities if e['type'] == 'document'), None)
    if not doc_entity:
        return relationships
    
    doc_id = doc_entity['id']
    
    # Relaciones documento -> conceptos
    concept_entities = [e for e in entities if e['type'] == 'concept']
    for concept in concept_entities:
        relationships.append({
            'source': doc_id,
            'target': concept['id'],
            'type': RelationshipType.RELATED_TO.value,
            'weight': 0.8,
            'description': f"Documento menciona concepto: {concept['name']}",
        })
    
    # Relaciones documento -> temas
    topic_entities = [e for e in entities if e['type'] == 'topic']
    for topic in topic_entities:
        relationships.append({
            'source': doc_id,
            'target': topic['id'],
            'type': RelationshipType.RELATED_TO.value,
            'weight': 0.9,
            'description': f"Documento trata sobre tema: {topic['name']}",
        })
    
    # Relaciones entre conceptos relacionados (simplificado)
    if len(concept_entities) > 1:
        for i in range(len(concept_entities) - 1):
            for j in range(i + 1, len(concept_entities)):
                relationships.append({
                    'source': concept_entities[i]['id'],
                    'target': concept_entities[j]['id'],
                    'type': RelationshipType.RELATED_TO.value,
                    'weight': 0.6,
                    'description': f"Conceptos relacionados: {concept_entities[i]['name']} <-> {concept_entities[j]['name']}",
                })
    
    return relationships


def build_knowledge_graph():
    """Construir grafo de conocimiento."""
    print('CONSTRUYENDO GRAFO DE CONOCIMIENTO PARA PSYCHEOS')
    print('=' * 60)
    
    # Cargar archivos procesados
    processed_files = load_processed_files()
    print(f'Archivos procesados cargados: {len(processed_files)}')
    
    if not processed_files:
        print('No hay archivos procesados para construir el grafo.')
        return None
    
    # Inicializar constructor de grafo
    builder = KnowledgeGraphBuilder()
    
    all_entities = []
    all_relationships = []
    
    # Procesar cada archivo
    for file_path, content_data in processed_files:
        print(f'Procesando: {file_path.name}')
        
        # Extraer entidades
        entities = extract_entities_from_content(content_data)
        all_entities.extend(entities)
        
        # Extraer relaciones
        relationships = extract_relationships(entities, content_data)
        all_relationships.extend(relationships)
        
        print(f'  • Entidades extraídas: {len(entities)}')
        print(f'  • Relaciones extraídas: {len(relationships)}')
    
    # Construir grafo
    print('\nConstruyendo grafo...')
    
    # Añadir entidades
    for entity in all_entities:
        builder.add_node(
            node_id=entity['id'],
            label=entity['name'],
            node_type=entity['type'],
            attributes={
                'source': entity.get('source', ''),
                'source_type': entity.get('source_type', ''),
                'url': entity.get('url', ''),
            }
        )
    
    # Añadir relaciones
    for rel in all_relationships:
        builder.add_relationship(
            source_id=rel['source'],
            target_id=rel['target'],
            rel_type=rel['type'],
            weight=rel['weight'],
            description=rel['description']
        )
    
    # Obtener grafo
    graph = builder.get_graph()
    
    # Estadísticas
    print('\nESTADISTICAS DEL GRAFO:')
    print(f'Nodos totales: {graph.number_of_nodes()}')
    print(f'Relaciones totales: {graph.number_of_edges()}')
    
    # Contar por tipo
    node_types = {}
    for _, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print('\nTIPOS DE NODOS:')
    for node_type, count in node_types.items():
        print(f'  • {node_type}: {count}')
    
    # Guardar grafo
    output_file = Path('data/graph/extracted_knowledge_graph.graphml')
    output_file.parent.mkdir(exist_ok=True)
    
    builder.save_graph(str(output_file), format='graphml')
    print(f'\nGrafo guardado en: {output_file}')
    
    # Exportar para visualización
    viz_file = Path('data/graph/extracted_graph_visualization.json')
    try:
        from graph.visualizer import GraphVisualizer
        visualizer = GraphVisualizer(graph)
        visualizer.export_for_d3(str(viz_file))
        print(f'Visualización exportada: {viz_file}')
    except ImportError:
        print('Nota: Módulo de visualización no disponible')
    
    return graph


def main():
    """Función principal."""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    graph = build_knowledge_graph()
    
    if graph:
        print('\nGRAFO CONSTRUIDO EXITOSAMENTE!')
        print('\nPuedes:')
        print('1. Visualizar el grafo: Abrir data/graph/extracted_graph_visualization.json en navegador')
        print('2. Consultar el grafo: Usar graph/visualizer.py para análisis')
        print('3. Servir via API: uvicorn api.main:app --reload')
        print('4. Buscar contenido: python -m api.search "consciencia"')
    else:
        print('\nNo se pudo construir el grafo.')


if __name__ == '__main__':
    main()