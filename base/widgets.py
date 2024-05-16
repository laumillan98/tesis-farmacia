from django import forms

class BooleanCheckbox(forms.CheckboxInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_type = 'checkbox'  # Establece el tipo de entrada como checkbox

    def get_context(self, name, value, attrs):
        if value is None:
            value = False  # Si el valor es None, establece el valor por defecto como False (no marcado)
        context = super().get_context(name, value, attrs)
        context['widget']['attrs'].pop('value', None)  # Elimina el atributo 'value' para evitar conflictos
        return context
