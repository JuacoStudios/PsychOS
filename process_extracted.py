"""
Script para procesar contenido extraído con PsycheOS.
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


def process_extracted_content():
    """Procesar archivos JSON extraídos."""
    
    extracted_dir = Path('data/sources/extracted')
    processed_dir = Path('data/processed')
    processed_dir.mkdir(exist_ok=True)
    
    files = list(extracted_dir.glob('*.json'))
    logger.info(f'Encontrados {len(files)} archivos para procesar')
    
    processed_files = []
    
    for file in files:
        try:
            logger.info(f'Procesando: {file.name}')
            
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraer información clave
            source_type = data.get('source_type', 'unknown')
            title = data.get('title', 'Untitled')
            content = data.get('content', {})
            
            # Crear estructura procesada
            processed_data = {
                'id': f"{source_type}_{file.stem}_{datetime.now().strftime('%Y%m%d')}",
                'source_file': file.name,
                'source_type': source_type,
                'title': title,
                'extracted_date': data.get('extracted_date', ''),
                'url': data.get('url', ''),
                'content_summary': {
                    'topics': content.get('topics', []),
                    'key_concepts': extract_key_concepts(content),
                    'main_findings': extract_main_findings(content),
                },
                'metadata': data.get('metadata', {}),
                'processing_timestamp': datetime.now().isoformat(),
                'processing_version': '1.0',
            }
            
            # Guardar archivo procesado
            output_file = processed_dir / f'processed_{file.name}'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            processed_files.append(output_file.name)
            logger.info(f'Procesado: {file.name} -> {output_file.name}')
            
        except Exception as e:
            logger.error(f'Error procesando {file.name}: {e}')
    
    return processed_files


def extract_key_concepts(content):
    """Extraer conceptos clave del contenido."""
    concepts = []
    
    # Extraer de diferentes estructuras posibles
    if isinstance(content, dict):
        # Teorías de conciencia
        if 'theory_name' in content:
            concepts.append(content['theory_name'])
        if 'proponents' in content:
            concepts.extend(content['proponents'][:3])
        if 'key_concepts' in content:
            concepts.extend(content['key_concepts'][:5])
        
        # Investigación en salud mental
        if 'topic' in content:
            concepts.append(content['topic'])
        if 'key_findings' in content:
            for finding in content['key_findings'][:3]:
                if isinstance(finding, dict) and 'finding' in finding:
                    concepts.append(finding['finding'])
        
        # Temas generales
        if 'topics' in content:
            concepts.extend(content['topics'][:5])
    
    # Eliminar duplicados y limpiar
    concepts = list(set(concepts))
    return concepts[:10]  # Limitar a 10 conceptos


def extract_main_findings(content):
    """Extraer hallazgos principales."""
    findings = []
    
    if isinstance(content, dict):
        # Para papers de investigación
        if 'key_points' in content:
            findings.extend(content['key_points'][:5])
        
        # Para actualizaciones de investigación
        if 'updates' in content:
            for update in content['updates'][:3]:
                if isinstance(update, dict) and 'summary' in update:
                    findings.append(update['summary'])
        
        # Para revisiones científicas
        if 'key_findings' in content:
            for finding in content['key_findings'][:3]:
                if isinstance(finding, dict) and 'details' in finding:
                    findings.append(f"{finding.get('finding', 'Finding')}: {finding['details']}")
    
    return findings[:5]  # Limitar a 5 hallazgos


def create_processing_report(processed_files):
    """Crear reporte de procesamiento."""
    report = {
        'processing_date': datetime.now().isoformat(),
        'total_files_processed': len(processed_files),
        'processed_files': processed_files,
        'output_directory': 'data/processed/',
        'next_steps': [
            'Usar graph/builder.py para construir grafo de conocimiento',
            'Indexar contenido para búsqueda semántica',
            'Servir a través de API REST',
        ],
    }
    
    report_file = Path('data/processed/processing_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file


def main():
    """Función principal."""
    print('PROCESANDO CONTENIDO EXTRAIDO PARA PSYCHEOS')
    print('=' * 60)
    
    processed_files = process_extracted_content()
    
    if processed_files:
        report_file = create_processing_report(processed_files)
        
        print(f'\n✅ PROCESAMIENTO COMPLETADO')
        print(f'Archivos procesados: {len(processed_files)}')
        print(f'Reporte generado: {report_file}')
        print('\nARCHIVOS PROCESADOS:')
        for file in processed_files:
            print(f'  • {file}')
        
        print('\n🎯 SIGUIENTES PASOS:')
        print('1. Construir grafo: python -m graph.builder')
        print('2. Iniciar API: uvicorn api.main:app --reload')
        print('3. Buscar contenido: python -m api.search "consciencia"')
    else:
        print('❌ No se procesaron archivos')


if __name__ == '__main__':
    main()