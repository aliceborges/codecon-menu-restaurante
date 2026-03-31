"""
Sistema de Temas para o Cardápio Digital
"""

# Temas pré-configurados
TEMAS = {
    'sushi': {
        'nome': 'Sakura Sushi',
        'tipo_cozinha': 'Japonesa',
        'cores': {
            'primary': '#d32f2f',
            'primary_dark': '#b71c1c',
            'secondary': '#ff6b6b',
            'accent': '#ffcdd2',
            'background': '#fafafa',
            'card_bg': '#ffffff',
            'text': '#333333',
            'text_light': '#666666',
            'border': '#e0e0e0',
            'success': '#4caf50'
        },
        'fonte': 'Noto Sans JP',
        'fonte_url': 'https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap',
        'logo_emoji': '🌸',
        'icones': {
            'entradas': '🥢',
            'principais': '🍣',
            'bebidas': '🍶',
            'sobremesas': '🍡'
        },
        'imagens_default': {
            'entrada': '🍜',
            'prato': '🍱',
            'bebida': '🥤',
            'sobremesa': '🍡'
        },
        'status_labels': {
            'novo': 'Novo',
            'confirmado': 'Confirmado',
            'preparando': 'Em Preparação',
            'pronto': 'Pronto',
            'saiu_entrega': 'Saiu para Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        }
    },
    
    'churrasco': {
        'nome': 'Boi na Brasa',
        'tipo_cozinha': 'Brasileira',
        'cores': {
            'primary': '#8B4513',
            'primary_dark': '#5D2E0C',
            'secondary': '#D2691E',
            'accent': '#FFE4C4',
            'background': '#FFFAF5',
            'card_bg': '#ffffff',
            'text': '#3E2723',
            'text_light': '#6D4C41',
            'border': '#D7CCC8',
            'success': '#2E7D32'
        },
        'fonte': 'Roboto',
        'fonte_url': 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
        'logo_emoji': '🥩',
        'icones': {
            'entradas': '🥗',
            'principais': '🍖',
            'bebidas': '🍺',
            'sobremesas': '🍮'
        },
        'imagens_default': {
            'entrada': '🥗',
            'prato': '🍖',
            'bebida': '🍺',
            'sobremesa': '🍮'
        },
        'status_labels': {
            'novo': 'Novo',
            'confirmado': 'Confirmado',
            'preparando': 'Na Brasa',
            'pronto': 'Pronto',
            'saiu_entrega': 'Saiu para Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        }
    },
    
    'pizzaria': {
        'nome': 'Pizza Italia',
        'tipo_cozinha': 'Italiana',
        'cores': {
            'primary': '#E65100',
            'primary_dark': '#BF360C',
            'secondary': '#FFB74D',
            'accent': '#FFE0B2',
            'background': '#FFF8E1',
            'card_bg': '#ffffff',
            'text': '#3E2723',
            'text_light': '#6D4C41',
            'border': '#FFCC80',
            'success': '#4caf50'
        },
        'fonte': 'Lora',
        'fonte_url': 'https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&display=swap',
        'logo_emoji': '🍕',
        'icones': {
            'entradas': '🥖',
            'principais': '🍕',
            'bebidas': '🍷',
            'sobremesas': '🍰'
        },
        'imagens_default': {
            'entrada': '🥗',
            'prato': '🍕',
            'bebida': '🥤',
            'sobremesa': '🍰'
        },
        'status_labels': {
            'novo': 'Novo',
            'confirmado': 'Confirmado',
            'preparando': 'No Forno',
            'pronto': 'Pronto',
            'saiu_entrega': 'Saiu para Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        }
    },
    
    'hamburgueria': {
        'nome': 'Burger House',
        'tipo_cozinha': 'Americana',
        'cores': {
            'primary': '#FF6F00',
            'primary_dark': '#E65100',
            'secondary': '#FFD54F',
            'accent': '#FFF8E1',
            'background': '#FAFAFA',
            'card_bg': '#ffffff',
            'text': '#212121',
            'text_light': '#616161',
            'border': '#E0E0E0',
            'success': '#4caf50'
        },
        'fonte': 'Poppins',
        'fonte_url': 'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap',
        'logo_emoji': '🍔',
        'icones': {
            'entradas': '🍟',
            'principais': '🍔',
            'bebidas': '🥤',
            'sobremesas': '🍦'
        },
        'imagens_default': {
            'entrada': '🍟',
            'prato': '🍔',
            'bebida': '🥤',
            'sobremesa': '🍦'
        },
        'status_labels': {
            'novo': 'Novo',
            'confirmado': 'Confirmado',
            'preparando': 'Montando',
            'pronto': 'Pronto',
            'saiu_entrega': 'Saiu para Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        }
    }
}


class ThemeManager:
    """Gerenciador de temas do cardápio"""
    
    def __init__(self, app=None):
        self.app = app
        self.tema_atual = 'sushi'  # tema padrão
    
    def set_tema(self, tema_id):
        """Define o tema atual"""
        if tema_id in TEMAS:
            self.tema_atual = tema_id
            return True
        return False
    
    def get_tema(self, tema_id=None):
        """Retorna configuração do tema"""
        tema = tema_id or self.tema_atual
        return TEMAS.get(tema, TEMAS['sushi'])
    
    def get_css_variables(self, tema_id=None):
        """Retorna as variáveis CSS do tema"""
        tema = self.get_tema(tema_id)
        cores = tema['cores']
        
        return f"""
:root {{
    --primary: {cores['primary']};
    --primary-dark: {cores['primary_dark']};
    --secondary: {cores['secondary']};
    --accent: {cores['accent']};
    --background: {cores['background']};
    --card-bg: {cores['card_bg']};
    --text: {cores['text']};
    --text-light: {cores['text_light']};
    --border: {cores['border']};
    --success: {cores['success']};
}}
"""
    
    def listar_temas(self):
        """Retorna lista de temas disponíveis"""
        return [
            {'id': k, 'nome': v['nome'], 'tipo': v['tipo_cozinha']}
            for k, v in TEMAS.items()
        ]


# Instância global
theme_manager = ThemeManager()
