from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Usuario(db.Model):
    """Usuário autenticado com Google OAuth"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    avaliacoes_restaurante = db.relationship('AvaliacaoRestaurante', backref='usuario', lazy=True)
    avaliacoes_itens = db.relationship('AvaliacaoItem', backref='usuario', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'foto': self.foto
        }


class Configuracao(db.Model):
    """Configurações gerais do sistema"""
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(255))
    
    @staticmethod
    def get_tema_atual():
        """Retorna o tema atual configurado"""
        config = Configuracao.query.filter_by(chave='tema_atual').first()
        return config.valor if config else 'churrasco'
    
    @staticmethod
    def set_tema_atual(tema_id):
        """Define o tema atual"""
        config = Configuracao.query.filter_by(chave='tema_atual').first()
        if not config:
            config = Configuracao(chave='tema_atual', valor=tema_id)
            db.session.add(config)
        else:
            config.valor = tema_id
        db.session.commit()
    
    @staticmethod
    def get_hora_simulada():
        """Retorna hora simulada para testes (formato HH:MM)"""
        config = Configuracao.query.filter_by(chave='hora_simulada').first()
        return config.valor if config else None
    
    @staticmethod
    def set_hora_simulada(hora):
        """Define hora simulada"""
        config = Configuracao.query.filter_by(chave='hora_simulada').first()
        if not config:
            config = Configuracao(chave='hora_simulada', valor=hora)
            db.session.add(config)
        else:
            config.valor = hora
        db.session.commit()


class Restaurante(db.Model):
    __tablename__ = 'restaurante'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    horario = db.Column(db.String(100))
    logo = db.Column(db.String(100))
    tema = db.Column(db.String(20), default='churrasco')
    
    def to_dict(self):
        # Calcular média das avaliações do restaurante
        media = db.session.query(db.func.avg(AvaliacaoRestaurante.nota)).scalar() or 0
        total = AvaliacaoRestaurante.query.count()
        
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'horario': self.horario,
            'logo': self.logo,
            'tema': self.tema,
            'avaliacao': {
                'media': round(media, 1),
                'total': total
            }
        }


class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.String(50), primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ordem = db.Column(db.Integer, default=0)
    icone = db.Column(db.String(10), default='🍽️')
    horario = db.Column(db.String(20), default='todos')
    
    itens = db.relationship('Item', backref='categoria', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'icone': self.icone,
            'horario': self.horario,
            'itens': [item.to_dict() for item in self.itens]
        }


class Item(db.Model):
    __tablename__ = 'itens'
    
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.String(50), db.ForeignKey('categorias.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(10), default='🍽️')
    ativo = db.Column(db.Boolean, default=True)
    
    complementos = db.relationship('Complemento', backref='item', lazy=True, cascade='all, delete-orphan')
    avaliacoes = db.relationship('AvaliacaoItem', backref='item', lazy=True)
    
    def to_dict(self):
        # Calcular média das avaliações do item
        media = db.session.query(db.func.avg(AvaliacaoItem.nota)).filter_by(item_id=self.id).scalar() or 0
        total = AvaliacaoItem.query.filter_by(item_id=self.id).count()
        
        data = {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'imagem': self.imagem,
            'avaliacao': {
                'media': round(media, 1),
                'total': total
            }
        }
        if self.complementos:
            data['complementos'] = [c.to_dict() for c in self.complementos]
        return data


class Complemento(db.Model):
    __tablename__ = 'complementos'
    
    id = db.Column(db.String(20), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('itens.id'), nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Float, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'preco': self.preco
        }


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.now)
    
    # Dados do cliente
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    complemento = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    
    # Usuário (opcional - pode fazer pedido sem login)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Pagamento
    metodo_pagamento = db.Column(db.String(20), nullable=False)
    troco = db.Column(db.Float)
    
    # Valores
    subtotal = db.Column(db.Float, nullable=False)
    taxa_entrega = db.Column(db.Float, default=5.0)
    total = db.Column(db.Float, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='novo')
    
    # Relacionamentos
    itens = db.relationship('PedidoItem', backref='pedido', lazy=True, cascade='all, delete-orphan')
    avaliacao_restaurante = db.relationship('AvaliacaoRestaurante', backref='pedido', lazy=True, uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.strftime('%d/%m/%Y %H:%M:%S'),
            'cliente': {
                'nome': self.nome,
                'telefone': self.telefone,
                'endereco': self.endereco,
                'complemento': self.complemento,
                'observacoes': self.observacoes
            },
            'pagamento': {
                'metodo': self.metodo_pagamento,
                'troco': self.troco
            },
            'valores': {
                'subtotal': self.subtotal,
                'entrega': self.taxa_entrega,
                'total': self.total
            },
            'status': self.status,
            'itens': [item.to_dict() for item in self.itens],
            'avaliacao_restaurante': self.avaliacao_restaurante.to_dict() if self.avaliacao_restaurante else None
        }


class PedidoItem(db.Model):
    __tablename__ = 'pedido_itens'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    
    item_id = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    complementos_json = db.Column(db.Text)
    
    avaliacao = db.relationship('AvaliacaoItem', backref='pedido_item', lazy=True, uselist=False)
    
    def to_dict(self):
        import json
        complementos = json.loads(self.complementos_json) if self.complementos_json else []
        return {
            'id': self.id,
            'itemId': self.item_id,
            'nome': self.nome,
            'preco': self.preco_unitario,
            'quantidade': self.quantidade,
            'complementos': complementos,
            'avaliacao': self.avaliacao.to_dict() if self.avaliacao else None
        }


class AvaliacaoRestaurante(db.Model):
    """Avaliação do restaurante em geral"""
    __tablename__ = 'avaliacoes_restaurante'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nota': self.nota,
            'comentario': self.comentario,
            'data': self.data.strftime('%d/%m/%Y %H:%M'),
            'usuario': self.usuario.nome if self.usuario else None
        }


class AvaliacaoItem(db.Model):
    """Avaliação de item específico do pedido"""
    __tablename__ = 'avaliacoes_itens'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_item_id = db.Column(db.Integer, db.ForeignKey('pedido_itens.id'), nullable=False, unique=True)
    item_id = db.Column(db.Integer, db.ForeignKey('itens.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'nota': self.nota,
            'comentario': self.comentario,
            'data': self.data.strftime('%d/%m/%Y %H:%M'),
            'usuario': self.usuario.nome if self.usuario else None
        }
