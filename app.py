from flask import Flask,escape,render_template,session, url_for, request, redirect, flash
from sqlalchemy.orm import sessionmaker
import datetime
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
import hashlib
from sqlalchemy.orm.session import make_transient
app = Flask(__name__)
app.config.from_pyfile("config.py")

from models import Usuarios,Pedidos, ItemsPedidos, Productos, basedatos
        
listapedidos = []
listaprecios = []

@app.route("/")
def index ():
    if "DNI" in session and "Tipo" in session:
        return render_template('principal.html', Tipo = escape(session['Tipo']))
    return redirect(url_for('login'))

@app.route("/login")
def login ():
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def LOGIN ():
    if request.method == "POST":
        if request.form["dni"] and request.form["password"]:
            usuario = Usuarios.query.filter_by(DNI=request.form['dni']).first()
            if type(usuario) is not None:
                pasaword = request.form["password"]
                result = hashlib.md5(bytes(pasaword, encoding='utf-8'))
                if usuario.Clave == result.hexdigest():
                    session['DNI'] = usuario.DNI
                    session['Tipo'] = usuario.Tipo
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('login'))
            else:
                return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))

@app.route("/registrarPedido")
def registarPedido ():
    if "DNI" in session:
        if session["Tipo"] == "Mozo":
            productos = Productos.query.all()
            return render_template('registar_pedido_mozo.html', productos=productos)
        else:
            if session["Tipo"] == "Cocinero":
                pedidos = ItemsPedidos.query.all()
                return render_template('listar_pedidos_cocinero.html', pedidos=pedidos)
    else:
        listapedidos.clear()
        listaprecios.clear()
        return redirect(url_for('login'))

@app.route("/nuevopedido", methods=["POST"])
def Nuevopedido():
    if request.method == "POST":
        if "DNI" in session and "Tipo" in session:
            if session["Tipo"] == 'Mozo':
                total = 0
                for i in range(len(listaprecios)):
                    total += listaprecios[i]
                p = basedatos.session.query(Pedidos).count()  #Numero de pedidos
                p += 1  #Auto incremento de Numero de pedidos
                pedido_nuevo = Pedidos(NumPedido = "{}".format(int(p)),Fecha = datetime.date.today(), Total = total, Cobrado = 'False', Observacion=request.form['observacion'], Mesa = request.form['Mesa'],  DniMozo = escape(session["DNI"]))
                basedatos.session.add(pedido_nuevo)
                basedatos.session.commit()
                
                for item in listapedidos:
                    q = basedatos.session.query(ItemsPedidos).count() #Numero de Items
                    q +=1       #Auto incremento de Numero de item
                    producto = Productos.query.filter_by(Nombre = item).first()
                    nuevo_item = ItemsPedidos(NumItem = "{}".format(int(q)), NumPedido=pedido_nuevo.NumPedido,NumProducto="{}".format(int(producto.NumProducto)), Precio=producto.PrecioUnitario, Estado="Pendiente")
                    basedatos.session.add(nuevo_item)
                basedatos.session.commit()
                del listapedidos[:]
                del listaprecios[:]
                return redirect(url_for('registarPedido'))
        else:
            return redirect(url_for('login'))

@app.route("/listado_pedidos")
def Listado ():
    if "DNI" in session and "Tipo" in session:
        if escape(session['Tipo']) == "Cocinero":
            q = basedatos.session.query(Pedidos).join(ItemsPedidos).filter(ItemsPedidos.Estado == "Pendiente").all()
            for i in q:
                print(i.item_pedido)
            return render_template("listar_pedidos_cocinero.html", pedidos = q)
        
        else:
            return redirect(url_for("Logout"))    
    else:
        return redirect(url_for('login'))

@app.route('/listar <nombre> <precio>')
def Listar(nombre,precio):
    i=0
    try:
        Total=0
        productos = Productos.query.all()
        if(nombre not in listapedidos):
            listapedidos.append(nombre)
            listaprecios.append(float(precio))
       
        if(listaprecios != None):
            for i in range(len(listaprecios)):
                Total+=listaprecios[i]

        if(len(listapedidos)!=0):
            return render_template('registar_pedido_mozo.html',productos=productos,listaNom=listapedidos,total=Total)
    except(TypeError):
        print("")

@app.route("/ListarPedido")
def ListarCocinero ():
    if "DNI" in session and "Tipo" in session:
        if escape(session["Tipo"]) == "Cocinero":
            union = basedatos.session.query(Pedidos).join(ItemsPedidos).\
                filter(ItemsPedidos.Estado == "Pendiente").all()
            return render_template("listar_cocinero.html", pedidos = union)
        elif escape(session['Tipo']) == "Mozo":
            fecha_de_hoy = datetime.date.today()
            pedidos = Pedidos.query.filter_by(Fecha = fecha_de_hoy,Cobrado="False").all()
            return render_template('Listar_mozo.html', pedidos = pedidos)
    else:
        return redirect(url_for("/Logout"))

@app.route("/ListarPedido <int:numpedido>")
def Cocinero (numpedido):
    if "DNI" in session and "Tipo" in session:
        if escape(session["Tipo"]) == "Cocinero":
            marcar_Listo = ItemsPedidos.query.filter_by(NumItem = "{}".format(int(numpedido))).first()
            #print(marcar_Listo)
            marcar_Listo.Estado = "Listo"
            basedatos.session.commit()
            return redirect(url_for("ListarCocinero"))
        else:
            redirect(url_for("Logout"))
    else:
        return redirect(url_for("login"))

@app.route("/CobrarPedido <int:pedido>")
def Cobrar (pedido):
    if "DNI" in session and "Tipo" in session:
        if escape(session['Tipo']) == "Mozo":
            cobrar = Pedidos.query.filter_by(NumPedido="{}".format(int(pedido))).first()
            if cobrar is not None:
                return render_template("cobrar_pedido_mozo.html",pedido = cobrar)
            else:
                return redirect(url_for("ListarCocinero"))
        else:
            return redirect(url_for("Logout"))
    else:
        redirect(url_for("Login"))

@app.route("/CobrarPedido <pedido>",methods=["POST"])
def PagarPedido (pedido):
    if "DNI" in session and "Tipo" in session:
        if escape(session["Tipo"]) == "Mozo":
            if request.method == "POST":
                cobrar = Pedidos.query.filter_by(NumPedido = "{}".format(int(pedido))).first()
                cobrar.Cobrado = "True"
                basedatos.session.commit()
                return redirect(url_for("ListarCocinero"))
        else:
            return redirect(url_for("Logout"))
    else:
        return redirect(url_for("Login"))

@app.route('/Logout')
def Logout():
    session.pop('DNI')
    session.pop('Tipo')
    listapedidos.clear()
    listaprecios.clear()
    return redirect(url_for('login'))

@app.route('/newUser', methods=['GET', 'POST'])
def newUser():
    if request.method == "POST":
        if "DNI" in session and "Tipo" in session:
            if session["Tipo"] == 'Administrador':
                pword=request.form['Password']
                result = hashlib.md5(bytes(pword, encoding='utf-8'))
                newuser = Usuarios(DNI=request.form['Usuario'],Clave=result.hexdigest(),Tipo=request.form['Tipo'])
                basedatos.session.add(newuser)
                basedatos.session.commit()
                return redirect(url_for('index'))
    return render_template("newUser.html")

@app.route('/newProduct', methods=['GET', 'POST'])
def newProduct():
    if request.method == "POST":
        if "DNI" in session and "Tipo" in session:
            if session["Tipo"] == 'Administrador':
                q = basedatos.session.query(Productos).count() #Numero de Items
                q += 1
                new = Productos(NumProducto= q, Nombre = str(request.form['Name']), PrecioUnitario=str(request.form['Precio']))
                basedatos.session.add(new)
                basedatos.session.commit()
                return redirect(url_for('index'))

    return render_template("newProduct.html")

@app.route('/delete', methods=['GET', 'POST'])
def deleteUoP():
    if request.method == "POST":
        if "DNI" in session and "Tipo" in session:
            if session["Tipo"] == 'Administrador':
                try:
                    if(Usuarios.query.filter_by(DNI=request.form.get('Name')).first()):
                        return render_template('delete.html',usuario=Usuarios.query.filter_by(DNI=request.form.get('Name')).first())
                    else:
                        return render_template('delete.html',product=Productos.query.filter_by(Nombre=request.form.get('Name')).first())
                except KeyError:
                    print("Error de key")
    return render_template('delete.html')   

@app.route('/delete/eraseProduct/<nom>',methods=['POST','GET'])
def eraseP(nom):                #Elimina Productos
    print(nom)
    objeto=Productos.query.filter_by(Nombre=nom).first()
    basedatos.session.delete(objeto)
    basedatos.session.commit()
    return redirect(url_for('deleteUoP'))

@app.route('/delete/eraseUser/<nom>',methods=['POST','GET'])
def eraseU(nom):                #Elimina Usuarios
    print(nom)
    objeto=Usuarios.query.filter_by(DNI=nom).first()
    basedatos.session.delete(objeto)
    basedatos.session.commit()
    return redirect(url_for('deleteUoP'))

@app.route('/Ver/Histoial/', methods=['GET','POST'])
def ViewHistory():
    total=0
    try:
        fecha=request.form['dateSelecter']
        pedidos=Pedidos.query.filter_by(Fecha=fecha).all()
        for i in pedidos:
            total += int(i.Total)
        return render_template('ViewHistory.html',pedidos=pedidos,Total=total)
    except KeyError:
        return render_template('ViewHistory.html',Total=total)





def clearDDBB():                    # ******** PENDIENTE A REVISION POR LAS FECHAS ********
    a=datetime.date.today().year
    m=datetime.date.today().month-1
    d=datetime.date.today().day
    date=('{}-0{}-{}' .format(a,m,d))
    ped=Pedidos.query.filter_by(Fecha=date).all()
    for i in ped:
        basedatos.session.delete(i)
    basedatos.session.commit()

if __name__ == "__main__": 
    clearDDBB()
    app.run(debug=True)
