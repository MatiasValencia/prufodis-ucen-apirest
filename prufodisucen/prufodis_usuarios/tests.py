from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from prufodis.models import Asignatura
from .forms import UsuarioInlineForm
from .models import Usuario
from .serializers import UsuarioSerializer


class UsuarioTests(TestCase):
    def setUp(self):
        self.asignatura = Asignatura.objects.create(
            nombre="Matemáticas",
            cantidadNotas=1,
            porcentajeNotas=[100],
        )

    def test_usuario_guarda_rol_y_multiple_asignaturas_para_profesor(self):
        otra_asignatura = Asignatura.objects.create(
            nombre="Historia",
            cantidadNotas=1,
            porcentajeNotas=[100],
        )
        user = get_user_model().objects.create_user(
            username="profesor",
            password="test-password",
            first_name="Ana",
            last_name="Pérez",
        )
        perfil = Usuario.objects.create(
            usuario=user,
            rol="profesor",
        )
        perfil.asignaturas.add(self.asignatura, otra_asignatura)

        self.assertEqual(perfil.rol, "profesor")
        self.assertEqual(
            set(perfil.asignaturas.all()),
            {self.asignatura, otra_asignatura},
        )
        self.assertTrue(user.check_password("test-password"))

    def test_profesor_debe_tener_al_menos_una_asignatura(self):
        serializer = UsuarioSerializer(
            data={"rol": Usuario.Rol.PROFESOR, "asignaturas": []},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("asignaturas", serializer.errors)

    def test_otros_roles_no_pueden_tener_asignaturas(self):
        serializer = UsuarioSerializer(
            data={
                "rol": Usuario.Rol.PSICOLOGO,
                "asignaturas": [self.asignatura.pk],
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("asignaturas", serializer.errors)

    def test_admin_form_requires_and_saves_multiple_professor_subjects(self):
        user = get_user_model().objects.create_user(username="profesor")
        otra_asignatura = Asignatura.objects.create(
            nombre="Historia",
            cantidadNotas=1,
            porcentajeNotas=[100],
        )
        form_data = {
            "usuario": user.pk,
            "rol": Usuario.Rol.PROFESOR,
            "asignaturas": [self.asignatura.pk, otra_asignatura.pk],
        }

        form = UsuarioInlineForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        perfil = form.save()
        self.assertEqual(
            set(perfil.asignaturas.all()),
            {self.asignatura, otra_asignatura},
        )

        form_data["asignaturas"] = []
        form = UsuarioInlineForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("asignaturas", form.errors)

    def test_api_root_requires_login(self):
        client = APIClient()
        self.assertEqual(client.get("/").status_code, 403)
        login_page = client.get("/api-auth/login/")
        self.assertEqual(login_page.status_code, 200)
        self.assertContains(login_page, 'name="email"')
        self.assertNotContains(login_page, 'name="username"')

        user = get_user_model().objects.create_user(
            username="psicologo",
            password="test-password",
            email="psicologo@example.com",
        )
        perfil = Usuario.objects.create(usuario=user, rol="psicologo")
        response = client.post(
            "/api-auth/login/",
            {"username": user.username, "password": "test-password"},
        )
        self.assertEqual(response.status_code, 200)

        response = client.post(
            "/api-auth/login/",
            {"email": user.email, "password": "test-password"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("usuarios", response.data)
        response = client.get("/usuarios/")
        self.assertEqual(response.status_code, 200)
        response = client.post("/usuarios/", {}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Usted no tiene los permisos para realizar esta tarea",
        )

    def test_admin_can_open_user_creation_form_with_role_and_assignment(self):
        admin = get_user_model().objects.create_superuser(
            username="administrador",
            password="test-password",
            email="admin@example.com",
        )
        Usuario.objects.create(usuario=admin, rol="administrador")
        client = APIClient()
        client.force_login(admin)

        response = client.get("/admin/auth/user/add/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rol")
        self.assertContains(response, "Asignaturas")
        self.assertContains(
            response,
            'name="perfil-0-asignaturas"',
        )
        self.assertRegex(
            response.content.decode(),
            r'<select[^>]*name="perfil-0-asignaturas"[^>]*multiple',
        )
