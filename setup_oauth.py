#!/usr/bin/env python3
"""
Script auxiliar para configurar Google OAuth
"""

import os
import sys

def check_env():
    """Verifica se as variaveis de ambiente estao configuradas"""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    print("=" * 60)
    print("VERIFICACAO DO GOOGLE OAUTH")
    print("=" * 60)
    
    if client_id:
        print(f"[OK] GOOGLE_CLIENT_ID: {client_id[:20]}...")
    else:
        print("[X] GOOGLE_CLIENT_ID: NAO CONFIGURADO")
    
    if client_secret:
        print(f"[OK] GOOGLE_CLIENT_SECRET: {client_secret[:15]}...")
    else:
        print("[X] GOOGLE_CLIENT_SECRET: NAO CONFIGURADO")
    
    if not client_id or not client_secret:
        print("\n" + "=" * 60)
        print("COMO CONFIGURAR:")
        print("=" * 60)
        print("""
Op 1 - Criar arquivo .env na pasta do projeto:
   
   GOOGLE_CLIENT_ID=seu_id_aqui
   GOOGLE_CLIENT_SECRET=seu_secret_aqui
   SECRET_KEY=uma_chave_qualquer

Op 2 - PowerShell:
   $env:GOOGLE_CLIENT_ID="seu_id"
   $env:GOOGLE_CLIENT_SECRET="seu_secret"
   $env:SECRET_KEY="uma_chave"

Op 3 - Windows CMD:
   set GOOGLE_CLIENT_ID=seu_id
   set GOOGLE_CLIENT_SECRET=seu_secret
   set SECRET_KEY=uma_chave

Veja o arquivo GOOGLE_OAUTH_SETUP.md para o guia completo!
""")
        return False
    
    print("\n[OK] Tudo configurado! Execute: python app.py")
    return True

if __name__ == '__main__':
    check_env()
    input("\nPressione ENTER para sair...")
