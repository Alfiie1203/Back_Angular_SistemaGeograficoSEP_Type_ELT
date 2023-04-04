from rest_framework import serializers
from apps.company.models.company import Company
from apps.company.serializers.company_serializer import CompanySerializerReview
from ..models.supplybase import SupplyBaseRegister, SupplyBaseDependency, PurchasedPercentage
from apps.company.serializers.actor_type_serializer import ActorTypeSerializer
from apps.traceability.models.traceability import Traceability
from apps.company.models.actor_type import ActorType
from django.db.models import Q
from django.db.models import Sum
from decimal import Decimal

from django.db.models import F


class SupplyBaseRegisterListSerializer(serializers.ModelSerializer):

    company = CompanySerializerReview(read_only=True)
    has_resume = serializers.SerializerMethodField('check_has_resume')
    has_data_traceability = serializers.SerializerMethodField('check_has_data')
    class Meta:
        model = SupplyBaseRegister
        fields = ['id', 'created_by', 'company', 'register_year', 'period', 'purchased_volume',
            'has_resume',
            'has_data_traceability',
            ]

    def check_has_resume(self, obj):
        company = obj.company
        period = obj.period
        year = obj.register_year

        if period == 0:
            return False
        if period == 1:
            if SupplyBaseRegister.objects.filter(company = company, period = 2, register_year = year).exists():
                return True
            else:
                return False
        if period == 2:
            if SupplyBaseRegister.objects.filter(company = company, period = 1, register_year = year).exists():
                return True
            else:
                return False
    
    def check_has_data(self, obj):
        company = obj.company
        period = obj.period
        year = obj.register_year

        if Traceability.objects.filter(reported_company = company, period = period, year = year).exists():
            return True
        else:
            return False

class SupplyBaseDependencySerializer(serializers.ModelSerializer):

    actor_type =  ActorTypeSerializer(read_only=True)
    actor_type_dependency =  ActorTypeSerializer(many = True, read_only=True)
    class Meta:
        model = SupplyBaseDependency
        fields = ['id', 'actor_type', 'actor_type_dependency']

class SupplyBaseRegisterCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupplyBaseRegister
        fields = ['id', 'register_year', 'period', 'purchased_volume']

class SupplyBaseTotalResumeSerializer(serializers.ModelSerializer):

    company = CompanySerializerReview(read_only=True)
    traceability_percentage_1 = serializers.SerializerMethodField('get_traceability_percentage_1')
    traceability_alert_1 = serializers.SerializerMethodField('get_alert_table_1')
    traceability_percentage_2 = serializers.SerializerMethodField('get_traceability_percentage_2')
    traceability_alert_2 = serializers.SerializerMethodField('get_alert_table_2')
    traceability_percentage_resume = serializers.SerializerMethodField('get_traceability_percentage_resume')
    traceability_alert_resume = serializers.SerializerMethodField('get_alert_table_resume')
    
    class Meta:
        model = SupplyBaseRegister
        fields = ['id', 'created_by', 'company',
                'register_year', 'period', 'purchased_volume',
                'traceability_percentage_1',
                'traceability_alert_1',
                'traceability_percentage_2',
                'traceability_alert_2',
                'traceability_percentage_resume',
                'traceability_alert_resume',
                
                
                    ]

    def get_registers_list(self, obj):
        language_code = f'actor_type__name_{self.context["language_code"]}'
        registers = PurchasedPercentage.objects.filter(supplybase_register = obj)
        data_register = registers.values(str(language_code), 'percentage')
        
        return data_register

 

    def get_traceability_percentage_1(self,obj):
        try:
            supply_base_period1 = SupplyBaseRegister.objects.get(company = obj.company, register_year = obj.register_year, period=1)
            traceabilities = Traceability.objects.filter(reported_company = obj.company, year=obj.register_year, period= 1)
            validated_traceabilities = traceabilities.filter(Q(status_revision='VA') | Q(status_revision='VE'))
            verified_traceabilities = traceabilities.filter(status_revision='VE')

            supplybase_registers = PurchasedPercentage.objects.filter(supplybase_register=supply_base_period1)
            #
            trazabilidad_reportada = traceabilities.aggregate(Sum('purchased_volume'))
            supplybase_sum = supplybase_registers.aggregate(Sum('percentage'))
            try:
                razon_reportada = trazabilidad_reportada['purchased_volume__sum']/supplybase_sum['percentage__sum']
            except:
                razon_reportada = 0
            #
            trazabilidad_validada = validated_traceabilities.aggregate(Sum('purchased_volume'))
            try:
                razon_validada = round(trazabilidad_validada['purchased_volume__sum']/supplybase_sum['percentage__sum'],3)
                trazabilidad_validada_percentage = trazabilidad_validada['purchased_volume__sum']*100
            except:
                trazabilidad_validada_percentage = 0
                razon_validada = 0
            #
            trazabilidad_verificada = verified_traceabilities.aggregate(Sum('purchased_volume'))
            try:
                razon_verified = round(trazabilidad_verificada['purchased_volume__sum']/supplybase_sum['percentage__sum'],3)
                trazab_verificada_percentage = trazabilidad_verificada['purchased_volume__sum']*100
            except:
                razon_verified = 0
                trazab_verificada_percentage = 0

            table_data = [
                ['trazabilidad_reportada', str(round(trazabilidad_reportada['purchased_volume__sum']*100, 3))+' %' , str(round(supplybase_sum ['percentage__sum']*100,3)) +' %', str(round(razon_reportada*100,3))+' %'],
                ['trazabilidad_validada', str(round(trazabilidad_validada_percentage,3))+' %' , str(supplybase_sum ['percentage__sum']*100)+' %', str(round(razon_validada*100,3))+' %'],
                ['trazabilidad_verificada', str(round(trazab_verificada_percentage,3))+' %' , str(supplybase_sum ['percentage__sum']*100)+' %', str(round(razon_verified*100,3))+ ' %'],
                ]

        except:
            table_data = [
                ['trazabilidad_reportada', '0 %' , '0 %', '0 %'],
                ['trazabilidad_validada', '0 %' , '0 %', '0 %'],
                ['trazabilidad_verificada', '0 %' , '0 %', '0 %'],
                ]

        return table_data

    def get_alert_table_1(self,obj):
        supply_base_period1 = SupplyBaseRegister.objects.get(company = obj.company, register_year = obj.register_year, period=1)
        traceabilities = Traceability.objects.filter(reported_company = obj.company, year=obj.register_year, period= 1)
        actortype_company = obj.company.actor_type
        actortype_dependency = SupplyBaseDependency.objects.get(actor_type = actortype_company).actor_type_dependency.all()

        language_code = self.context["language_code"]
        field_translated = f'name_{language_code}'
        table_data = []
        
        for actor in actortype_dependency:
            actor_trace = traceabilities.filter(actor_type =actor)
            actor_trace_reportada = actor_trace.aggregate(Sum('purchased_volume'))
            try:
                if actor_trace.count() >0:
                    percentage_reported = PurchasedPercentage.objects.get(supplybase_register = supply_base_period1, actor_type = actor).percentage
                    razon_per_actor = round((actor_trace_reportada['purchased_volume__sum']/percentage_reported)*100, 3)
                    if razon_per_actor == 100:
                        text_alarm = 'OK'
                    if razon_per_actor == 0:
                        text_alarm = 'OK'
                    elif razon_per_actor < 100:
                        text_alarm= 'Incomplete'    
                    elif razon_per_actor >100:
                        text_alarm= 'Overload'
                    data = [ getattr(actor, field_translated) , str(round(actor_trace_reportada['purchased_volume__sum']*100,3)) +' %', str(razon_per_actor)+' %', text_alarm]

                else:
                    if PurchasedPercentage.objects.filter(supplybase_register = supply_base_period1, actor_type = actor).exists():
                        
                        percentage_reported = PurchasedPercentage.objects.get(supplybase_register = supply_base_period1, actor_type = actor).percentage
                        if percentage_reported == 0 and actor_trace.count() >0 :
                            razon_per_actor = round((percentage_reported)*100, 3)
                            text_alarm='Error'
                            data = [ getattr(actor, field_translated) , '0 %', '-'+str(razon_per_actor)+' %', text_alarm]
                        else:
                            razon_per_actor = round((percentage_reported)*100, 3)
                            
                            if razon_per_actor == 0 and actor_trace.count() == 0 :
                                text_alarm='OK'
                                data = [ getattr(actor, field_translated) , '0 %', '0 %', text_alarm]
                            else:
                                text_alarm='Error'
                                data = [ getattr(actor, field_translated) , '0 %', '-'+str(razon_per_actor)+' %', text_alarm]
                    else:
                        razon_per_actor = 0
                        text_alarm = 'OK'
                        data = [ getattr(actor, field_translated) , '0 %', str(razon_per_actor)+' %', text_alarm]
            except:
                data = [ getattr(actor, field_translated) , '0 %', '0 %', 'NA']
            table_data.append(data)

        return table_data

    def get_traceability_percentage_2(self,obj):
        try:
            supply_base_period1 = SupplyBaseRegister.objects.get(company = obj.company, register_year = obj.register_year, period=2)
            traceabilities = Traceability.objects.filter(reported_company = obj.company, year=obj.register_year, period= 2)
            validated_traceabilities = traceabilities.filter(Q(status_revision='VA') | Q(status_revision='VE'))
            verified_traceabilities = traceabilities.filter(status_revision='VE')

            supplybase_registers = PurchasedPercentage.objects.filter(supplybase_register=supply_base_period1)
            #
            trazabilidad_reportada = traceabilities.aggregate(Sum('purchased_volume'))
            supplybase_sum = supplybase_registers.aggregate(Sum('percentage'))
            try:
                razon_reportada = round(trazabilidad_reportada['purchased_volume__sum']/supplybase_sum['percentage__sum'], 3)
            except:
                razon_reportada = 0
            #
            trazabilidad_validada = validated_traceabilities.aggregate(Sum('purchased_volume'))
            try:
                razon_validada = round(trazabilidad_validada['purchased_volume__sum']/supplybase_sum['percentage__sum'],3)
                trazabilidad_validada_percentage = trazabilidad_validada['purchased_volume__sum']*100
            except:
                trazabilidad_validada_percentage = 0
                razon_validada = 0
            #
            trazabilidad_verificada = verified_traceabilities.aggregate(Sum('purchased_volume'))
            try:
                razon_verified = round(trazabilidad_verificada['purchased_volume__sum']/supplybase_sum['percentage__sum'],3)
                trazab_verificada_percentage = trazabilidad_verificada['purchased_volume__sum']*100
            except:
                razon_verified = 0
                trazab_verificada_percentage = 0

            table_data = [
                ['trazabilidad_reportada', str(round(trazabilidad_reportada['purchased_volume__sum']*100,3))+' %' , str(round(supplybase_sum ['percentage__sum']*100,3)) +' %', str(razon_reportada*100)+' %'],
                ['trazabilidad_validada', str(trazabilidad_validada_percentage)+' %' , str(supplybase_sum ['percentage__sum']*100)+' %', str(razon_validada*100)+' %'],
                ['trazabilidad_verificada', str(trazab_verificada_percentage)+' %' , str(supplybase_sum ['percentage__sum']*100)+' %', str(razon_verified*100)+ ' %'],
                ]

        except:
            table_data = [
                ['trazabilidad_reportada', '0 %' , '0 %', '0 %'],
                ['trazabilidad_validada', '0 %' , '0 %', '0 %'],
                ['trazabilidad_verificada', '0 %' , '0 %', '0 %'],
                ]

        return table_data

    def get_alert_table_2(self,obj):
        supply_base_period2 = SupplyBaseRegister.objects.get(company = obj.company, register_year = obj.register_year, period=2)
        traceabilities = Traceability.objects.filter(reported_company = obj.company, year=obj.register_year, period= 2)
        actortype_company = obj.company.actor_type
        actortype_dependency = SupplyBaseDependency.objects.get(actor_type = actortype_company).actor_type_dependency.all()

        language_code = self.context["language_code"]
        field_translated = f'name_{language_code}'
        table_data = []
        
        for actor in actortype_dependency:
            actor_trace = traceabilities.filter(actor_type =actor)
            actor_trace_reportada = actor_trace.aggregate(Sum('purchased_volume'))
            try:
                if actor_trace.count() >0:
                    percentage_reported = PurchasedPercentage.objects.get(supplybase_register = supply_base_period2, actor_type = actor).percentage
                    razon_per_actor = round((actor_trace_reportada['purchased_volume__sum']/percentage_reported)*100, 3)
                    if razon_per_actor == 100:
                        text_alarm = 'OK'
                    if razon_per_actor == 0:
                        text_alarm = 'OK'
                    elif razon_per_actor < 100:
                        text_alarm= 'Incomplete'    
                    elif razon_per_actor >100:
                        text_alarm= 'Overload'
                    data = [ getattr(actor, field_translated) , str(round(actor_trace_reportada['purchased_volume__sum']*100,3)) +' %', str(razon_per_actor)+' %', text_alarm]

                else:
                    if PurchasedPercentage.objects.filter(supplybase_register = supply_base_period2, actor_type = actor).exists():
                        percentage_reported = PurchasedPercentage.objects.get(supplybase_register = supply_base_period2, actor_type = actor).percentage
                        if percentage_reported == 0 and actor_trace.count() >0 :
                            razon_per_actor = round((percentage_reported)*100, 3)
                            text_alarm='Error'
                            data = [ getattr(actor, field_translated) , '0 %', ''+str(razon_per_actor)+' %', text_alarm]
                        else:
                            razon_per_actor = round((percentage_reported)*100, 3)
                            
                            
                            if razon_per_actor == 0 and actor_trace.count() == 0 :
                                text_alarm='OK'
                                data = [ getattr(actor, field_translated) , '0 %', '0 %', text_alarm]
                            else:
                                text_alarm='Error'
                                data = [ getattr(actor, field_translated) , '0 %', '-'+str(razon_per_actor)+' %', text_alarm]

                    else:
                        razon_per_actor = 0
                        text_alarm = 'OK'
                        data = [ getattr(actor, field_translated) , '0 %', str(razon_per_actor)+' %', text_alarm]
            except:
                data = [ getattr(actor, field_translated) , '0 %', '0 %', 'NA']

            table_data.append(data)

        return table_data


    def get_traceability_percentage_resume(self,obj):
        supply_bases = SupplyBaseRegister.objects.filter(company = obj.company, register_year = obj.register_year)
        traceabilities = Traceability.objects.filter(reported_company = obj.company, year=obj.register_year )
        validated_traceabilities = traceabilities.filter(Q(status_revision='VA') | Q(status_revision='VE'))
        verified_traceabilities = traceabilities.filter(status_revision='VE')

        supplybase_registers = PurchasedPercentage.objects.filter(supplybase_register__in=supply_bases)
        #
        trazabilidad_reportada = traceabilities.aggregate(Sum('purchased_volume'))
        supplybase_sum = supplybase_registers.aggregate(Sum('percentage'))
        try:
            razon_reportada = round(trazabilidad_reportada['purchased_volume__sum']/supplybase_sum['percentage__sum'], 3)
        except:
            razon_reportada = 0
        #
        trazabilidad_validada = validated_traceabilities.aggregate(Sum('purchased_volume'))
        try:
            razon_validada = round(trazabilidad_validada['purchased_volume__sum']/supplybase_sum['percentage__sum'], 3)
            trazabilidad_validada_percentage = trazabilidad_validada['purchased_volume__sum']*50
        except:
            trazabilidad_validada_percentage = 0
            razon_validada = 0
        #
        trazabilidad_verificada = verified_traceabilities.aggregate(Sum('purchased_volume'))
        try:
            razon_verified = round(trazabilidad_verificada['purchased_volume__sum']/supplybase_sum['percentage__sum'], 3)
            trazab_verificada_percentage = round(trazabilidad_verificada['purchased_volume__sum']*50, 3)
        except:
            razon_verified = 0
            trazab_verificada_percentage = 0

        table_data = [
            ['trazabilidad_reportada', str(round(trazabilidad_reportada['purchased_volume__sum']*50,3))+' %' , str(round(supplybase_sum ['percentage__sum']*50,3)) +' %', str(razon_reportada*50)+' %'],
            ['trazabilidad_validada', str(trazabilidad_validada_percentage)+' %' , str(round(supplybase_sum ['percentage__sum']*50,3))+' %', str(razon_validada*50)+' %'],
            ['trazabilidad_verificada', str(trazab_verificada_percentage)+' %' , str(round(supplybase_sum ['percentage__sum']*50, 3))+' %', str(razon_verified*50)+ ' %'],
            ]

        return table_data

    def get_alert_table_resume(self,obj):
        supply_bases = SupplyBaseRegister.objects.filter(company = obj.company, register_year = obj.register_year)
        traceabilities = Traceability.objects.filter(reported_company = obj.company, year=obj.register_year )

        actortype_company = obj.company.actor_type
        actortype_dependency = SupplyBaseDependency.objects.get(actor_type = actortype_company).actor_type_dependency.all()

        language_code = self.context["language_code"]
        field_translated = f'name_{language_code}'
        table_data = []
        
        for actor in actortype_dependency:
            actor_trace = traceabilities.filter(actor_type =actor)
            actor_trace_reportada = actor_trace.aggregate(Sum('purchased_volume'))
            if actor_trace.count() >0:
                registros_supply_base = PurchasedPercentage.objects.filter(supplybase_register__in = supply_bases, actor_type = actor)
                percentage_reported = registros_supply_base.aggregate(Sum('percentage'))
                razon_per_actor = round((actor_trace_reportada['purchased_volume__sum']/percentage_reported['percentage__sum'])*100, 3)
                if razon_per_actor == 100:
                    text_alarm = 'OK'
                if razon_per_actor == 0:
                    text_alarm = 'OK'
                elif razon_per_actor < 100:
                    text_alarm= 'Incomplete'    
                elif razon_per_actor >100:
                    text_alarm= 'Overload'
                data = [ getattr(actor, field_translated) , str(round(actor_trace_reportada['purchased_volume__sum']*100,3)) +' %', str(razon_per_actor)+' %', text_alarm]

            else:
                if PurchasedPercentage.objects.filter(supplybase_register__in = supply_bases, actor_type = actor).exists():
                    registros_supply_base = PurchasedPercentage.objects.filter(supplybase_register__in = supply_bases, actor_type = actor)
                    percentage_reported = registros_supply_base.aggregate(Sum('percentage'))
                    if percentage_reported == 0 and actor_trace.count() >0 :
                        razon_per_actor = round((percentage_reported['percentage__sum'])*100, 3)
                        text_alarm='Error'
                        data = [ getattr(actor, field_translated) , '0 %', '-'+str(razon_per_actor)+' %', text_alarm]
                    else:
                        razon_per_actor = round((percentage_reported['percentage__sum'])*100, 3)
                        
                        
                        if razon_per_actor == 0 and actor_trace.count() == 0 :
                            text_alarm='OK'
                            data = [ getattr(actor, field_translated) , '0 %', '0 %', text_alarm]
                        else:
                            text_alarm='Error'
                            data = [ getattr(actor, field_translated) , '0 %', '-'+str(razon_per_actor)+' %', text_alarm]


                else:
                    razon_per_actor = 0
                    text_alarm = 'OK'
                    data = [ getattr(actor, field_translated) , '0 %', str(razon_per_actor)+' %', text_alarm]

            table_data.append(data)

        return table_data



class SupplyBaseRegisterDetailSerializer(serializers.ModelSerializer):

    company = CompanySerializerReview(read_only=True)
    registers = serializers.SerializerMethodField('get_registers_list')
    traceability = serializers.SerializerMethodField('get_traceability')
    traceability_percentage = serializers.SerializerMethodField('get_traceability_percentage') #esto es una tabla
    traceability_alert = serializers.SerializerMethodField('get_alert_table') # Esto es la otra tabla
    
    class Meta:
        model = SupplyBaseRegister
        fields = ['id', 'created_by', 'company',
                'register_year', 'period', 'purchased_volume',
                # 'traceability_reported',
                'traceability_percentage',
                'traceability_alert',
                'registers',
                'traceability'
                    ]

    def get_registers_list(self, obj):
        language_code = self.context["language_code"]
        field_translated = f'name_{language_code}'
        registers = PurchasedPercentage.objects.filter(supplybase_register = obj)
        data_register = registers.values('id', 'percentage', 'actor_type_id').annotate(actor_type=F(f'actor_type__{field_translated}'))
        
        return data_register

    def get_traceability(self, obj):
        language_code = self.context["language_code"]
        field_translated = f'name_{language_code}'

        if obj.period == 0:
            queryset = Traceability.objects.filter(reported_company = obj.company,
                        year=obj.register_year)
        else:
            queryset = Traceability.objects.filter(reported_company = obj.company,
                        year=obj.register_year, period= obj.period)
        return queryset.values('id', 'supplier_name', 'purchased_volume', 'latitude',
                'longitude', 'year','period').annotate(actor_type=F(f'actor_type__{field_translated}'), supplier_company_id=F(f'supplier_company__id'))

    def get_traceability_percentage(self,obj):
        if obj.period == 0:
            traceabilities = Traceability.objects.filter(reported_company = obj.company,
                        year=obj.register_year)
            
        else:
            traceabilities = Traceability.objects.filter(reported_company = obj.company,
                        year=obj.register_year, period= obj.period)
        validated_traceabilities = traceabilities.filter(Q(status_revision='VA') | Q(status_revision='VE'))
        verified_traceabilities = traceabilities.filter(status_revision='VE')

        supplybase_registers = PurchasedPercentage.objects.filter(supplybase_register=obj)
        #
        trazabilidad_reportada = traceabilities.aggregate(Sum('purchased_volume'))
        supplybase_sum = supplybase_registers.aggregate(Sum('percentage'))
        try:
            razon_reportada = round(trazabilidad_reportada['purchased_volume__sum']/supplybase_sum['percentage__sum'], 3)
        except:
            razon_reportada = 0
        #
        trazabilidad_validada = validated_traceabilities.aggregate(Sum('purchased_volume'))
        try:
            razon_validada = round(trazabilidad_validada['purchased_volume__sum']/supplybase_sum['percentage__sum'], 3)
            trazabilidad_validada_percentage = round(trazabilidad_validada['purchased_volume__sum']*100,3)
        except:
            trazabilidad_validada_percentage = 0
            razon_validada = 0
        #
        trazabilidad_verificada = verified_traceabilities.aggregate(Sum('purchased_volume'))
        try:
            razon_verified = trazabilidad_verificada['purchased_volume__sum']/supplybase_sum['percentage__sum']
            trazab_verificada_percentage = round(trazabilidad_verificada['purchased_volume__sum']*100, 3)
        except:
            razon_verified = 0
            trazab_verificada_percentage = 0

        table_data = [
            ['trazabilidad_reportada', str(round(trazabilidad_reportada['purchased_volume__sum']*100, 3))+' %' , str(round(supplybase_sum ['percentage__sum']*100, 3)) +' %', str(razon_reportada*100)+' %'],
            ['trazabilidad_validada', str(trazabilidad_validada_percentage)+' %' , str(supplybase_sum ['percentage__sum']*100)+' %', str(round(razon_validada*100,3))+' %'],
            ['trazabilidad_verificada', str(trazab_verificada_percentage)+' %' , str(supplybase_sum ['percentage__sum']*100)+' %', str(round(razon_verified*100,3))+ ' %'],
            ]

        return table_data

    def get_alert_table(self,obj):
        if obj.period == 0:
            traceabilities = Traceability.objects.filter(reported_company = obj.company,
                        year=obj.register_year)
            
        else:
            traceabilities = Traceability.objects.filter(reported_company = obj.company,
                        year=obj.register_year, period= obj.period)

        actortype_company = obj.company.actor_type
        actortype_dependency = SupplyBaseDependency.objects.get(actor_type = actortype_company).actor_type_dependency.all()

        language_code = self.context["language_code"]
        field_translated = f'name_{language_code}'
        table_data = []
        
        for actor in actortype_dependency:
            actor_trace = traceabilities.filter(actor_type =actor)
            actor_trace_reportada = actor_trace.aggregate(Sum('purchased_volume'))
            try:
                percentage_reported = PurchasedPercentage.objects.get(supplybase_register = obj, actor_type = actor).percentage
            except:
                PurchasedPercentage.objects.create(supplybase_register = obj, actor_type = actor, percentage=0)
                percentage_reported = PurchasedPercentage.objects.get(supplybase_register = obj, actor_type = actor).percentage

            print(f'Para el actortype: {actor} | tiene {actor_trace.count()} | Porcentaje reportado {percentage_reported}')
            if actor_trace.count() >0 and percentage_reported > 0:
                
                razon_per_actor = round((actor_trace_reportada['purchased_volume__sum']/percentage_reported)*100, 3)
                print("razon per actor", razon_per_actor)
                if razon_per_actor == 100:
                    text_alarm = 'OK'
                if razon_per_actor == 0:
                    text_alarm = 'OK'
                elif razon_per_actor < 100:
                    text_alarm= 'Incomplete'    
                elif razon_per_actor >100:
                    text_alarm= 'Overload'
                data = [ getattr(actor, field_translated) , str(round(actor_trace_reportada['purchased_volume__sum']*100,3)) +' %', str(razon_per_actor)+' %', text_alarm,  actor.pk]

            else:
                if PurchasedPercentage.objects.filter(supplybase_register = obj, actor_type = actor).exists():
                    print("entrando aca que tiene registros")
                    percentage_reported = PurchasedPercentage.objects.get(supplybase_register = obj, actor_type = actor).percentage
                    if percentage_reported == 0 and actor_trace.count() >0 :

                        text_alarm='Error'
                        data = [ getattr(actor, field_translated) , str(round(actor_trace_reportada['purchased_volume__sum']*100,3)) +' %', '0 %', 'incomplete', actor.pk]
                        
                    else:
                        razon_per_actor = round((percentage_reported)*100, 3)
                        
                        
                        if razon_per_actor == 0 and actor_trace.count() == 0 :
                            text_alarm='OK'
                            data = [ getattr(actor, field_translated) , '0 %', '0 %', text_alarm , actor.pk]
                        else:
                            text_alarm='Error'
                            data = [ getattr(actor, field_translated) , '0 %', '-'+str(razon_per_actor)+' %', text_alarm , actor.pk]

                else:
                    razon_per_actor = 0
                    text_alarm = 'OK'
                    data = [ getattr(actor, field_translated) , '0 %', str(razon_per_actor)+' %', text_alarm , actor.pk]

            table_data.append(data)

        return table_data


class TraceabilityCompanyResumeSerializer(serializers.ModelSerializer):
    supplier_company = CompanySerializerReview(read_only=True)
    traceability = serializers.SerializerMethodField('get_traceability')
    class Meta:
        model = Traceability
        fields = ['id', 'reported_user', 'supplier_company',
                'traceability'
                    ]
        
    def get_traceability(self, obj):
        if obj.period == 0:
            queryset = Traceability.objects.filter(reported_company = obj.reported_company,
                        year=obj.year)
        else:
            queryset = Traceability.objects.filter(reported_company = obj.reported_company,
                        year=obj.year, period= obj.period)
        return queryset.values()

class PurchasedPercentageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchasedPercentage
        fields = ['id', 'percentage']