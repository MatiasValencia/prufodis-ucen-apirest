from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from prufodis.models import Asignatura
from .models import Usuario


class UsuarioTests(TestCase):
    def setUp(self):
        self.asignatura = Asignatura.objects.create(
            nombre="Matemáticas",
            cantidadNotas=1,
            porcentajeNotas=[100],
        )

    def test_usuario_guarda_rol_y_asignatura_para_profesor(self):
        user = get_user_model().objects.create_user(
            username="profesor",
            password="test-password",
            first_name="Ana",
            last_name="Pérez",
        )
        perfil = Usuario.objects.create(
            usuario=user,
            rol="profesor",
            asignatura=self.asignatura,
        )

        self.assertEqual(perfil.rol, "profesor")
        self.assertEqual(perfil.asignatura, self.asignatura)
        self.assertTrue(user.check_password("test-password"))

    def test_profesor_debe_tener_asignatura(self):
        perfil = Usuario(
            rol="profesor",
        )

        with self.assertRaises(ValidationError) as error:
            perfil.full_clean()

        self.assertIn("asignatura", error.exception.message_dict)

    def test_api_root_requires_login(self):
        client = APIClient()
        self.assertEqual(client.get("/").status_code, 403)
        self.assertEqual(client.get("/api-auth/login/").status_code, 200)

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
        self.assertContains(response, "Asignatura")
