import os
import hashlib

def gerar():
    xml = u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
    
    # Procura por pastas que contenham addon.xml
    for pasta in os.listdir('.'):
        arquivo_xml = os.path.join(pasta, 'addon.xml')
        if os.path.exists(arquivo_xml):
            with open(arquivo_xml, 'r', encoding='utf-8') as f:
                # Remove o cabeçalho do XML original para juntar tudo
                conteudo = f.read().split('?>')[-1].strip()
                xml += conteudo + '\n'
    
    xml += u'\n</addons>'
    
    # Salva o addons.xml
    with open('addons.xml', 'w', encoding='utf-8') as f:
        f.write(xml)
        
    # Gera o MD5 (o que o Kodi usa para saber se tem atualização)
    md5 = hashlib.md5(xml.encode('utf-8')).hexdigest()
    with open('addons.xml.md5', 'w') as f:
        f.write(md5)
        
    print("Sucesso! Arquivos addons.xml e addons.xml.md5 criados.")

if __name__ == '__main__':
    gerar()