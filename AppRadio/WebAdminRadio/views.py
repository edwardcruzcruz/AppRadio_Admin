import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from accounts.models import Usuario
from .models import *
from .forms import *

# Sección pantallas principales

@login_required
def home(request):
    return render(request, 'webAdminRadio/index.html', {'title': 'Principal'})

@login_required
def emisoras(request):
    list_emisoras = Emisora.objects.filter(activo='A')
    context = {'title': 'Emisoras', 'emisoras': list_emisoras}
    return render(request, 'webAdminRadio/emisoras.html', context)

@login_required
def segmentos(request):
    list_emisoras = Emisora.objects.all()
    context = {'title': 'Segmentos', 'emisoras': list_emisoras}
    return render(request, 'webAdminRadio/segmentos.html', context)

@login_required
def locutores(request):
    list_segmentos = Segmento.objects.filter(activo='A')
    emisoras = Emisora.objects.filter(activo='A')
    context = {
        'title': 'Locutores',
        'segmentos': list_segmentos,
        'emisoras': emisoras
    }
    return render(request, 'webAdminRadio/locutores.html', context)

@login_required
def concursos(request):
    list_segmentos = Segmento.objects.filter(activo='A')
    emisoras = Emisora.objects.filter(activo='A') 
    context = {
        'title': 'Concursos',
        'segmentos': list_segmentos,
        'emisoras': emisoras
    }
    return render(request, 'webAdminRadio/concursos.html', context)

@login_required
def encuestas(request):
    emisoras = Emisora.objects.filter(activo='A')
    context = {
        'title': "Encuestas",
        'emisoras': emisoras
    }
    return render(request, 'webAdminRadio/encuestas.html', context)

@login_required
def usuarios(request):
    context = {'title': 'Usuarios'}
    return render(request, 'webAdminRadio/usuarios.html', context)

@login_required
def sugerencias(request):
    list_sugerencias = Sugerencia.objects.all().order_by("-fecha_creacion")
    query = request.GET.get("q")
    if query:
        try:
            list_sugerencias = list_sugerencias.filter(Q(fecha_creacion__year=query))
        except ValueError:
            list_sugerencias = list_sugerencias.filter(
                Q(mensaje__icontains=query) |
                Q(idUsuario__first_name__icontains=query) |
                Q(idUsuario__last_name__icontains=query) |
                Q(idSegmento__nombre__icontains=query) |
                Q(idEmisora__nombre__icontains=query)
            ).distinct()
    paginator = Paginator(list_sugerencias, 2)
    page = request.GET.get('page')
    list_sugerencias = paginator.get_page(page)
    context = {'title': 'Sugerencias', 'sugerencias': list_sugerencias}
    return render(request, 'webAdminRadio/sugerencias.html', context)

@login_required
def publicidad(request):
    list_emisoras = Emisora.objects.filter(activo='A')
    list_segmentos = Segmento.objects.filter(activo='A')
    context = {
        'title': 'Publicidad',
        'segmentos': list_segmentos,
        'emisoras': list_emisoras,
    }
    return render(request, 'webAdminRadio/publicidad.html', context)

# Sección agregar

@login_required
def encuestas(request):
    emisoras = Emisora.objects.filter(activo='A')
    context = {
        'title': "Encuestas",
        'emisoras': emisoras
    }
    return render(request, 'webAdminRadio/encuestas.html', context)

@login_required
def agregar_emisora(request):
    context = {'title': 'Agregar Emisora'}
    if request.POST:
        emisora_form = EmisoraForm(request.POST, request.FILES)
        if not emisora_form.is_valid():
            context['error'] = emisora_form.errors
            return render(request, 'webAdminRadio/agregar_emisora.html', context)

        for i in range(len(request.POST.getlist('telefono'))):
            telefono_form = TelefonoForm({
                'telefono':request.POST.getlist('telefono')[i]
            })
            if not telefono_form.is_valid():
                context['error'] = telefono_form.errors
                return render(request, 'webAdminRadio/agregar_emisora.html', context)

        for i in range(len(request.POST.getlist('red_social_nombre'))):
            red_form = RedSocialForm({
                'nombre': request.POST.getlist('red_social_nombre')[i],
                'link': request.POST.getlist('red_social_url')[i]
            })
            if not red_form.is_valid():
                context['error'] = red_form.errors
                return render(request, 'webAdminRadio/agregar_emisora.html', context)

        emisora_form.save()
        for i in range(len(request.POST.getlist('telefono'))):
            Telefono_emisora.objects.create(
                idEmisora=Emisora.objects.order_by('-id')[0],
                nro_telefono=request.POST.getlist('telefono')[i]
            )
        for i in range(len(request.POST.getlist('red_social_nombre'))):
            RedSocial_emisora.objects.create(
                idEmisora=Emisora.objects.order_by('-id')[0],
                nombre=request.POST.getlist('red_social_nombre')[i],
                link=request.POST.getlist('red_social_url')[i]
            )
        context['success'] = '¡La emisora ha sido registrada con éxito!'
        return render(request, 'webAdminRadio/agregar_emisora.html', context)
    return render(request, 'webAdminRadio/agregar_emisora.html', context)

@login_required
def agregar_segmento(request):
    list_emisoras = Emisora.objects.all()
    context = {'title': 'Agregar Segmento', 'emisoras': list_emisoras}
    if request.POST:
        segmento_form = SegmentoForm(request.POST, request.FILES)
        if segmento_form.is_valid():
            segmento_form.save()
            # Iterar por todos los horarios
            for i in range(len(request.POST.getlist('dia'))):
                # Creación del horario
                horario_form = HorarioForm({
                    'dia': request.POST.getlist('dia')[i],
                    'inicio': request.POST.getlist('inicio')[i],
                    'fin': request.POST.getlist('fin')[i]
                })
                if horario_form.is_valid():
                    horario_form.save()
                    # Enlazar segmento con horario
                    segmento_horario.objects.create(
                        idSegmento=Segmento.objects.order_by('-id')[0],
                        idHorario=Horario.objects.order_by('-id')[0]
                    )
                else:
                    context['error'] = horario_form.errors
                    break
            if 'error' not in context:
                context['success'] = '¡El registro del segmento se ha sido creado con éxito!'
        else:
            context['error'] = segmento_form.errors
        return render(request, 'webAdminRadio/agregar_segmento.html', context)
    return render(request, 'webAdminRadio/agregar_segmento.html', context)

@login_required
def agregar_concurso(request):
    list_usuarios = Usuario.objects.all()
    list_emisoras = Emisora.objects.filter(activo='A')
    list_segmentos = Segmento.objects.filter(activo='A')
    context = {
        'title': 'Agregar Concurso',
        'usuarios': list_usuarios,
        'emisoras': list_emisoras,
        'segmentos': list_segmentos
    }
    if request.POST:
        print(request.POST)
        encuesta_form = EncuestaFrom(request.POST)
        if encuesta_form.is_valid():
            encuesta = encuesta_form.save()
            for i in range(len(request.POST.getlist('preguntas'))):
                pregunta_form = PreguntaForm({
                    'contenido': request.POST.getlist('preguntas')[i],
                    'tipo': request.POST.getlist('tipo')[i],
                    'respuesta_c': request.POST.getlist('respuesta_correcta')[i],
                    'idEncuesta': encuesta.id
                })
                if pregunta_form.is_valid():
                    new_pregunta = pregunta_form.save()
                    for j in range(len(request.POST.getlist('respuesta' + str(i+1)))):
                        alternativa_form = AlternativaForm({
                            'contenido': request.POST.getlist('respuesta' + str(i+1))[j],
                            'idPregunta': new_pregunta.id
                        })
                        if alternativa_form.is_valid():
                            alternativa_form.save()
                        else:
                            context['error'] = alternativa_form.errors
                            return render(request, 'webAdminRadio/agregar_concurso.html', context)
                else:
                    context['error'] = pregunta_form.errors
            concurso_form = ConcursoForm({
                'idEncuesta' : encuesta.id,
                'idUsuario' : request.POST['usuario'],
                'premios' : request.POST['premios']
            })
            if concurso_form.is_valid():
                concurso = concurso_form.save()
            else:
                context['error'] = concurso_form.errors
        if 'error' not in context:
            context['success'] = '¡Concurso creado con éxito!'
    return render(request, 'webAdminRadio/agregar_concurso.html', context)

@login_required
def agregar_encuesta(request):
    emisoras = Emisora.objects.filter(activo='A')
    context = {
        'title': "Agregar Encuesta",
        'emisoras': emisoras,
    }
    if request.POST:
        encuesta_form = EncuestaFrom(request.POST)
        if encuesta_form.is_valid():
            new_encuesta = encuesta_form.save()
            # Iterando por cada pregunta con sus respectivas alternativas
            for i in range(len(request.POST.getlist('preguntas'))):
                pregunta_form = PreguntaForm({
                    'contenido': request.POST.getlist('preguntas')[i],
                    'idEncuesta': new_encuesta.id
                })
                if pregunta_form.is_valid():
                    new_pregunta = pregunta_form.save()
                    for j in range(len(request.POST.getlist('respuesta' + str(i)))):
                        alternativa_form = AlternativaForm({
                            'contenido': request.POST.getlist('respuesta' + str(i))[j],
                            'idPregunta': new_pregunta.id
                        })
                        if alternativa_form.is_valid():
                            alternativa_form.save()
                        else:
                            context['error'] = alternativa_form.errors
                            return render(request, 'webAdminRadio/agregar_encuesta.html', context)
                else:
                    context['error'] = pregunta_form.errors
                    return render(request, 'webAdminRadio/agregar_encuesta.html', context)
        else:
            context['error'] = encuesta_form.errors
        if 'error' not in context:
            context['success'] = '¡Se ha guardado la encuesta con éxito!'
    return render(request, 'webAdminRadio/agregar_encuesta.html', context)

@login_required
def agregar_usuario(request):
    context = {'title': 'Agregar Usuario'}
    if request.POST:
        nombre = request.POST['nombre']
        apellidos = request.POST['apellido']
        username = nombre[0].lower() + apellidos.partition(' ')[0].lower()
        password = Usuario.objects.make_random_password()
        user_form = UsuarioForm({
            'nombre': nombre,
            'apellido': apellidos,
            'username': username,
            'password': password,
            'email': request.POST['email'],
            'fechaNac': request.POST['fechaNac'],
            'rol': request.POST['tipo_select'],
            'apodo': request.POST['apodo'],
            'biografia': request.POST['biografia'],
            'hobbies': request.POST['hobbies']
        }, request.FILES)

        telefono_form = TelefonoForm({
            'telefono': request.POST['telefono']
        })

        if not telefono_form.is_valid():
            context['error'] = telefono_form.errors
            return render(request, 'webAdminRadio/agregar_usuario.html', context)

        list_redes = len(request.POST.getlist('red_social_nombre'))

        if request.POST['red_social_url']:
            for i in range(list_redes):
                red_social_form = RedSocialForm({
                    'nombre': request.POST.getlist('red_social_nombre')[i],
                    'link': request.POST.getlist('red_social_url')[i]
                })
                if not red_social_form.is_valid():
                    context['error'] = red_social_form.errors
                    return render(request, 'webAdminRadio/agregar_usuario.html', context)

        if user_form.is_valid():
            user_form.save()
            Telefono_Usuario.objects.create(
                idUsuario=Usuario.objects.order_by('-id')[0],
                nro_telefono=request.POST['telefono']
            )
            if request.POST['red_social_url']:
                for i in range(list_redes):
                    RedSocial_usuario.objects.create(
                        idUsuario=Usuario.objects.order_by('-id')[0],
                        nombre=request.POST.getlist('red_social_nombre')[i],
                        link=request.POST.getlist('red_social_url')[i]
                    )
            context['success'] = '¡El usuario ha sido registrado!'
        else:
            context['error'] = user_form.errors
    return render(request, 'webAdminRadio/agregar_usuario.html', context)

@login_required
def agregar_publicidad(request):
    list_emisoras = Emisora.objects.filter(activo='A')
    context = {
        'title': 'Agregar Publicidad',
        'emisoras': list_emisoras
        }
    if request.POST:
        publicidad_form = PublicidadForm(request.POST, request.FILES)
        if publicidad_form.is_valid():
            publicidad_form.save()
            # Iterar por todos los horarios
            for i in range(len(request.POST.getlist('tipo'))):
                frecuencia_form = FrecuenciaForm({
                    'tipo': request.POST.getlist('tipo')[i],
                    'dia': request.POST.getlist('dia_semana')[i],
                    'inicio': request.POST.getlist('hora_inicio')[i],
                    'fin': request.POST.getlist('hora_fin')[i]
                })
                if frecuencia_form.is_valid():
                    frecuencia_form.save()
                    frecuencia_publicidad.objects.create(
                        idPublicidad=Publicidad.objects.order_by('-id')[0],
                        idFrecuencia=Frecuencia.objects.order_by('-id')[0]
                    )
                else:
                    context['error'] = frecuencia_form.errors
                    break
            for s in request.POST.getlist('segmento'):
                segmento_publicidad.objects.create(
                    idPublicidad=Publicidad.objects.order_by('-id')[0],
                    idSegmento=Segmento.objects.get(id=s)
                )
            if 'error' not in context:
                context['success'] = '¡El registro de la publicidad se ha sido creado con éxito!'
        else:
            context['error'] = publicidad_form.errors
    return render(request, 'webAdminRadio/agregar_publicidad.html', context)

# Sección modificar

@login_required
def modificar_emisora(request, id_emisora):
    edit_emisora = Emisora.objects.get(id=id_emisora, activo='A')
    red_social = RedSocial_emisora.objects.filter(idEmisora=id_emisora)
    telefono_emisora = Telefono_emisora.objects.filter(idEmisora=id_emisora)
    context = {
        'title': 'Editar Emisora',
        'emisora': edit_emisora,
        'telefono': json.dumps(list(telefono_emisora.values('nro_telefono')), cls=DjangoJSONEncoder),
        'redsocial': red_social
    }
    if request.POST:
        emisora_form = EmisoraForm(request.POST, request.FILES, instance=edit_emisora)
        if not emisora_form.is_valid():
            context['error'] = emisora_form.errors
            return render(request, 'webAdminRadio/modificar_emisora.html', context)

        for i in range(len(request.POST.getlist('telefono'))):
            telefono_form = TelefonoForm({
                'telefono': request.POST.getlist('telefono')[i]
            })
            if not telefono_form.is_valid():
                context['error'] = telefono_form.errors
                return render(request, 'webAdminRadio/modificar_emisora.html', context)

        for i in range(len(request.POST.getlist('red_social_nombre'))):
            red_form = RedSocialForm({
                'nombre': request.POST.getlist('red_social_nombre')[i],
                'link': request.POST.getlist('red_social_url')[i]
            })
            if not red_form.is_valid():
                context['error'] = red_form.errors
                return render(request, 'webAdminRadio/modificar_emisora.html', context)

        emisora_form.save()
        telefono_emisora.delete()
        red_social.delete()
        for i in range(len(request.POST.getlist('telefono'))):
            Telefono_emisora.objects.create(
                idEmisora=edit_emisora,
                nro_telefono=request.POST.getlist('telefono')[i]
            )
        for i in range(len(request.POST.getlist('red_social_nombre'))):
            RedSocial_emisora.objects.create(
                idEmisora=edit_emisora,
                nombre=request.POST.getlist('red_social_nombre')[i],
                link=request.POST.getlist('red_social_url')[i]
            )

        context['success'] = "¡La emisora ha sido registrada con éxito!"
        return render(request, 'webAdminRadio/modificar_emisora.html', context)
    return render(request, 'webAdminRadio/modificar_emisora.html', context)

@login_required
def modificar_segmento(request, id_segmento):
    edit_segmento = Segmento.objects.get(id=id_segmento, activo='A')
    horarios = Horario.objects.filter(pk__in=segmento_horario.objects.filter(idSegmento=edit_segmento))
    list_emisoras = Emisora.objects.all()
    context = {
        'title': 'Editar Segmento',
        'segmento': edit_segmento,
        'emisoras': list_emisoras,
        'horarios': json.dumps(list(horarios.values('dia', 'fecha_inicio', 'fecha_fin')), cls=DjangoJSONEncoder)
    }
    if request.POST:
        segmento_form = SegmentoForm(request.POST, request.FILES, instance=edit_segmento)
        if segmento_form.is_valid():
            segmento_form.save()
            horarios.delete()
            for i in range(len(request.POST.getlist('dia'))):
                horario_form = HorarioForm({
                    'dia': request.POST.getlist('dia')[i],
                    'inicio': request.POST.getlist('inicio')[i],
                    'fin': request.POST.getlist('fin')[i]
                })
                if horario_form.is_valid():
                    horario_form.save()
                    segmento_horario.objects.create(
                        idSegmento=edit_segmento,
                        idHorario=Horario.objects.order_by('-id')[0]
                    )
                else:
                    context['error'] = horario_form.errors
                    break
                context['success'] = '¡El registro ha sido modificado con éxito!'
        else:
            context['error'] = segmento_form.errors
        return render(request, 'webAdminRadio/editar_segmento.html', context)
    return render(request, 'webAdminRadio/editar_segmento.html', context)

@login_required
def modificar_locutor(request, id_locutor):
    list_emisoras = Emisora.objects.all()
    edit_locutor = Usuario.objects.get(id=id_locutor)
    list_segmentos = Segmento.objects.filter(pk__in=segmento_usuario.objects.filter(idUsuario=edit_locutor), activo='A')
    edit_telef = Telefono_Usuario.objects.get(idUsuario=id_locutor)
    segmentos_loc = segmento_usuario.objects.filter(idUsuario=id_locutor)
    context = {
        'title': 'Editar Locutor',
        'locutor': edit_locutor,
        'telefono': edit_telef,
        'emisoras': list_emisoras,
        'segmentos': json.dumps(list(list_segmentos.values('id', 'nombre')), cls=DjangoJSONEncoder)
    }
    if request.POST:
        usuario_form = UsuarioForm(request.POST, request.FILES, instance=edit_locutor)
        telf = request.POST['telefono']
        telefono_form = TelefonoForm({'telefono': telf}, instance=edit_telef)
        if (usuario_form.is_valid() and telefono_form.is_valid()):
            usuario_form.save()
            telefono_form.save()
            segmentos_loc.delete()
            for s in request.POST.getlist('segmento'):
                segmento_usuario.objects.create(
                    idUsuario=edit_locutor,
                    idSegmento=Segmento.objects.get(id=s)
                )
        else:
            if telefono_form.has_error:
                context['error'] = telefono_form.errors
            if usuario_form.has_error:
                context['error'] = usuario_form.errors
            return render(request, 'webAdminRadio/editar_locutor.html', context)
        context['success'] = '¡El registro del locutor se ha sido creado con éxito!'
    return render(request, 'webAdminRadio/editar_locutor.html', context)

@login_required
def modificar_usuario(request, id_usuario):
    edit_usuario = Usuario.objects.get(id=id_usuario)
    edit_telefono = Telefono_Usuario.objects.get(idUsuario=id_usuario)
    redes = RedSocial_usuario.objects.filter(idUsuario=id_usuario)
    context = {
        'title': 'Editar Usuario',
        'usuario': edit_usuario,
        'telefono': edit_telefono,
        'redes': json.dumps(list(redes.values('nombre', 'link')), cls=DjangoJSONEncoder)
    }
    if request.POST:
        nombre = request.POST['nombre']
        apellidos = request.POST['apellido']
        username = nombre[0].lower() + apellidos.partition(' ')[0].lower()
        password = Usuario.objects.make_random_password()
        user_form = UsuarioForm({
            'nombre': nombre,
            'apellido': apellidos,
            'username': username,
            'password': password,
            'email': request.POST['email'],
            'fechaNac': request.POST['fechaNac'],
            'rol': request.POST['tipo_select'],
            'apodo': request.POST['apodo'],
            'biografia': request.POST['biografia'],
            'hobbies': request.POST['hobbies']
        }, request.FILES, instance=edit_usuario)

        telefono_form = TelefonoForm({
            'telefono': request.POST['telefono']
        })

        if not telefono_form.is_valid():
            context['error'] = telefono_form.errors
            return render(request, 'webAdminRadio/editar_usuario.html', context)

        list_redes = len(request.POST.getlist('red_social_nombre'))

        if request.POST['red_social_url']:
            for i in range(list_redes):
                red_social_form = RedSocialForm({
                    'nombre': request.POST.getlist('red_social_nombre')[i],
                    'link': request.POST.getlist('red_social_url')[i]
                })
                if not red_social_form.is_valid():
                    context['error'] = red_social_form.errors
                    return render(request, 'webAdminRadio/editar_usuario.html', context)

        if user_form.is_valid():
            user_form.save()
            edit_telefono.nro_telefono = request.POST['telefono']
            edit_telefono.save()
            redes.delete()
            if request.POST['red_social_url']:
                for i in range(list_redes):
                    RedSocial_usuario.objects.create(
                        idUsuario=edit_usuario,
                        nombre=request.POST.getlist('red_social_nombre')[i],
                        link=request.POST.getlist('red_social_url')[i]
                    )
            context['success'] = '¡El usuario ha sido modificado exitosamente!'
        else:
            context['error'] = user_form.errors
    return render(request, 'webAdminRadio/editar_usuario.html', context)

@login_required
def modificar_publicidad(request, id_publicidad):
    edit_publicidad = Publicidad.objects.get(id=id_publicidad)
    horarios = Frecuencia.objects.filter(pk__in=frecuencia_publicidad.objects.filter(idPublicidad=edit_publicidad))
    list_emisoras = Emisora.objects.all()
    list_segmentos = Segmento.objects.filter(pk__in=segmento_publicidad.objects.filter(idPublicidad=edit_publicidad).values('idSegmento'))
    list_segmentos_publicidad = segmento_publicidad.objects.filter(idPublicidad=edit_publicidad)
    context = {
        'title': 'Editar Publicidad',
        'publicidad': edit_publicidad,
        'emisoras': list_emisoras,
        'horarios': json.dumps(list(horarios.values('tipo','dia_semana', 'hora_inicio', 'hora_fin')), cls=DjangoJSONEncoder),
        'segmentos': json.dumps(list(list_segmentos.values('id', 'nombre')), cls=DjangoJSONEncoder)
    }
    if request.POST:
        publicidad_form = PublicidadForm(request.POST, request.FILES, instance=edit_publicidad)
        if publicidad_form.is_valid():
            publicidad_form.save()
            horarios.delete()
            list_segmentos_publicidad.delete()
            for i in range(len(request.POST.getlist('dia'))):
                frecuencia_form = FrecuenciaForm({
                    'tipo': request.POST.getlist('tipo')[i],
                    'dia': request.POST.getlist('dia')[i],
                    'inicio': request.POST.getlist('inicio')[i],
                    'fin': request.POST.getlist('fin')[i]
                })
                if frecuencia_form.is_valid():
                    frecuencia_form.save()
                    frecuencia_publicidad.objects.create(
                        idPublicidad=edit_publicidad,
                        idFrecuencia=Frecuencia.objects.order_by('-id')[0]
                    )
                else:
                    context['error'] = frecuencia_form.errors
                    break
            for s in request.POST.getlist('segmento'):
                segmento_publicidad.objects.create(
                    idPublicidad=edit_publicidad,
                    idSegmento=Segmento.objects.get(id=s)
                )
            if 'error' not in context:
                context['success'] = '¡El registro ha sido modificado con éxito!'
        else:
            context['error'] = publicidad_form.errors
        return render(request, 'webAdminRadio/editar_publicidad.html', context)
    return render(request, 'webAdminRadio/editar_publicidad.html', context)

@login_required
def modificar_concurso(request, id_encuesta):
    emisoras = Emisora.objects.filter(activo='A')
    edit_encuesta = Encuesta.objects.get(id=id_encuesta)
    edit_concurso = Concurso.objects.get(idEncuesta=edit_encuesta)
    usuarios = Usuario.objects.all()
    segmentos = Segmento.objects.filter(idEmisora=edit_encuesta.idEmisora)
    list_preguntas = Pregunta.objects.filter(idEncuesta=edit_encuesta)
    preguntas = []

    for pregunta in list_preguntas:
        objects_preguntas = {}
        opciones = []
        objects_preguntas['pregunta'] = pregunta.contenido
        objects_preguntas['tipo']= pregunta.tipo
        objects_preguntas['respuesta_correcta']= pregunta.respuesta_c
        list_alterntivas = Alternativa.objects.filter(idPregunta=pregunta)
        for alternativa in list_alterntivas:
            opcion = {}
            opcion['opcion'] = alternativa.contenido
            opciones.append(opcion)
        objects_preguntas['opciones'] = opciones
        preguntas.append(objects_preguntas)

    context = {
        'title': "Editar Concurso",
        'emisoras': emisoras,
        'concurso': edit_concurso,
        'encuesta': edit_encuesta,
        'usuarios': usuarios,
        'segmentos': segmentos,
        'preguntas': json.dumps(preguntas, ensure_ascii=False)
    }

    if request.POST:
        encuesta_form = EncuestaFrom(request.POST, instance=edit_encuesta)
        if encuesta_form.is_valid():
            encuesta_form.save()
            list_preguntas.delete()
            # Iterando por cada pregunta con sus respectivas alternativas
            for i in range(len(request.POST.getlist('preguntas'))):
                pregunta_form = PreguntaForm({
                    'contenido': request.POST.getlist('preguntas')[i],
                    'tipo': request.POST.getlist('tipo')[i],
                    'respuesta_c': request.POST.getlist('respuesta_correcta')[i],
                    'idEncuesta': edit_encuesta.id
                })
                if pregunta_form.is_valid():
                    new_pregunta = pregunta_form.save()
                    for j in range(len(request.POST.getlist('respuesta' + str(i)))):
                        alternativa_form = AlternativaForm({
                            'contenido': request.POST.getlist('respuesta' + str(i))[j],
                            'idPregunta': new_pregunta.id
                        })
                        if alternativa_form.is_valid():
                            alternativa_form.save()
                        else:
                            context['error'] = alternativa_form.errors
                            return render(request, 'webAdminRadio/agregar_concurso.html', context)
                else:
                    context['error'] = pregunta_form.errors
                    return render(request, 'webAdminRadio/agregar_concurso.html', context)

            concurso_form = ConcursoForm({
                'idEncuesta' : edit_encuesta.id,
                'idUsuario': request.POST['usuario'],
                'premios': request.POST['premios']
            }, instance=edit_concurso)
            if concurso_form.is_valid():
                concurso_form.save()
            else:
                context['error'] = concurso_form.errors
        else:
            context['error'] = encuesta_form.errors
        if 'error' not in context:
            context['success'] = '¡Se ha modificado el concuro con éxito!'

    return render(request, 'webAdminRadio/editar_concurso.html', context)

def modificar_encuesta(request, id_encuesta):
    emisoras = Emisora.objects.filter(activo='A')
    edit_encuesta = Encuesta.objects.get(id=id_encuesta)
    segmentos = Segmento.objects.filter(idEmisora=edit_encuesta.idEmisora)
    list_preguntas = Pregunta.objects.filter(idEncuesta=edit_encuesta)
    preguntas = []

    for pregunta in list_preguntas:
        objects_preguntas = {}
        opciones = []
        objects_preguntas['pregunta'] = pregunta.contenido
        list_alterntivas = Alternativa.objects.filter(idPregunta=pregunta)
        for alternativa in list_alterntivas:
            opcion = {}
            opcion['opcion'] = alternativa.contenido
            opciones.append(opcion)
        objects_preguntas['opciones'] = opciones
        preguntas.append(objects_preguntas)

    context = {
        'title': "Editar Encuesta",
        'emisoras': emisoras,
        'encuesta': edit_encuesta,
        'segmentos': segmentos,
        'preguntas': json.dumps(preguntas, ensure_ascii=False)
    }

    if request.POST:
        encuesta_form = EncuestaFrom(request.POST, instance=edit_encuesta)
        if encuesta_form.is_valid():
            encuesta_form.save()
            list_preguntas.delete()
            # Iterando por cada pregunta con sus respectivas alternativas
            for i in range(len(request.POST.getlist('preguntas'))):
                pregunta_form = PreguntaForm({
                    'contenido': request.POST.getlist('preguntas')[i],
                    'idEncuesta': edit_encuesta.id
                })
                if pregunta_form.is_valid():
                    new_pregunta = pregunta_form.save()
                    for j in range(len(request.POST.getlist('respuesta' + str(i)))):
                        alternativa_form = AlternativaForm({
                            'contenido': request.POST.getlist('respuesta' + str(i))[j],
                            'idPregunta': new_pregunta.id
                        })
                        if alternativa_form.is_valid():
                            alternativa_form.save()
                        else:
                            context['error'] = alternativa_form.errors
                            return render(request, 'webAdminRadio/agregar_encuesta.html', context)
                else:
                    context['error'] = pregunta_form.errors
                    return render(request, 'webAdminRadio/agregar_encuesta.html', context)
        else:
            context['error'] = encuesta_form.errors
        if 'error' not in context:
            context['success'] = '¡Se ha guardado la encuesta con éxito!'

    return render(request, 'webAdminRadio/editar_encuesta.html', context)

#Sección ver

@login_required
def ver_segmento(request, id_segmento):
    segmento = Segmento.objects.get(id=id_segmento)
    context = {
        'title': 'Información del segmento',
        'segmento': segmento
    }
    return render(request, 'webAdminRadio/ver_segmento.html', context)

@login_required
def ver_locutor(request, id_locutor):
    edit_segmento = segmento_usuario.objects.filter(idUsuario=id_locutor)
    locutor = Usuario.objects.get(id=id_locutor)
    telefono = Telefono_Usuario.objects.get(idUsuario=locutor)
    context = {
        'title': "Informacion del locutor",
        'locutor': locutor,
        'telefono': telefono,
        'segmentos': edit_segmento
    }
    return render(request, 'webAdminRadio/ver_locutor.html', context)

@login_required
def ver_usuario(request, id_usuario):
    usuario = Usuario.objects.get(id=id_usuario)
    telefono = Telefono_Usuario.objects.get(idUsuario=id_usuario)
    redes = RedSocial_usuario.objects.filter(idUsuario=id_usuario)
    context = {
        'title': 'Información del Usuario',
        'usuario': usuario,
        'telefono': telefono,
        'redes': redes
    }
    return render(request, 'webAdminRadio/ver_usuario.html', context)

@login_required
def ver_publicidad(request, id_publicidad):
    publicidad = Publicidad.objects.get(id=id_publicidad)
    segmento = segmento_publicidad.objects.filter(idPublicidad=id_publicidad)
    frecuencia = frecuencia_publicidad.objects.filter(idPublicidad=id_publicidad)
    context = {
        'title': "Informacion de la publicidad",
        'publicidad':publicidad,
        'segmentos': segmento,
        'horarios': frecuencia
    }
    return render(request, 'webAdminRadio/ver_publicidad.html', context)

@login_required
def ver_concursos(request, id_encuesta):
    encuesta = Encuesta.objects.get(id=id_encuesta)
    concurso = Concurso.objects.get(idEncuesta=encuesta)
    preguntas = Pregunta.objects.filter(idEncuesta=encuesta)
    context = {
        'title': "Información del concurso",
        'concurso': concurso,
        'encuesta': encuesta,
        'preguntas': preguntas
    }
    return render(request, 'webAdminRadio/ver_concursos.html', context)

@login_required
def ver_encuesta(request, id_encuesta):
    encuesta = Encuesta.objects.get(id=id_encuesta)
    preguntas = Pregunta.objects.filter(idEncuesta=id_encuesta)
    context = {
        'title': "Información de la encuesta",
        'encuesta': encuesta,
        'preguntas': preguntas
    }
    return render(request, 'webAdminRadio/ver_encuesta.html', context)

#Sección borrar

@login_required
def borrar_emisora(request, id_emisora):
    delete_segmento = Emisora.objects.get(id=id_emisora)
    delete_segmento.activo = 'I'
    delete_segmento.save()
    messages.success(request, 'La emisora ha sido eliminada')
    return redirect('webadminradio:emisoras')

@login_required
def borrar_segmento(request, id_segmento):
    delete_segmento = Segmento.objects.get(id=id_segmento)
    delete_segmento.activo = 'I'
    delete_segmento.save()
    messages.success(request, 'El segmento ha sido eliminado')
    return redirect('webadminradio:segmentos')

@login_required
def borrar_publicidad(request, id_publicidad):
    delete_publicidad = Publicidad.objects.get(id=id_publicidad)
    delete_publicidad.estado = 'I'
    delete_publicidad.save()
    messages.success(request, 'La publicidad ha sido eliminada con exito')
    return redirect('webadminradio:publicidad')

@login_required
def borrar_locutor(request, id_locutor):
    delete_locutor = Usuario.objects.get(id=id_locutor)
    delete_locutor.is_active = False
    delete_locutor.save()
    messages.success(request, 'El locutor ha sido eliminado')
    return redirect('webadminradio:locutores')

@login_required
def borrar_concurso(request, id_encuesta):
    delete_concurso = Concurso.objects.get(idEncuesta=id_encuesta)
    delete_concurso.idEncuesta.activo = 'I'
    delete_concurso.idEncuesta.save()
    delete_concurso.activo = 'I'
    delete_concurso.save()
    messages.success(request, 'El concurso ha sido eliminado')
    return redirect('webadminradio:concursos')

@login_required
def borrar_encuesta(request, id_encuesta):
    delete_encuesta = Encuesta.objects.get(id=id_encuesta)
    delete_encuesta.activo = 'I'
    delete_encuesta.save()
    messages.success(request, 'La encuesta ha sido eliminada con éxito')
    return redirect('webadminradio:encuestas')

@login_required
def borrar_usuario(request, id_usuario):
    delete_usuario = Usuario.objects.get(id=id_usuario)
    delete_usuario.is_active = False
    delete_usuario.save()
    messages.success(request, 'El usuario ha sido eliminado')
    return redirect('webadminradio:usuarios')

@login_required
def asignar_locutor(request):
    list_emisoras = Emisora.objects.all()
    context = {
        'title': 'Asignar Locutor',
        'emisoras': list_emisoras
    }
    return render(request, 'webAdminRadio/asignar_locutor.html', context)

@login_required
def asignar_locutor_segmento(request, id_locutor, id_segmento):
    new_locutor = Usuario.objects.get(id=id_locutor)
    segmento = Segmento.objects.get(id=id_segmento)
    new_locutor.rol = 'L'
    new_locutor.save()
    segmento_usuario.objects.create(
        idSegmento=segmento,
        idUsuario=new_locutor
    )
    messages.success(request, 'El usuario ha sido asignado como locutor')
    return redirect('webadminradio:asignar_locutor')
    return render(request, 'webAdminRadio/ver_encuesta.html', context)
