from app import app, db, bcrypt
from flask import render_template, redirect, url_for, flash, request, abort,send_from_directory
from models import Usuario, Documento, Firma
from forms import RegistrationForm, LoginForm, UploadDocumentForm
from flask_login import login_user, current_user, logout_user, login_required
import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
import datetime
import io
import qrcode
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@app.route('/')
@app.route('/inicio')
def index():
    return render_template('inicio.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        nuevo_usuario = Usuario(nombre=form.nombre.data, email=form.email.data, password=hashed_password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('¡Tu cuenta ha sido creada! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.password, form.password.data):
            login_user(usuario, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos.', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    documentos_enviados = Documento.query.filter_by(id_propietario=current_user.id).all()
    firmas_pendientes = Firma.query.filter_by(id_firmante=current_user.id, estado='pendiente').all()

    return render_template('dashboard.html',
                           nombre_usuario=current_user.nombre,
                           documentos_enviados=documentos_enviados,
                           firmas_pendientes=firmas_pendientes)


#RUTA DE SUBIDA DE DOCUMENTOS
@app.route('/subir_documento', methods=['GET', 'POST'])
@login_required
def subir_documento():
    form = UploadDocumentForm()
    usuarios_disponibles = Usuario.query.filter(Usuario.id != current_user.id).all()
    form.firmantes.choices = [(u.id, u.nombre) for u in usuarios_disponibles]

    if form.validate_on_submit():
        archivo = form.documento.data
        nombre_original_seguro = secure_filename(archivo.filename)

        # Nombre único para guardar
        nombre_unico_sistema = f"{uuid.uuid4()}_{nombre_original_seguro}"
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], nombre_unico_sistema)

        archivo.save(ruta_archivo)

        # Calcular Hash
        sha256 = hashlib.sha256()
        with open(ruta_archivo, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data: break
                sha256.update(data)
        hash_doc = sha256.hexdigest()

        nuevo_doc = Documento(
            nombre_original=nombre_original_seguro,
            nombre_sistema=nombre_unico_sistema,
            hash_original=hash_doc,
            id_propietario=current_user.id
        )
        db.session.add(nuevo_doc)
        db.session.commit()

        # Guardar Firmas
        for firmante_id in form.firmantes.data:
            nueva_firma = Firma(
                id_documento=nuevo_doc.id,
                id_firmante=firmante_id,
                estado='pendiente'
            )
            db.session.add(nueva_firma)
        db.session.commit()

        flash('Documento subido y enviado correctamente.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('subir_documento.html', form=form)


#RUTA DE FIRMA DE DOCUMENTOS

@app.route('/firmar/<int:id_firma>', methods=['GET', 'POST'])
@login_required
def firmar(id_firma):
    # query a bd
    firma = Firma.query.get_or_404(id_firma)

    # usuario logueado
    if firma.id_firmante != current_user.id:
        abort(403)
    if firma.estado != 'pendiente':
        flash('Este documento ya ha sido firmado.', 'info')
        return redirect(url_for('dashboard'))

    documento = firma.documento


    if request.method == 'POST':
        try:

            ruta_original = os.path.join(app.config['UPLOAD_FOLDER'], documento.nombre_sistema)
            ruta_final = ruta_original

            # CREAMOS HOJA DE FIRMA
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Título
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2.0, height - 72, "HOJA DE EVIDENCIA DE FIRMA DIGITAL")

            # Datos del Firmante
            c.setFont("Helvetica", 11)
            c.drawString(72, height - 120, f"Firmado por: {current_user.nombre}")
            c.drawString(72, height - 140, f"Correo electrónico: {current_user.email}")

            now = datetime.datetime.utcnow()
            c.drawString(72, height - 160, f"Fecha de firma (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(72, height - 200, "Firma  (Hash SHA-256):")
            c.setFont("Courier", 10)
            c.drawString(72, height - 220, documento.hash_original)

            # GENERAR EL CODIGO QR
            qr_data = f"Firma Digital Validado\nDoc: {documento.nombre_original}\nHash: {documento.hash_original}\nFirmante: {current_user.nombre}"
            qr_img = qrcode.make(qr_data)

            qr_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_qr_{firma.id}.png")
            qr_img.save(qr_temp_path)

            #PASAR EL QR AL PDF
            c.drawImage(qr_temp_path, x=72, y=height - 400, width=150, height=150)
            #MOSTRAR EN LA PAGINA
            c.showPage()
            c.save()

            buffer.seek(0)
            pagina_firma_pdf = PdfReader(buffer)
            pdf_original = PdfReader(open(ruta_original, 'rb'))

            merger = PdfWriter()
            merger.append_pages_from_reader(pdf_original)
            merger.append_pages_from_reader(pagina_firma_pdf)

            with open(ruta_final, 'wb') as f_out:
                merger.write(f_out)

            # DB limpiar y actaualiza
            firma.estado = 'firmado'
            firma.fecha_firma = now
            db.session.commit()

            buffer.close()
            if os.path.exists(qr_temp_path):
                os.remove(qr_temp_path)

            flash(f'¡Documento "{documento.nombre_original}" firmado correctamente!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f'Error al firmar: {e}', 'error')
            return redirect(url_for('dashboard'))

    return render_template('firmar_documento.html', doc_nombre=documento.nombre_original)


# DESCARAGR EL DOC
@app.route('/descargar/<int:id_documento>')
@login_required
def descargar(id_documento):
    documento = Documento.query.get_or_404(id_documento)

    #seg logeada
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        documento.nombre_sistema,
        as_attachment=True,
        download_name=documento.nombre_original
    )