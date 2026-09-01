from django import forms

from booking.models import Room


class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('description', 'price')


class BookingCreateForm(forms.Form):
    room_id = forms.ModelChoiceField(queryset=Room.objects.all())
    date_start = forms.DateField(input_formats=['%Y-%m-%d'])
    date_end = forms.DateField(input_formats=['%Y-%m-%d'])

    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')

        if date_start and date_end and date_end < date_start:
            self.add_error(
                'date_end',
                'The end date cannot be earlier than the start date.',
            )

        return cleaned_data


class BookingListForm(forms.Form):
    room_id = forms.IntegerField(min_value=1)