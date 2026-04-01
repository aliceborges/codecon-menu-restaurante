from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for
from models import db, Configuracao, Restaurante, Categoria, Item, Complemento, Pedido, PedidoItem, AvaliacaoRestaurante, AvaliacaoItem, Usuario
from themes import theme_manager, TEMAS
from authlib.integrations.flask_client import OAuth
from datetime import datetime
from dotenv import load_dotenv
import json
import os

# Carregar variaveis do arquivo .env
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurante2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'restaurante-secret-key-2024')

db.init_app(app)

# Configuração OAuth Google
oauth = OAuth(app)

# Configuração do Google OAuth
# Nota: Em produção, use variáveis de ambiente
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    google = oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
    )


# ==================== FUNÇÕES AUXILIARES ====================

def get_tema_atual():
    """Retorna o tema atual - FIXO CHURRASCO"""
    return theme_manager.get_tema('churrasco')


def get_hora_atual():
    """Retorna hora atual ou simulada para testes"""
    hora_simulada = Configuracao.get_hora_simulada()
    if hora_simulada:
        return datetime.strptime(hora_simulada, '%H:%M')
    return datetime.now()


def get_tipo_cardapio():
    """Retorna qual cardápio está ativo baseado no horário"""
    hora_atual = get_hora_atual()
    hora = hora_atual.hour
    
    if 11 <= hora < 15:
        return 'almoco'
    elif 18 <= hora < 23:
        return 'jantar'
    else:
        return 'fechado'


def get_menu_data():
    """Retorna os dados do restaurante e cardápio filtrado por horário"""
    restaurante = Restaurante.query.first()
    tipo_cardapio = get_tipo_cardapio()
    
    if tipo_cardapio == 'fechado':
        categorias = []
    else:
        query = Categoria.query.order_by(Categoria.ordem)
        if tipo_cardapio == 'almoco':
            query = query.filter(Categoria.horario.in_(['almoco', 'todos']))
        elif tipo_cardapio == 'jantar':
            query = query.filter(Categoria.horario.in_(['jantar', 'todos']))
        categorias = query.all()
    
    return {
        'restaurante': restaurante.to_dict() if restaurante else {},
        'categorias': [c.to_dict() for c in categorias],
        'tema': get_tema_atual(),
        'horario': {
            'tipo': tipo_cardapio,
            'hora_atual': get_hora_atual().strftime('%H:%M'),
            'mensagem': {
                'almoco': 'Almoço Executivo (11h às 15h)',
                'jantar': 'Espeto Corrido (18h às 23h)',
                'fechado': 'Restaurante Fechado'
            }.get(tipo_cardapio)
        }
    }


def login_required(f):
    """Decorator para verificar se usuário está logado"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Retorna usuário atual logado"""
    if 'user_id' in session:
        user = Usuario.query.get(session['user_id'])
        print(f"[DEBUG] get_current_user: user_id={session['user_id']}, user={user}")
        return user
    print(f"[DEBUG] get_current_user: user_id não na sessão")
    return None


# ==================== SEED DATABASE ====================

def _complementos_acai_para_item(item_id):
    """Complementos típicos de açaí; IDs únicos por item (coluna id ≤ 20 chars)."""
    defs = [
        ('lc', 'Leite condensado', 2.00),
        ('lp', 'Leite em pó', 2.00),
        ('gr', 'Granola', 2.00),
        ('pac', 'Paçoca', 2.50),
        ('ban', 'Banana', 1.50),
        ('mor', 'Morango', 3.50),
        ('nut', 'Nutella', 5.00),
        ('nin', 'Creme Ninho', 3.50),
        ('bis', 'Bis (2 unidades)', 2.50),
        ('ovo', 'Ovomaltine', 3.00),
        ('am', 'Amendoim', 1.50),
        ('mel', 'Mel', 1.00),
    ]
    return [
        {'id': f'a{item_id}-{k}', 'nome': nome, 'preco': preco}
        for k, nome, preco in defs
    ]


def get_acai_categoria_data():
    """Categoria Açaí: copos por tamanho + copos montados, todos com complementos opcionais."""
    comp = _complementos_acai_para_item
    return {
        'id': 'acai',
        'nome': 'Açaí — Copos montados',
        'ordem': 7,
        'icone': '🫐',
        'horario': 'todos',
        'itens': [
            {
                'id': 24,
                'nome': 'Copo Açaí 300 ml',
                'descricao': 'Açaí na medida; monte com os complementos de sua preferência.',
                'preco': 14.90,
                'imagem': '🫐',
                'complementos': comp(24),
            },
            {
                'id': 25,
                'nome': 'Copo Açaí 500 ml',
                'descricao': 'Porção generosa; ideal para combinar vários complementos.',
                'preco': 19.90,
                'imagem': '🫐',
                'complementos': comp(25),
            },
            {
                'id': 26,
                'nome': 'Copo Açaí 700 ml',
                'descricao': 'Tamanho família; monte do seu jeito.',
                'preco': 24.90,
                'imagem': '🫐',
                'complementos': comp(26),
            },
            {
                'id': 27,
                'nome': 'Copo Montado Tradicional',
                'descricao': '300 ml com banana, granola e mel já inclusos. Pode adicionar extras.',
                'preco': 17.90,
                'imagem': '🍌',
                'complementos': comp(27),
            },
            {
                'id': 28,
                'nome': 'Copo Montado Premium',
                'descricao': '500 ml com leite condensado, leite em pó, paçoca e granola inclusos.',
                'preco': 26.90,
                'imagem': '✨',
                'complementos': comp(28),
            },
            {
                'id': 29,
                'nome': 'Copo Montado Nutella',
                'descricao': '500 ml com Nutella, morango e granola na montagem.',
                'preco': 28.90,
                'imagem': '🍫',
                'complementos': comp(29),
            },
        ],
    }


def _persist_categoria_cardapio(cat_data):
    """Insere uma categoria e seus itens/complementos (sem commit)."""
    categoria = Categoria(
        id=cat_data['id'],
        nome=cat_data['nome'],
        ordem=cat_data['ordem'],
        icone=cat_data['icone'],
        horario=cat_data['horario'],
    )
    db.session.add(categoria)
    for item_data in cat_data['itens']:
        item = Item(
            id=item_data['id'],
            categoria_id=categoria.id,
            nome=item_data['nome'],
            descricao=item_data['descricao'],
            preco=item_data['preco'],
            imagem=item_data['imagem'],
        )
        db.session.add(item)
        for comp_data in item_data.get('complementos', []):
            db.session.add(
                Complemento(
                    id=comp_data['id'],
                    item_id=item.id,
                    nome=comp_data['nome'],
                    preco=comp_data['preco'],
                )
            )


def ensure_acai_menu():
    """Garante a categoria Açaí em bancos já existentes (seed antigo sem açaí)."""
    if Categoria.query.filter_by(id='acai').first():
        return
    _persist_categoria_cardapio(get_acai_categoria_data())
    db.session.commit()
    print('Cardápio de Açaí adicionado ao banco.')


def seed_database():
    """Popula o banco com dados iniciais se estiver vazio"""
    
    if not Configuracao.query.filter_by(chave='tema_atual').first():
        config = Configuracao(chave='tema_atual', valor='churrasco')
        db.session.add(config)
    
    if not Restaurante.query.first():
        restaurante = Restaurante(
            nome="Boi na Brasa",
            descricao="O melhor churrasco da cidade, na brasa com carvão",
            endereco="Rua das Flores, 123 - Centro",
            telefone="(11) 3456-7890",
            horario="Almoço: 11h-15h | Jantar: 18h-23h",
            logo="/static/images/logo.png",
            tema="churrasco"
        )
        db.session.add(restaurante)
        
        seed_churrasco_data()
        
        db.session.commit()
        print("Banco de dados populado com dados iniciais (Churrasco)!")
    
    ensure_acai_menu()


def seed_churrasco_data():
    """Dados do tema Churrasco com horários"""
    
    dados_categorias = [
        {
            'id': 'executivo',
            'nome': 'Almoço Executivo',
            'ordem': 1,
            'icone': '🍽️',
            'horario': 'almoco',
            'itens': [
                {'id': 1, 'nome': 'Executivo Picanha', 'descricao': 'Picanha grelhada + arroz + feijão + salada + batata', 'preco': 35.90, 'imagem': '🥩'},
                {'id': 2, 'nome': 'Executivo Contrafilé', 'descricao': 'Contrafilé grelhado + arroz + feijão + salada', 'preco': 29.90, 'imagem': '🍖'},
                {'id': 3, 'nome': 'Executivo Frango', 'descricao': 'Peito de frango grelhado + arroz + feijão + salada', 'preco': 26.90, 'imagem': '🍗'},
                {'id': 4, 'nome': 'Executivo Linguiça', 'descricao': 'Linguiça artesanal + arroz + feijão + salada', 'preco': 24.90, 'imagem': '🌭'}
            ]
        },
        {
            'id': 'entradas',
            'nome': 'Entradas',
            'ordem': 2,
            'icone': '🥗',
            'horario': 'todos',
            'itens': [
                {'id': 5, 'nome': 'Pão de Alho', 'descricao': 'Pão francês com manteiga de alho e ervas', 'preco': 12.90, 'imagem': '🍞'},
                {'id': 6, 'nome': 'Vinagrete', 'descricao': 'Vinagrete tradicional com legumes frescos', 'preco': 8.90, 'imagem': '🥣'},
                {'id': 7, 'nome': 'Salada Caesar', 'descricao': 'Alface, croutons, parmesão e molho caesar', 'preco': 18.90, 'imagem': '🥗'}
            ]
        },
        {
            'id': 'espetos',
            'nome': 'Espetos - Espeto Corrido',
            'ordem': 3,
            'icone': '🍢',
            'horario': 'jantar',
            'itens': [
                {'id': 8, 'nome': 'Espeto de Picanha', 'descricao': 'Espeto de picanha nobre (300g)', 'preco': 42.90, 'imagem': '🥩'},
                {'id': 9, 'nome': 'Espeto de Alcatra', 'descricao': 'Espeto de alcatra com cebola (300g)', 'preco': 38.90, 'imagem': '🍖'},
                {'id': 10, 'nome': 'Espeto de Fraldinha', 'descricao': 'Espeto de fraldinha na brasa (300g)', 'preco': 36.90, 'imagem': '🥩'},
                {'id': 11, 'nome': 'Espeto de Coração', 'descricao': 'Espeto de coração de frango (6 un)', 'preco': 24.90, 'imagem': '🍢'},
                {'id': 12, 'nome': 'Espeto de Linguiça', 'descricao': 'Espeto de linguiça artesanal (2 un)', 'preco': 22.90, 'imagem': '🌭'},
                {'id': 13, 'nome': 'Espeto Misto', 'descricao': 'Picanha, alcatra e linguiça (400g)', 'preco': 48.90, 'imagem': '🍖'}
            ]
        },
        {
            'id': 'acompanhamentos',
            'nome': 'Acompanhamentos',
            'ordem': 4,
            'icone': '🍚',
            'horario': 'todos',
            'itens': [
                {'id': 14, 'nome': 'Arroz Carreteiro', 'descricao': 'Arroz com carne seca e linguiça', 'preco': 32.90, 'imagem': '🍚'},
                {'id': 15, 'nome': 'Batata Frita', 'descricao': 'Porção de batata frita crocante', 'preco': 18.90, 'imagem': '🍟',
                 'complementos': [
                     {'id': 'c1-15', 'nome': 'Cheddar e Bacon', 'preco': 8.00}
                 ]},
                {'id': 16, 'nome': 'Mandioca Frita', 'descricao': 'Porção de mandioca frita', 'preco': 16.90, 'imagem': '🥔'},
                {'id': 17, 'nome': 'Queijo Coalho', 'descricao': 'Espeto de queijo coalho (4 un)', 'preco': 22.90, 'imagem': '🧀'}
            ]
        },
        {
            'id': 'bebidas',
            'nome': 'Bebidas',
            'ordem': 5,
            'icone': '🍺',
            'horario': 'todos',
            'itens': [
                {'id': 18, 'nome': 'Cerveja Artesanal', 'descricao': 'Cerveja artesanal IPA ou Pilsen (500ml)', 'preco': 16.90, 'imagem': '🍺'},
                {'id': 19, 'nome': 'Refrigerante', 'descricao': 'Coca, Guaraná ou Sprite (350ml)', 'preco': 7.00, 'imagem': '🥤'},
                {'id': 20, 'nome': 'Suco Natural', 'descricao': 'Laranja, Limão ou Maracujá (500ml)', 'preco': 12.90, 'imagem': '🧃'},
                {'id': 21, 'nome': 'Água', 'descricao': 'Água mineral sem gás (500ml)', 'preco': 4.50, 'imagem': '💧'}
            ]
        },
        {
            'id': 'sobremesas',
            'nome': 'Sobremesas',
            'ordem': 6,
            'icone': '🍮',
            'horario': 'todos',
            'itens': [
                {'id': 22, 'nome': 'Pudim de Leite', 'descricao': 'Pudim de leite condensado com calda', 'preco': 14.90, 'imagem': '🍮'},
                {'id': 23, 'nome': 'Mousse de Maracujá', 'descricao': 'Mousse com calda de maracujá', 'preco': 12.90, 'imagem': '🍨'}
            ]
        }
    ]
    
    dados_categorias.append(get_acai_categoria_data())
    
    for cat_data in dados_categorias:
        _persist_categoria_cardapio(cat_data)


# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/login')
def login():
    """Tela de login com Google"""
    user = get_current_user()
    return render_template('login.html', tema=get_tema_atual(), user=user)


@app.route('/auth/google')
def auth_google():
    """Inicia autenticação com Google"""
    if not GOOGLE_CLIENT_ID:
        return 'Google OAuth não configurado. Defina GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET.', 500
    
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/callback')
def auth_callback():
    """Callback após autenticação Google"""
    print(f"[DEBUG] Callback chamado! Args: {request.args}")
    try:
        print("[DEBUG] Tentando authorize_access_token...")
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        
        # Buscar ou criar usuário
        usuario = Usuario.query.filter_by(google_id=user_info['sub']).first()
        
        if not usuario:
            usuario = Usuario(
                google_id=user_info['sub'],
                email=user_info['email'],
                nome=user_info.get('name', user_info['email']),
                foto=user_info.get('picture', '')
            )
            db.session.add(usuario)
        else:
            usuario.last_login = datetime.now()
        
        db.session.commit()
        
        # Salvar na sessão
        session['user_id'] = usuario.id
        session['user_name'] = usuario.nome
        session['user_email'] = usuario.email
        session['user_foto'] = usuario.foto
        
        print(f"[DEBUG] Usuario logado: {usuario.nome} (ID: {usuario.id})")
        print(f"[DEBUG] Session: {dict(session)}")
        
        # Redirecionar para página anterior ou home
        next_page = request.args.get('next') or url_for('index')
        return redirect(next_page)
        
    except Exception as e:
        import traceback
        print(f"[ERRO] OAuth Exception: {e}")
        print(f"[ERRO] Traceback: {traceback.format_exc()}")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/api/user')
def api_user():
    """Retorna dados do usuário logado"""
    user = get_current_user()
    if user:
        return jsonify({
            'logged_in': True,
            'user': user.to_dict()
        })
    return jsonify({'logged_in': False})


@app.route('/debug/session')
def debug_session():
    """Debug da sessão"""
    return jsonify({
        'session': dict(session),
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name'),
        'user_email': session.get('user_email')
    })


# ==================== ROTAS DO CLIENTE ====================

@app.route('/')
def index():
    data = get_menu_data()
    user = get_current_user()
    return render_template('index.html',
                         restaurante=data['restaurante'],
                         categorias=data['categorias'],
                         tema=data['tema'],
                         horario=data['horario'],
                         user=user)


@app.route('/carrinho')
def cart():
    if get_tipo_cardapio() == 'fechado':
        return render_template('fechado.html', tema=get_tema_atual(), horario=get_hora_atual().strftime('%H:%M'))
    user = get_current_user()
    return render_template('cart.html', tema=get_tema_atual(), user=user)


@app.route('/dados')
def user():
    if get_tipo_cardapio() == 'fechado':
        return render_template('fechado.html', tema=get_tema_atual(), horario=get_hora_atual().strftime('%H:%M'))
    user = get_current_user()
    return render_template('user.html', tema=get_tema_atual(), user=user)


@app.route('/pagamento')
def payment():
    if get_tipo_cardapio() == 'fechado':
        return render_template('fechado.html', tema=get_tema_atual(), horario=get_hora_atual().strftime('%H:%M'))
    user = get_current_user()
    return render_template('payment.html', tema=get_tema_atual(), user=user)


@app.route('/confirmacao')
def confirmation():
    order_id = request.args.get('pedido', 0)
    user = get_current_user()
    return render_template('confirmation.html', pedido_id=order_id, tema=get_tema_atual(), user=user)


@app.route('/acompanhar')
def track_order():
    order_id = request.args.get('pedido')
    user = get_current_user()
    return render_template('track.html', pedido_id=order_id, tema=get_tema_atual(), user=user)


@app.route('/historico')
def order_history():
    user = get_current_user()
    return render_template('history.html', tema=get_tema_atual(), user=user)


@app.route('/avaliar')
@login_required
def rate_order():
    """Avaliação - SÓ PODE AVALIAR SE ESTIVER LOGADO"""
    order_id = request.args.get('pedido')
    user = get_current_user()
    return render_template('rate.html', pedido_id=order_id, tema=get_tema_atual(), user=user)


@app.route('/admin')
def admin_panel():
    """Painel de administração para testar horário"""
    return render_template('admin.html')


# ==================== CSS DINÂMICO ====================

@app.route('/theme.css')
def theme_css():
    """Retorna o CSS dinâmico baseado no tema atual"""
    css = theme_manager.get_css_variables('churrasco')
    return Response(css, mimetype='text/css')


# ==================== API ENDPOINTS ====================

@app.route('/api/dados', methods=['GET'])
def get_data():
    return jsonify(get_menu_data())


@app.route('/api/hora', methods=['GET', 'POST'])
def simular_hora():
    """GET: retorna hora atual/simulada | POST: simula hora"""
    if request.method == 'GET':
        return jsonify({
            'hora_atual': get_hora_atual().strftime('%H:%M'),
            'tipo_cardapio': get_tipo_cardapio(),
            'hora_simulada': Configuracao.get_hora_simulada()
        })
    
    elif request.method == 'POST':
        data = request.json
        hora = data.get('hora')
        
        if hora:
            Configuracao.set_hora_simulada(hora)
        else:
            config = Configuracao.query.filter_by(chave='hora_simulada').first()
            if config:
                db.session.delete(config)
                db.session.commit()
        
        return jsonify({
            'success': True,
            'hora': hora,
            'mensagem': 'Hora atualizada. Recarregue a página (F5).'
        })


@app.route('/api/pedido', methods=['POST'])
def create_order():
    if get_tipo_cardapio() == 'fechado':
        return jsonify({'success': False, 'error': 'Restaurante fechado'}), 403
    
    data = request.json
    user = get_current_user()
    
    try:
        pedido = Pedido(
            nome=data['cliente']['nome'],
            telefone=data['cliente']['telefone'],
            endereco=data['cliente']['endereco'],
            complemento=data['cliente'].get('complemento', ''),
            observacoes=data['cliente'].get('observacoes', ''),
            usuario_id=user.id if user else None,
            metodo_pagamento=data['pagamento']['metodo'],
            troco=data['pagamento'].get('troco'),
            subtotal=data['valores']['subtotal'],
            taxa_entrega=data['valores']['entrega'],
            total=data['valores']['total'],
            status='novo'
        )
        
        db.session.add(pedido)
        db.session.flush()
        
        for item_data in data['itens']:
            item = PedidoItem(
                pedido_id=pedido.id,
                item_id=item_data['itemId'],
                nome=item_data['nome'],
                preco_unitario=item_data['preco'],
                quantidade=item_data['quantidade'],
                complementos_json=json.dumps(item_data.get('complementos', []))
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({'success': True, 'order_id': pedido.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pedido/<int:pedido_id>', methods=['GET'])
def get_order(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return jsonify(pedido.to_dict())


@app.route('/api/pedidos/buscar', methods=['POST'])
def find_orders():
    data = request.json
    order_ids = data.get('pedidos', [])
    
    if not order_ids:
        return jsonify([])
    
    pedidos = Pedido.query.filter(Pedido.id.in_(order_ids)).order_by(Pedido.id.desc()).all()
    return jsonify([p.to_dict() for p in pedidos])


# ==================== AVALIAÇÕES (REQUER LOGIN) ====================

@app.route('/api/pedido/<int:pedido_id>/avaliacao', methods=['GET', 'POST'])
@login_required
def avaliar_pedido(pedido_id):
    """Avaliação do restaurante e itens - REQUER LOGIN"""
    pedido = Pedido.query.get_or_404(pedido_id)
    user = get_current_user()
    
    if request.method == 'GET':
        return jsonify({
            'restaurante': pedido.avaliacao_restaurante.to_dict() if pedido.avaliacao_restaurante else None,
            'itens': [item.to_dict() for item in pedido.itens]
        })
    
    elif request.method == 'POST':
        data = request.json
        
        try:
            # Avaliação do restaurante
            if 'restaurante' in data:
                if pedido.avaliacao_restaurante:
                    return jsonify({'success': False, 'error': 'Pedido já avaliado'}), 400
                
                avaliacao = AvaliacaoRestaurante(
                    pedido_id=pedido_id,
                    usuario_id=user.id,
                    nota=data['restaurante']['nota'],
                    comentario=data['restaurante'].get('comentario', '')
                )
                db.session.add(avaliacao)
            
            # Avaliação dos itens
            if 'itens' in data:
                for item_aval in data['itens']:
                    pedido_item = PedidoItem.query.filter_by(
                        pedido_id=pedido_id, 
                        item_id=item_aval['item_id']
                    ).first()
                    
                    if pedido_item and not pedido_item.avaliacao:
                        avaliacao_item = AvaliacaoItem(
                            pedido_item_id=pedido_item.id,
                            item_id=item_aval['item_id'],
                            usuario_id=user.id,
                            nota=item_aval['nota'],
                            comentario=item_aval.get('comentario', '')
                        )
                        db.session.add(avaliacao_item)
            
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ADMIN ENDPOINTS ====================

@app.route('/api/pedidos', methods=['GET'])
def list_orders():
    pedidos = Pedido.query.order_by(Pedido.id.desc()).all()
    return jsonify([p.to_dict() for p in pedidos])


@app.route('/api/pedido/<int:pedido_id>/status', methods=['PUT'])
def update_order_status(pedido_id):
    data = request.json
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.status = data.get('status', pedido.status)
    db.session.commit()
    return jsonify({'success': True, 'pedido': pedido.to_dict()})


# ==================== INICIALIZAÇÃO ====================

with app.app_context():
    db.create_all()
    seed_database()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
