from __main__ import app
from flask_sqlalchemy import SQLAlchemy


basedatos=SQLAlchemy(app)

class Usuarios(basedatos.Model):
    __tablename__="usuarios"
    DNI=basedatos.Column(basedatos.String(16),primary_key=True, nullable=False)
    Clave=basedatos.Column(basedatos.String(16),nullable=False)
    Tipo=basedatos.Column(basedatos.String(16),nullable=False)
    pedido_cargado = basedatos.relationship('Pedidos',backref='usuarios',cascade="all, delete-orphan",lazy='dynamic')

class Pedidos(basedatos.Model):
    __tablename__ = 'pedidos'
    NumPedido= basedatos.Column(basedatos.Integer,primary_key=True)
    Fecha= basedatos.Column(basedatos.Date,nullable=False)
    Total= basedatos.Column(basedatos.Float,nullable=False)
    Cobrado= basedatos.Column(basedatos.String(22),nullable=False)
    Observacion=basedatos.Column(basedatos.Text)
    DniMozo=basedatos.Column(basedatos.Integer,basedatos.ForeignKey('usuarios.DNI'))
    Mesa=basedatos.Column(basedatos.Integer,nullable=False)
    item_pedido=basedatos.relationship('ItemsPedidos',backref='pedidos', cascade="all, delete-orphan", lazy='dynamic')

class ItemsPedidos(basedatos.Model):
    __tablename__ = "ItemsPedidos"
    NumItem= basedatos.Column(basedatos.Integer,primary_key=True)
    NumPedido=basedatos.Column(basedatos.Integer,basedatos.ForeignKey('pedidos.NumPedido'))
    NumProducto=basedatos.Column(basedatos.Integer,basedatos.ForeignKey('productos.NumProducto'))
    Precio=basedatos.Column(basedatos.Float,nullable=False)
    Estado=basedatos.Column(basedatos.String(50),nullable=False)
    item_producto=basedatos.relationship('Productos',backref='itempedidos')

class Productos (basedatos.Model):
    __tablename__="productos"
    NumProducto= basedatos.Column(basedatos.Integer,primary_key=True)
    Nombre= basedatos.Column(basedatos.String(120),nullable=False)
    PrecioUnitario= basedatos.Column(basedatos.Float,nullable=False)
