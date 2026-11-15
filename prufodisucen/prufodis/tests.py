from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Asignatura, Estudiante, REQUIRED_FIELD_ERROR
from .serializers import AsignaturaSerializer, EstudianteSerializer


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

    def test_serializer_requires_students_and_preserves_many_to_many_relation(self):
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

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["estudiantes"][0]),
            "La asignatura debe tener al menos un estudiante.",
        )

        data["estudiantes"] = [estudiante.pk]
        serializer = AsignaturaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        asignatura = serializer.save()
        self.assertEqual(list(asignatura.estudiantes.all()), [estudiante])
