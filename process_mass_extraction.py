"""
Procesar extracción masiva para PsycheOS.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def process_mass_extraction():
    """Procesar todos los archivos de extracción masiva."""
    
    extracted_dir = Path('data/sources/mass_extracted')
    processed_dir = Path('data/processed/mass')
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Encontrar archivos de extracción (excluyendo reporte)
    extraction_files = [f for f in extracted_dir.glob('*.json') if 'report' not in f.name]
    
    logger.info(f'Encontrados {len(extraction_files)} archivos de extracción masiva')
    
    processed_data = []
    categories = {}
    
    for file in extraction_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determinar tipo de contenido
            content_type = data.get('type', 'unknown')
            categories[content_type] = categories.get(content_type, 0) + 1
            
            # Procesar según tipo
            processed_item = process_by_type(data, content_type)
            
            if processed_item:
                # Guardar individualmente
                output_file = processed_dir / f"processed_{file.stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_item, f, indent=2, ensure_ascii=False)
                
                processed_data.append(processed_item)
                logger.info(f'Procesado: {file.name} -> {content_type}')
            
        except Exception as e:
            logger.error(f'Error procesando {file.name}: {e}')
    
    # Crear índice consolidado
    create_consolidated_index(processed_data, processed_dir, categories)
    
    return processed_data, categories


def process_by_type(data: dict, content_type: str) -> dict:
    """Procesar datos según su tipo."""
    
    base_structure = {
        'id': data.get('extraction_id', 'unknown'),
        'source_type': 'mass_extraction',
        'original_type': content_type,
        'extraction_time': data.get('extraction_time', ''),
        'processing_time': datetime.now().isoformat(),
        'content_summary': {},
        'metadata': {
            'psycheos_compatible': data.get('psycheos_compatible', True),
            'version': data.get('version', '1.0'),
        },
    }
    
    if content_type == 'research_paper':
        return {
            **base_structure,
            'title': f"Research: {data.get('query', 'Unknown')}",
            'content_summary': {
                'topics': data.get('topics', []),
                'key_concepts': extract_paper_concepts(data),
                'year': data.get('year', 2024),
                'research_area': 'consciousness_neuroscience',
            },
        }
    
    elif content_type == 'mental_health_research':
        return {
            **base_structure,
            'title': f"Mental Health Research: {data.get('condition', 'Unknown').title()}",
            'content_summary': {
                'topics': [data.get('condition', ''), 'neuroscience', 'research'],
                'key_concepts': [
                    data.get('condition', 'mental_health'),
                    'neurobiology',
                    'brain_circuits',
                    'treatment',
                ],
                'research_area': data.get('research_area', 'neuroscience'),
                'condition': data.get('condition', ''),
            },
        }
    
    elif content_type == 'historical_theory':
        return {
            **base_structure,
            'title': f"Theory: {data.get('theory', 'Unknown')} by {data.get('theorist', 'Unknown')}",
            'content_summary': {
                'topics': ['history', 'theory', 'consciousness', data.get('field', '')],
                'key_concepts': [
                    data.get('theorist', ''),
                    data.get('theory', ''),
                    data.get('era', ''),
                    'philosophy',
                    'psychology',
                ],
                'theorist': data.get('theorist', ''),
                'theory': data.get('theory', ''),
                'era': data.get('era', ''),
                'significance': data.get('significance', 'medium'),
            },
        }
    
    elif content_type == 'mental_health_treatment':
        return {
            **base_structure,
            'title': f"Treatment: {data.get('treatment_name', 'Unknown')}",
            'content_summary': {
                'topics': ['treatment', 'therapy', data.get('treatment_type', ''), 'mental_health'],
                'key_concepts': [
                    data.get('treatment_name', ''),
                    data.get('treatment_type', ''),
                    'evidence_based',
                    data.get('evidence_level', ''),
                ],
                'treatment_name': data.get('treatment_name', ''),
                'treatment_type': data.get('treatment_type', ''),
                'evidence_level': data.get('evidence_level', ''),
                'applications': data.get('applications', []),
            },
        }
    
    else:
        # Tipo desconocido - estructura genérica
        return {
            **base_structure,
            'title': data.get('query', f"Extracted: {content_type}"),
            'content_summary': {
                'topics': ['extracted_content', content_type],
                'key_concepts': list(data.keys())[:5],
                'raw_data_preview': {k: v for k, v in list(data.items())[:3]},
            },
        }


def extract_paper_concepts(data: dict) -> list:
    """Extraer conceptos de datos de paper."""
    concepts = []
    
    query = data.get('query', '').lower()
    
    # Conceptos basados en query
    if 'consciousness' in query:
        concepts.append('consciousness')
    if 'neuroscience' in query:
        concepts.append('neuroscience')
    if 'integrated information' in query:
        concepts.append('integrated_information_theory')
        concepts.append('IIT')
    if 'global workspace' in query:
        concepts.append('global_workspace_theory')
        concepts.append('GWT')
    if 'predictive processing' in query:
        concepts.append('predictive_processing')
    if 'research' in query:
        concepts.append('scientific_research')
    
    # Añadir temas si existen
    concepts.extend(data.get('topics', []))
    
    return list(set(concepts))[:10]  # Limitar y eliminar duplicados


def create_consolidated_index(processed_data: list, output_dir: Path, categories: dict):
    """Crear índice consolidado de todo el contenido procesado."""
    
    index = {
        'metadata': {
            'total_items': len(processed_data),
            'processing_date': datetime.now().isoformat(),
            'categories': categories,
            'source': 'mass_extraction',
        },
        'items_by_category': {},
        'concept_index': {},
        'topic_index': {},
    }
    
    # Organizar por categoría
    for item in processed_data:
        category = item.get('original_type', 'unknown')
        if category not in index['items_by_category']:
            index['items_by_category'][category] = []
        
        index['items_by_category'][category].append({
            'id': item.get('id'),
            'title': item.get('title', 'Untitled'),
            'key_concepts': item.get('content_summary', {}).get('key_concepts', []),
            'topics': item.get('content_summary', {}).get('topics', []),
        })
        
        # Indexar conceptos
        for concept in item.get('content_summary', {}).get('key_concepts', []):
            if concept not in index['concept_index']:
                index['concept_index'][concept] = []
            index['concept_index'][concept].append(item.get('id'))
        
        # Indexar temas
        for topic in item.get('content_summary', {}).get('topics', []):
            if topic not in index['topic_index']:
                index['topic_index'][topic] = []
            index['topic_index'][topic].append(item.get('id'))
    
    # Guardar índice
    index_file = output_dir / "consolidated_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    logger.info(f'Índice consolidado creado: {index_file}')
    
    # Crear reporte de procesamiento
    create_processing_report(processed_data, categories, output_dir)


def create_processing_report(processed_data: list, categories: dict, output_dir: Path):
    """Crear reporte de procesamiento."""
    
    report = {
        'processing_report': {
            'total_processed': len(processed_data),
            'categories_processed': categories,
            'processing_timestamp': datetime.now().isoformat(),
            'output_directory': str(output_dir),
        },
        'statistics': {
            'total_concepts': sum(len(item.get('content_summary', {}).get('key_concepts', [])) 
                                 for item in processed_data),
            'total_topics': sum(len(item.get('content_summary', {}).get('topics', [])) 
                               for item in processed_data),
            'unique_concepts': len(set(
                concept for item in processed_data 
                for concept in item.get('content_summary', {}).get('key_concepts', [])
            )),
            'unique_topics': len(set(
                topic for item in processed_data 
                for topic in item.get('content_summary', {}).get('topics', [])
            )),
        },
        'sample_items': [
            {
                'id': item.get('id'),
                'title': item.get('title', 'Untitled'),
                'type': item.get('original_type', 'unknown'),
                'concepts_sample': item.get('content_summary', {}).get('key_concepts', [])[:3],
            }
            for item in processed_data[:5]  # Muestra de 5 items
        ],
        'next_steps': [
            'Construir grafo de conocimiento con todo el contenido',
            'Indexar para búsqueda semántica avanzada',
            'Integrar con contenido anterior de PsycheOS',
            'Servir via API REST con endpoints expandidos',
        ],
    }
    
    report_file = output_dir / "processing_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f'Reporte de procesamiento creado: {report_file}')
    
    return report_file


def main():
    """Función principal."""
    print('PROCESANDO EXTRACCION MASIVA PARA PSYCHEOS')
    print('=' * 60)
    
    processed_data, categories = process_mass_extraction()
    
    print(f'\nPROCESAMIENTO COMPLETADO')
    print(f'Items procesados: {len(processed_data)}')
    print(f'Categorias:')
    for category, count in categories.items():
        print(f'  • {category}: {count} items')
    
    # Calcular estadísticas
    total_concepts = sum(len(item.get('content_summary', {}).get('key_concepts', [])) 
                        for item in processed_data)
    total_topics = sum(len(item.get('content_summary', {}).get('topics', [])) 
                      for item in processed_data)
    
    print(f'\nESTADISTICAS:')
    print(f'Conceptos totales extraidos: {total_concepts}')
    print(f'Temas totales identificados: {total_topics}')
    
    # Mostrar muestra
    print(f'\nMUESTRA DE CONTENIDO PROCESADO:')
    for i, item in enumerate(processed_data[:3], 1):
        print(f'{i}. {item.get("title", "Untitled")}')
        print(f'   Tipo: {item.get("original_type", "unknown")}')
        concepts = item.get('content_summary', {}).get('key_concepts', [])[:3]
        if concepts:
            print(f'   Conceptos: {", ".join(concepts)}')
        print()
    
    print('=' * 60)
    print('¡CONTENIDO MASIVO PROCESADO EXITOSAMENTE!')
    print(f'Directorio: data/processed/mass/')
    print('\nPsycheOS ahora tiene una base de conocimiento expandida significativamente.')
    print('Listo para construir un grafo de conocimiento masivo.')


if __name__ == '__main__':
    main()