#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile
import os
import shutil
import unicodedata
import re

def sanitize_filename(filename):
    """Sanitiza nome de arquivo removendo caracteres problemáticos"""
    # Remove caracteres de controle e substitui caracteres problemáticos
    filename = unicodedata.normalize('NFKD', filename)
    filename = re.sub(r'[^\w\s\-_\.]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-_')

def extract_rag_zip():
    """Extrai o arquivo ZIP do RAG Tributária"""
    zip_path = '/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/rag_tributaria.zip'
    extract_path = '/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/rag_docs'
    
    # Cria diretório de destino
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    os.makedirs(extract_path, exist_ok=True)
    
    extracted_files = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                try:
                    # Tenta diferentes encodings
                    for encoding in ['utf-8', 'cp437', 'latin1', 'cp1252']:
                        try:
                            if isinstance(member, str):
                                safe_name = member
                            else:
                                safe_name = member.encode('cp437').decode(encoding, errors='replace')
                            break
                        except:
                            continue
                    
                    # Sanitiza o nome do arquivo
                    safe_name = os.path.basename(safe_name)  # Remove caminho
                    safe_name = sanitize_filename(safe_name)
                    
                    if not safe_name or safe_name == '.':
                        safe_name = f'documento_{len(extracted_files)}'
                    
                    # Define extensão se não tiver
                    if '.' not in safe_name:
                        # Verifica se é PDF pelo conteúdo
                        content = zip_ref.read(member)
                        if content.startswith(b'%PDF'):
                            safe_name += '.pdf'
                        else:
                            safe_name += '.txt'
                    
                    target_path = os.path.join(extract_path, safe_name)
                    
                    # Evita sobrescrever arquivos
                    counter = 1
                    original_path = target_path
                    while os.path.exists(target_path):
                        name, ext = os.path.splitext(original_path)
                        target_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # Extrai o arquivo
                    with zip_ref.open(member) as source:
                        content = source.read()
                        with open(target_path, 'wb') as target:
                            target.write(content)
                    
                    extracted_files.append(safe_name)
                    print(f"✅ Extraído: {safe_name}")
                    
                except Exception as e:
                    print(f"❌ Erro ao extrair {member}: {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Erro ao abrir ZIP: {e}")
        return False
    
    print(f"\n🎉 Extração concluída! {len(extracted_files)} arquivos extraídos em:")
    print(f"📁 {extract_path}")
    print("\n📋 Arquivos extraídos:")
    for file in extracted_files:
        print(f"  • {file}")
    
    return True

if __name__ == "__main__":
    extract_rag_zip()