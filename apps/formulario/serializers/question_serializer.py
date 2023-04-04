from apps.formulario.models.question import Question, QuestionHistory
from rest_framework import serializers
from apps.user.serializers.user_serializers import SimpleUserSerializer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id',  'question_bank',
                'reviewed_by', 'answered_by', 'reviewer_observations', 
                'validation', 'question_data', 'answer',
        ]

class QuestionHistorySerializer(serializers.ModelSerializer):
    reviewed_by = SimpleUserSerializer(read_only=True)
    profile =  serializers.SerializerMethodField('get_profile')
    class Meta:
        model = QuestionHistory
        fields = [ 'id',  'created_at',
                'validation',
                'reviewed_by', 'reviewer_observations',
                'profile'
                ]

    def get_profile(self, obj):
        name_group = obj.reviewed_by.groups.first().name
        return name_group
