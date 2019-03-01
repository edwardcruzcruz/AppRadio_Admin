from rest_framework import generics
#Social media imports
#FACEBOOK
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
#TWITTER
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.social_serializers import TwitterLoginSerializer

from django.http import HttpResponse, JsonResponse
from WebAdminRadio import models
from accounts.models import Usuario
from . import serializers
from rest_framework import mixins
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import render

import datetime
# Create your views here.

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

class ListTime(APIView):

    def get(self, request, format=None):
        dicTime= {'fecha': datetime.datetime.now().date(), 'hora': datetime.datetime.now().time()}
        serializer= serializers.TimeSerializer(dicTime)
        return Response(serializer.data)



class ListUsuarios(generics.ListAPIView):
    serializer_class = serializers.UsuarioSerializer
    queryset = Usuario.objects.filter(is_active=True)


##
#GET: Vista que obtiene los segmentos de todas las emisoras
#
class ListSegmento(generics.ListCreateAPIView):
    queryset = models.Segmento.objects.all()
    serializer_class = serializers.SegmentoSerializer


##
#GET: Vista que obtiene los segmentos del dia actual
#
#PARAMS: provincia (para escoger los segmentos por provincia)
#
class ListSegmentosDiaActual(generics.ListAPIView):
    serializer_class= serializers.SegmentoSerializerToday

    def get_queryset(self):
        provincia= self.request.query_params.get('provincia')
        day= datetime.datetime.today().weekday()
        dia_actual=DIAS[day]
        horariosDelDia= models.Horario.objects.filter(dia=dia_actual)
        ids_segmentos= models.segmento_horario.objects.filter(idHorario__in=horariosDelDia).distinct()
        queryset=  models.Segmento.objects.filter(pk__in=ids_segmentos.values('idSegmento'))
        if provincia!= None:
            emisoras= models.Emisora.objects.filter(provincia=provincia.capitalize())
            queryset= queryset.filter(idEmisora__in=emisoras.values('id'))
        return queryset


##
#GET: Vista que obtiene los segmentos del dia actual de una emisora especifica
#
#PARAMS: provincia (para escoger los segmentos por provincia)
#
class ListSegmentosEmisoraDiaActual(generics.ListAPIView):
    serializer_class= serializers.SegmentoSerializerToday

    def get_queryset(self):
        emisora = self.kwargs['id_emisora']
        day= datetime.datetime.today().weekday()
        dia_actual=DIAS[day]
        horariosDelDia= models.Horario.objects.filter(dia=dia_actual)
        ids_segmentos= models.segmento_horario.objects.filter(idHorario__in=horariosDelDia).distinct()
        queryset= models.Segmento.objects.filter(pk__in=ids_segmentos.values('idSegmento'),idEmisora=emisora)
        return queryset


##
#GET: Vista que obtiene todas las emisoras
#
#PARAMS: provincia (para escoger las emisoras por una provincia especifica)
#
class ListEmisora(generics.ListCreateAPIView):
    serializer_class = serializers.EmisoraSerializer

    def get_queryset(self):
        provincia= self.request.query_params.get('provincia')
        if provincia!= None:
            queryset= models.Emisora.objects.filter(provincia=provincia.capitalize())
        else:
            queryset = models.Emisora.objects.all()
        return queryset

class CreateUser(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer

class CreateUserA(APIView, mixins.CreateModelMixin):
    permission_classes = (AllowAny,)


    def post(self, request, format=None):
        serializer = serializers.UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class TwitterLogin(SocialLoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter

# Lista los segmentos de una emisora
class ListEmisoraSegmentos(generics.ListAPIView):
    serializer_class = serializers.SegmentoSerializerFull

    def get_queryset(self):
        emisora = self.kwargs['id_emisora']
        return models.Segmento.objects.filter(idEmisora=emisora, activo='A')

# Lista un segmento de una emisora
class ListEmisoraSegmento(generics.RetrieveAPIView):
    serializer_class = serializers.SegmentoSerializerFull

    def get_object(self):
        emisora = self.kwargs['id_emisora']
        segmento = self.kwargs['id_segmento']
        return models.Segmento.objects.get(id=segmento, idEmisora=emisora, activo='A')


class ListLocutores(generics.ListAPIView):
    serializer_class = serializers.LocutoresSerializer

    def get_serializer_context(self):
        return {'segmento': self.kwargs['id_segmento']}

    def get_queryset(self):
        segmento = self.kwargs['id_segmento']
        return Usuario.objects.filter(id__in=models.segmento_usuario.objects.filter(idSegmento=segmento).values('idUsuario'), is_active=True)

class ListPublicidad(generics.ListAPIView):
    serializer_class = serializers.PublicidadSerializer
    #
    def get_serializer_context(self):
        return {'segmento': self.kwargs['id_segmento']}

    def get_queryset(self):
        segmento = self.kwargs['id_segmento']
        return models.Publicidad.objects.filter(id__in=models.segmento_publicidad.objects.filter(idSegmento=segmento).values('idPublicidad'), estado='A')

class ListFrecuencias(generics.ListAPIView):
    serializer_class = serializers.FrecuenciaSerializer

    def get_queryset(self):
        publicidad = self.kwargs['id_publicidad']
        return models.Frecuencia.objects.filter(id__in=models.frecuencia_publicidad.objects.filter(idPublicidad=publicidad))

##
#GET: Vista que obtiene los telefonos de una emisora
#
class ListTelefonosEmisora(generics.ListCreateAPIView):
    serializer_class = serializers.TelefonoEmisoraSerializer

    def get_queryset(self):
        idemisora= self.kwargs['id_emisora']
        return models.Telefono_emisora.objects.filter(idEmisora=idemisora)


##
#GET: Vista que obtiene las redes sociales de una emisora
#
class ListRedSocialEmisora(generics.ListCreateAPIView):
    serializer_class = serializers.RedSocialEmisoraSerializer

    def get_queryset(self):
        idemisora= self.kwargs['id_emisora']
        return models.RedSocial_emisora.objects.filter(idEmisora=idemisora)


class ListLocutoresSegmento(generics.ListAPIView):
    serializer_class= serializers.LocutoresSegmentoSerializer

    def get_queryset(self):
        id_segmento= self.kwargs['id_segmento']
        results= models.segmento_usuario.objects.filter(idSegmento=id_segmento)
        return Usuario.objects.filter(pk__in=results.values('idUsuario'))


class ListImagenes(generics.ListAPIView):
    serializer_class = serializers.ImagenesSerializer
    queryset = models.Imagenes.objects.all()

class ListImagenesSegmento(generics.ListAPIView):
    serializer_class= serializers.ImagenesSerializer

    def get_queryset(self):
        id_segmento= self.kwargs['id_segmento']
        results= models.Imagenes.objects.filter(segmento=id_segmento)
        return results


class ListVideos(generics.ListAPIView):
    serializer_class = serializers.VideosSerializer
    queryset = models.Videos.objects.all()

class ListVideosSegmento(generics.ListAPIView):
    serializer_class= serializers.VideosSerializer

    def get_queryset(self):
        id_segmento= self.kwargs['id_segmento']
        results= models.Videos.objects.filter(segmento=id_segmento)
        return results


class ListFavoritos(generics.ListAPIView):
    serializer_class = serializers.FavoritoSerializer
    queryset = models.Favorito.objects.all()

class ListFavoritosUsuario(generics.ListAPIView):
    serializer_class= serializers.FavoritoSerializer

    def get_queryset(self):
        usuario= self.kwargs['usuario']
        id_usuario= Usuario.objects.filter(username=usuario).values('id').get()['id']
        results= models.Favorito.objects.filter(usuario=id_usuario)
        queryset= models.Segmento.objects.filter(pk__in=results.values('segmento'))
        return queryset

class ListEncuestas(generics.ListAPIView):
    serializer_class = serializers.EncuestaSerializer

    def get_queryset(self):
        id_segmento = self.kwargs['id_segmento']
        results = models.Encuesta.objects.filter(idSegmento=id_segmento)
        return results

class CreateFavorito(generics.ListCreateAPIView):
    queryset = models.Favorito.objects.all()
    serializer_class = serializers.FavoritoCreateSerializer

def CreateFavoritoView(request, id_segmento,username):

    user = Usuario.objects.get(username=username)

    fav = models.Favorito(usuario = user,segmento = models.Segmento.objects.filter(id=id_segmento)[0])
    fav.save()

    context = {'title': 'Usuarios'}
    return render(request, 'webAdminRadio/usuarios.html', context)

