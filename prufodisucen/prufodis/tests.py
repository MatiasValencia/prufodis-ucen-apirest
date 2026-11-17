import tempfile
from datetime import time

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from prufodis_usuarios.models import Usuario
from .models import (
    Asignatura,
    Asistencia,
    AsistenciaEstudiante,
    Competencia,
    DocumentoEstudiante,
    Estudiante,
    Evaluaciones,
    REQUIRED_FIELD_ERROR,
    TipoCompetencia,
)
from .serializers import (
    AsignaturaSerializer,
    AsistenciaSerializer,
    DocumentoEstudianteSerializer,
    EstudianteSerializer,
    EvaluacionesSerializer,
)


class EstudianteValidationTests(TestCase):
    def estudiante_data(self, **overrides):
        data = {
            "nombres": "Ana",
            "primerApellido": "Pérez",
            "segundoApellido": "González",
            "rut": "1234567-K",
            "apoderado": "María Pérez",
            "telefono": "912345678",
        }
        data.update(overrides)
        return data

    def test_required_fields_reject_missing_and_blank_values(self):
        serializer = EstudianteSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), {
            "nombres",
            "primerApellido",
            "segundoApellido",
            "rut",
            "apoderado",
            "telefono",
        })
        for field_errors in serializer.errors.values():
            self.assertEqual(str(field_errors[0]), REQUIRED_FIELD_ERROR)

        serializer = EstudianteSerializer(data=self.estudiante_data(nombres=""))

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["nombres"][0]),
            REQUIRED_FIELD_ERROR,
        )

    def test_rut_accepts_supported_formats_and_rejects_invalid_format(self):
        for rut in ("1234567-K", "12345678-9"):
            with self.subTest(rut=rut):
                serializer = EstudianteSerializer(
                    data=self.estudiante_data(rut=rut)
                )
                self.assertTrue(serializer.is_valid(), serializer.errors)

        serializer = EstudianteSerializer(
            data=self.estudiante_data(rut="123456-K")
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("Ingrese un RUT válido.", str(serializer.errors["rut"][0]))

    def test_phone_requires_nine_digits_and_preserves_leading_zero(self):
        serializer = EstudianteSerializer(
            data=self.estudiante_data(telefono="012345678")
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["telefono"], "012345678")

        for telefono in ("12345678", "1234567890"):
            with self.subTest(telefono=telefono):
                serializer = EstudianteSerializer(
                    data=self.estudiante_data(telefono=telefono)
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn(
                    "Inserte un número de teléfono de 9 dígitos.",
                    str(serializer.errors["telefono"][0]),
                )

    def test_model_full_clean_rejects_missing_required_fields(self):
        estudiante = Estudiante()

        with self.assertRaises(ValidationError) as error:
            estudiante.full_clean()

        self.assertEqual(
            set(error.exception.message_dict),
            {
                "nombres",
                "primerApellido",
                "segundoApellido",
                "rut",
                "apoderado",
                "telefono",
            },
        )
        for field_errors in error.exception.message_dict.values():
            self.assertEqual(field_errors, [REQUIRED_FIELD_ERROR])

    def test_existing_rut_is_rejected(self):
        data = self.estudiante_data()
        Estudiante.objects.create(**data)

        serializer = EstudianteSerializer(
            data=self.estudiante_data(telefono="912345679")
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["rut"][0]),
            "Este RUT ya está registrado.",
        )

    def test_existing_phone_is_rejected(self):
        data = self.estudiante_data()
        Estudiante.objects.create(**data)

        serializer = EstudianteSerializer(
            data=self.estudiante_data(rut="12345678-9")
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["telefono"][0]),
            "Este teléfono ya está registrado.",
        )


class DocumentoEstudianteTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username="psicologo",
            password="test-password",
            email="psicologo@example.com",
        )
        Usuario.objects.create(usuario=usuario, rol="psicologo")
        self.client = APIClient()
        self.client.force_authenticate(user=usuario)
        self.estudiante = Estudiante.objects.create(
            nombres="Ana",
            primerApellido="Pérez",
            segundoApellido="González",
            rut="1234567-K",
            apoderado="María Pérez",
            telefono="912345678",
        )

    def test_api_uploads_document_linked_to_student(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    "/documentos-estudiante/",
                    {
                        "estudiante": self.estudiante.pk,
                        "archivo": SimpleUploadedFile(
                            "informe.pdf",
                            b"contenido del informe",
                            content_type="application/pdf",
                        ),
                    },
                    format="multipart",
                )

                self.assertEqual(response.status_code, 201, response.data)
                documento = DocumentoEstudiante.objects.get(pk=response.data["id"])
                self.assertEqual(documento.estudiante, self.estudiante)
                self.assertTrue(documento.archivo.storage.exists(documento.archivo.name))
                self.assertEqual(response.data["archivo"].split("/")[-1], "informe.pdf")

                listado = self.client.get(
                    "/documentos-estudiante/",
                    {"estudiante": self.estudiante.pk},
                )
                self.assertEqual(listado.status_code, 200)
                self.assertEqual([item["id"] for item in listado.data], [documento.pk])

    def test_serializer_rejects_unsupported_file_extensions(self):
        serializer = DocumentoEstudianteSerializer(
            data={
                "estudiante": self.estudiante.pk,
                "archivo": SimpleUploadedFile("programa.exe", b"no permitido"),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("archivo", serializer.errors)


class RolPermissionsTests(TestCase):
    def setUp(self):
        self.estudiante = Estudiante.objects.create(
            nombres="Ana",
            primerApellido="Pérez",
            segundoApellido="González",
            rut="1234567-K",
            apoderado="María Pérez",
            telefono="912345678",
        )
        self.otro_estudiante = Estudiante.objects.create(
            nombres="Luis",
            primerApellido="Soto",
            segundoApellido="Díaz",
            rut="12345678-9",
            apoderado="Juan Soto",
            telefono="912345679",
        )
        self.asignatura = Asignatura.objects.create(
            nombre="Matemáticas",
            cantidadNotas=2,
            porcentajeNotas=[50, 50],
        )
        self.asignatura.estudiantes.add(self.estudiante)
        self.otra_asignatura = Asignatura.objects.create(
            nombre="Historia",
            cantidadNotas=2,
            porcentajeNotas=[50, 50],
        )
        self.otra_asignatura.estudiantes.add(self.otro_estudiante)
        self.perfiles = {}
        for rol in Usuario.Rol.values:
            user = get_user_model().objects.create_user(
                username=rol,
                password="test-password",
            )
            perfil = Usuario.objects.create(
                usuario=user,
                rol=rol,
            )
            if rol == Usuario.Rol.PROFESOR:
                perfil.asignaturas.add(self.asignatura)
            self.perfiles[rol] = perfil

    def client_for(self, rol):
        client = APIClient()
        client.force_authenticate(user=self.perfiles[rol].usuario)
        return client

    def assert_forbidden(self, response):
        self.assertEqual(response.status_code, 403, response.data)
        self.assertEqual(
            response.data["detail"],
            "Usted no tiene los permisos para realizar esta tarea",
        )

    def test_roles_can_read_all_resources_but_only_write_allowed_resources(self):
        cases = (
            (
                Usuario.Rol.ADMINISTRADOR,
                ("/estudiantes/", "/asignaturas/"),
                (
                    "/documentos-estudiante/",
                    "/documentos-asignatura/",
                    "/asistencia/",
                    "/asistencia-estudiante/",
                    "/tipo-competencias/",
                    "/competencias/",
                    "/evaluaciones/",
                    "/usuarios/",
                ),
            ),
            (
                Usuario.Rol.PROFESOR,
                (
                    "/asistencia/",
                    "/asistencia-estudiante/",
                    "/evaluaciones/",
                    "/documentos-asignatura/",
                    "/asignaturas/",
                ),
                (
                    "/estudiantes/",
                    "/documentos-estudiante/",
                    "/tipo-competencias/",
                    "/competencias/",
                    "/usuarios/",
                ),
            ),
            (
                Usuario.Rol.PSICOLOGO,
                (
                    "/documentos-estudiante/",
                    "/tipo-competencias/",
                    "/competencias/",
                ),
                (
                    "/estudiantes/",
                    "/documentos-asignatura/",
                    "/asignaturas/",
                    "/asistencia/",
                    "/asistencia-estudiante/",
                    "/evaluaciones/",
                    "/usuarios/",
                ),
            ),
        )

        for rol, permitidas, denegadas in cases:
            client = self.client_for(rol)
            for path in permitidas:
                with self.subTest(rol=rol, path=path):
                    self.assertEqual(client.get(path).status_code, 200)
            for path in denegadas:
                with self.subTest(rol=rol, path=path):
                    self.assertEqual(client.get(path).status_code, 200)
                    for method in ("post", "put", "patch", "delete"):
                        with self.subTest(method=method):
                            response = getattr(client, method)(
                                path,
                                {},
                                format="json",
                            )
                            self.assert_forbidden(response)

    def test_professor_can_only_read_and_write_assigned_subject_records(self):
        cliente = self.client_for(Usuario.Rol.PROFESOR)
        asistencia_otra_asignatura = Asistencia.objects.create(
            asignatura=self.otra_asignatura,
            fecha="2026-11-15",
            horaInicio="09:00:00",
            horaFin="10:00:00",
        )
        response = cliente.get("/asistencia/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        self.assert_forbidden(
            cliente.get(f"/asistencia/{asistencia_otra_asignatura.pk}/")
        )

        response = cliente.post(
            "/asistencia/",
            {
                "asignatura": self.asignatura.pk,
                "fecha": "2026-11-16",
                "horaInicio": "09:00:00",
                "horaFin": "10:00:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        asistencia = Asistencia.objects.get(pk=response.data["id"])

        response = cliente.post(
            "/asistencia-estudiante/",
            {
                "asistencia": asistencia.pk,
                "estudiante": self.otro_estudiante.pk,
                "presente": True,
            },
            format="json",
        )
        self.assert_forbidden(response)
        self.assertFalse(AsistenciaEstudiante.objects.exists())

        for asignatura, estudiante in (
            (self.asignatura, self.otro_estudiante),
            (self.otra_asignatura, self.otro_estudiante),
        ):
            response = cliente.post(
                "/evaluaciones/",
                {
                    "asignatura": asignatura.pk,
                    "estudiante": estudiante.pk,
                    "nota": "6.0",
                },
                format="json",
            )
            self.assert_forbidden(response)
        self.assertFalse(Evaluaciones.objects.exists())

        response = cliente.post(
            "/evaluaciones/",
            {
                "asignatura": self.asignatura.pk,
                "estudiante": self.estudiante.pk,
                "nota": "6.0",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)

    def test_professor_can_access_records_for_each_assigned_subject(self):
        perfil = self.perfiles[Usuario.Rol.PROFESOR]
        perfil.asignaturas.add(self.otra_asignatura)
        cliente = self.client_for(Usuario.Rol.PROFESOR)

        asistencia = Asistencia.objects.create(
            asignatura=self.otra_asignatura,
            fecha="2026-11-16",
            horaInicio="09:00:00",
            horaFin="10:00:00",
        )

        response = cliente.get("/asistencia/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual([item["id"] for item in response.data], [asistencia.pk])

        response = cliente.get(f"/asistencia/{asistencia.pk}/")
        self.assertEqual(response.status_code, 200, response.data)

        response = cliente.post(
            "/evaluaciones/",
            {
                "asignatura": self.otra_asignatura.pk,
                "estudiante": self.otro_estudiante.pk,
                "nota": "6.0",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)

    def test_admin_can_create_subject_without_students(self):
        response = self.client_for(Usuario.Rol.ADMINISTRADOR).post(
            "/asignaturas/",
            {
                "nombre": "Ciencias",
                "cantidadNotas": 1,
                "porcentajeNotas": [100],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        asignatura = Asignatura.objects.get(pk=response.data["id"])
        self.assertFalse(asignatura.estudiantes.exists())

    def test_professor_can_only_manage_students_in_assigned_subject(self):
        cliente = self.client_for(Usuario.Rol.PROFESOR)

        response = cliente.get("/asignaturas/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data],
            [self.asignatura.pk],
        )
        self.assert_forbidden(cliente.get(f"/asignaturas/{self.otra_asignatura.pk}/"))
        self.assert_forbidden(
            cliente.post(
                "/asignaturas/",
                {
                    "nombre": "Ciencias",
                    "cantidadNotas": 1,
                    "porcentajeNotas": [100],
                },
                format="json",
            )
        )
        self.assert_forbidden(
            cliente.patch(
                f"/asignaturas/{self.asignatura.pk}/",
                {"nombre": "Otro nombre"},
                format="json",
            )
        )
        self.assert_forbidden(
            cliente.delete(f"/asignaturas/{self.asignatura.pk}/")
        )
        self.assertEqual(self.asignatura.nombre, "Matemáticas")
        self.assertTrue(Asignatura.objects.filter(pk=self.asignatura.pk).exists())

        response = cliente.patch(
            f"/asignaturas/{self.asignatura.pk}/",
            {"estudiantes": [self.otro_estudiante.pk]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(
            list(self.asignatura.estudiantes.all()),
            [self.otro_estudiante],
        )

        response = cliente.patch(
            f"/asignaturas/{self.asignatura.pk}/",
            {"estudiantes": None},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(self.asignatura.estudiantes.exists())

    def test_psychologist_can_create_competencies_and_admin_cannot_manage_users(self):
        cliente = self.client_for(Usuario.Rol.PSICOLOGO)
        tipo = TipoCompetencia.objects.create(nombreTipoCompetencia="Social")
        response = cliente.post(
            "/competencias/",
            {
                "nombreCompetencia": "Trabajo en equipo",
                "tipoCompetencia": tipo.pk,
                "estudiante": self.estudiante.pk,
                "descripcion": "Colabora con sus compañeros",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(Competencia.objects.filter(pk=response.data["id"]).exists())

        for rol in Usuario.Rol.values:
            with self.subTest(rol=rol):
                client = self.client_for(rol)
                self.assertEqual(client.get("/usuarios/").status_code, 200)
                self.assert_forbidden(
                    client.post("/usuarios/", {}, format="json")
                )

    def test_psychologist_can_manage_competency_types(self):
        cliente = self.client_for(Usuario.Rol.PSICOLOGO)
        response = cliente.post(
            "/tipo-competencias/",
            {"nombreTipoCompetencia": "Social"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        tipo_id = response.data["id"]

        response = cliente.get("/tipo-competencias/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual([tipo["id"] for tipo in response.data], [tipo_id])

        response = cliente.get(f"/tipo-competencias/{tipo_id}/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["nombreTipoCompetencia"], "Social")

        response = cliente.put(
            f"/tipo-competencias/{tipo_id}/",
            {"nombreTipoCompetencia": "Emocional"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["nombreTipoCompetencia"], "Emocional")

        response = cliente.delete(f"/tipo-competencias/{tipo_id}/")
        self.assertEqual(response.status_code, 204, response.data)
        self.assertFalse(TipoCompetencia.objects.filter(pk=tipo_id).exists())

    def test_authenticated_user_without_role_is_denied(self):
        usuario = get_user_model().objects.create_user(username="sin-rol")
        client = APIClient()
        client.force_authenticate(user=usuario)

        self.assert_forbidden(client.get("/estudiantes/"))

    def test_filter_and_search_controls_respect_route_permissions(self):
        accessible_routes = (
            (Usuario.Rol.ADMINISTRADOR, "/estudiantes/", "rut"),
            (Usuario.Rol.ADMINISTRADOR, "/asignaturas/", "nombre"),
            (Usuario.Rol.PROFESOR, "/documentos-asignatura/", "asignatura"),
            (Usuario.Rol.PROFESOR, "/asistencia/", "fecha"),
            (Usuario.Rol.PROFESOR, "/asistencia-estudiante/", "presente"),
            (Usuario.Rol.PROFESOR, "/evaluaciones/", "nota"),
            (Usuario.Rol.PSICOLOGO, "/documentos-estudiante/", "estudiante"),
            (Usuario.Rol.PSICOLOGO, "/competencias/", "tipoCompetencia"),
        )
        for rol, path, filter_field in accessible_routes:
            with self.subTest(rol=rol, path=path):
                response = self.client_for(rol).get(
                    path,
                    HTTP_ACCEPT="text/html",
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'name="search"')
                self.assertContains(response, f'name="{filter_field}"')

        response = self.client_for(Usuario.Rol.PSICOLOGO).get(
            "/estudiantes/",
            HTTP_ACCEPT="text/html",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="search"')
        self.assertContains(response, 'name="rut"')

    def test_filter_and_search_controls_are_absent_from_root_and_login(self):
        response = self.client_for(Usuario.Rol.PSICOLOGO).get(
            "/",
            HTTP_ACCEPT="text/html",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="search"')
        self.assertNotContains(response, 'name="rut"')

        response = APIClient().get(
            "/api-auth/login/",
            HTTP_ACCEPT="text/html",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="search"')
        self.assertNotContains(response, 'name="rut"')

    def test_filter_and_search_query_params_filter_list_results(self):
        response = self.client_for(Usuario.Rol.ADMINISTRADOR).get(
            "/estudiantes/?rut=1234567-K&search=Ana"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [self.estudiante.pk])


class AsignaturaValidationTests(TestCase):
    def asignatura(self, **overrides):
        data = {
            "nombre": "Matemáticas",
            "cantidadNotas": 3,
            "porcentajeNotas": [30, 30, 40],
        }
        data.update(overrides)
        return Asignatura(**data)

    def test_cantidad_notas_must_be_greater_than_zero(self):
        asignatura = self.asignatura(cantidadNotas=0)

        with self.assertRaises(ValidationError) as error:
            asignatura.full_clean()

        self.assertEqual(
            error.exception.message_dict["cantidadNotas"],
            ["Ingrese una cantidad válida de notas, mayor a 0"],
        )

    def test_porcentajes_report_each_invalid_combination(self):
        cases = (
            (
                {"cantidadNotas": 2, "porcentajeNotas": [50, 50, 0]},
                "La cantidad de porcentajes debe ser la misma cantidad de notas "
                "de la asignatura.",
            ),
            (
                {"cantidadNotas": 2, "porcentajeNotas": [40, 40]},
                "El total de los porcentajes debe ser 100.",
            ),
            (
                {"cantidadNotas": 3, "porcentajeNotas": [20, 20]},
                "La cantidad de porcentajes y cantidad de notas deben coincidir, "
                "y también deben sumar 100.",
            ),
        )

        for overrides, mensaje in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValidationError) as error:
                    self.asignatura(**overrides).full_clean()

                self.assertEqual(
                    error.exception.message_dict["porcentajeNotas"],
                    [mensaje],
                )

    def test_serializer_allows_empty_or_null_students_and_preserves_relation(self):
        estudiante = Estudiante.objects.create(
            nombres="Ana",
            primerApellido="Pérez",
            segundoApellido="González",
            rut="1234567-K",
            apoderado="María Pérez",
            telefono="912345678",
        )
        data = {
            "nombre": "Matemáticas",
            "cantidadNotas": 3,
            "porcentajeNotas": [30, 30, 40],
            "estudiantes": [],
        }
        serializer = AsignaturaSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        asignatura_sin_estudiantes = serializer.save()
        self.assertFalse(asignatura_sin_estudiantes.estudiantes.exists())

        data["estudiantes"] = None
        serializer = AsignaturaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["estudiantes"], [])

        data["estudiantes"] = [estudiante.pk]
        serializer = AsignaturaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        asignatura = serializer.save()
        self.assertEqual(list(asignatura.estudiantes.all()), [estudiante])


class AsistenciaValidationTests(TestCase):
    def setUp(self):
        self.asignatura = Asignatura.objects.create(
            nombre="Matemáticas",
            cantidadNotas=1,
            porcentajeNotas=[100],
        )

    def test_end_time_must_be_later_than_start_time(self):
        for hora_fin in ("08:00:00", "09:00:00"):
            with self.subTest(hora_fin=hora_fin):
                asistencia = Asistencia(
                    asignatura=self.asignatura,
                    fecha="2026-11-15",
                    horaInicio="09:00:00",
                    horaFin=hora_fin,
                )

                with self.assertRaises(ValidationError) as error:
                    asistencia.full_clean()

                self.assertEqual(
                    error.exception.message_dict["horaFin"],
                    [
                        "La hora de fin de la clase debe ser mayor a la hora de inicio"
                    ],
                )

    def test_serializer_accepts_later_end_time_and_rejects_earlier_end_time(self):
        data = {
            "asignatura": self.asignatura.pk,
            "fecha": "2026-11-15",
            "horaInicio": "09:00:00",
            "horaFin": "10:00:00",
        }
        serializer = AsistenciaSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        data["horaFin"] = "08:00:00"
        serializer = AsistenciaSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["horaFin"][0]),
            "La hora de fin de la clase debe ser mayor a la hora de inicio",
        )

    def test_serializer_formats_times_as_twelve_hour_and_accepts_iso_input(self):
        serializer = AsistenciaSerializer()
        hora_inicio = serializer.fields["horaInicio"]

        self.assertEqual(hora_inicio.to_representation(time(18, 0)), "06:00 PM")
        self.assertEqual(hora_inicio.to_internal_value("18:00:00"), time(18, 0))
        self.assertEqual(hora_inicio.to_internal_value("6:00 pm"), time(18, 0))
        self.assertEqual(hora_inicio.style["input_type"], "text")
        self.assertEqual(
            hora_inicio.style["placeholder"],
            "hh:mm AM/PM",
        )


class EvaluacionesValidationTests(TestCase):
    def setUp(self):
        self.estudiante = Estudiante.objects.create(
            nombres="Ana",
            primerApellido="Pérez",
            segundoApellido="González",
            rut="1234567-K",
            apoderado="María Pérez",
            telefono="912345678",
        )
        self.asignatura = Asignatura.objects.create(
            nombre="Matemáticas",
            cantidadNotas=3,
            porcentajeNotas=[30, 30, 40],
        )

    def serializer(self, nota, asignatura=None):
        return EvaluacionesSerializer(data={
            "asignatura": (asignatura or self.asignatura).pk,
            "estudiante": self.estudiante.pk,
            "nota": nota,
        })

    def test_nota_must_be_between_one_and_seven_inclusive(self):
        for nota in ("1.0", "7.0"):
            with self.subTest(nota=nota):
                serializer = self.serializer(nota)
                self.assertTrue(serializer.is_valid(), serializer.errors)

        for nota in ("0.0", "0.9", "7.1", "10.0"):
            with self.subTest(nota=nota):
                serializer = self.serializer(nota)
                self.assertFalse(serializer.is_valid())
                self.assertEqual(
                    str(serializer.errors["nota"][0]),
                    "La nota debe ser entre un 1.0 y un 7.0",
                )

    def test_model_full_clean_rejects_note_outside_range(self):
        evaluacion = Evaluaciones(
            asignatura=self.asignatura,
            estudiante=self.estudiante,
            nota=10.0,
        )

        with self.assertRaises(ValidationError) as error:
            evaluacion.full_clean()

        self.assertEqual(
            error.exception.message_dict["nota"],
            ["La nota debe ser entre un 1.0 y un 7.0"],
        )

    def test_assignment_note_count_is_the_maximum_number_of_evaluations(self):
        for nota in ("4.0", "5.0", "6.0"):
            serializer = self.serializer(nota)
            self.assertTrue(serializer.is_valid(), serializer.errors)
            serializer.save()

        serializer = self.serializer("7.0")
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["asignatura"][0]),
            "No se pueden agregar más notas",
        )

        otra_asignatura = Asignatura.objects.create(
            nombre="Historia",
            cantidadNotas=1,
            porcentajeNotas=[100],
        )
        serializer = self.serializer("7.0", otra_asignatura)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_model_full_clean_rejects_excess_evaluations(self):
        for nota in ("4.0", "5.0", "6.0"):
            Evaluaciones.objects.create(
                asignatura=self.asignatura,
                estudiante=self.estudiante,
                nota=nota,
            )

        evaluacion = Evaluaciones(
            asignatura=self.asignatura,
            estudiante=self.estudiante,
            nota="7.0",
        )
        with self.assertRaises(ValidationError) as error:
            evaluacion.full_clean()

        self.assertEqual(
            error.exception.message_dict["asignatura"],
            ["No se pueden agregar más notas"],
        )

    def test_editing_existing_evaluation_does_not_consume_another_slot(self):
        evaluacion = Evaluaciones.objects.create(
            asignatura=self.asignatura,
            estudiante=self.estudiante,
            nota="4.0",
        )
        for nota in ("5.0", "6.0"):
            serializer = self.serializer(nota)
            self.assertTrue(serializer.is_valid(), serializer.errors)
            serializer.save()

        serializer = EvaluacionesSerializer(
            evaluacion,
            data={"nota": "7.0"},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
