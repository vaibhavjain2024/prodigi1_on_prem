from pandas import (
    read_excel,
    isnull,
    isna,
    to_datetime,
    notna,
    Timestamp,
    ExcelWriter
)

import datetime

from PSM.repositories.models.msil_part import MSILPart
from PSM.repositories.models.msil_recipe import MSILRecipe
from PSM.repositories.models.msil_model import MSILModel
from PSM.repositories.models.msil_equipment import MSILEquipment
from PSM.repositories.models.msil_variant import MSILVariant
from PSM.repositories.msil_part_repository import MSILPartRepository
from PSM.repositories.msil_recipe_repository import MSILRecipeRepository
from PSM.repositories.msil_model_repository import MSILModelRepository
from PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from PSM.repositories.msil_variant_repository import MSILVariantRepository
from PSM.repositories.msil_line_repository import MSILLineRepository
from PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from PSM.repositories.msil_quality_reason_repository import MSILQualityReasonRepository
from PSM.repositories.msil_quality_updation_reason_repository import MSILQualityUpdationReasonRepository
from PSM.repositories.msil_shift_repository import MSILShiftRepository
from PSM.repositories.msil_shop_breaks_repository import MSILShopBreaksRepository

class MasterParser():
    def __init__(self,
                 msil_part_repository : MSILPartRepository,
                 msil_recipe_repository : MSILRecipeRepository,
                 msil_model_repository : MSILModelRepository,
                 msil_equipment_repository: MSILEquipmentRepository,
                 msil_variant_repository: MSILVariantRepository,
                 msil_line_repository: MSILLineRepository,
                 msil_quality_updation_reason_repository: MSILQualityUpdationReasonRepository,
                 msil_quality_reason_repository: MSILQualityReasonRepository,
                 msil_downtime_reason_repository:MSILDowntimeReasonRepository,
                 msil_downtime_remark_repository:MSILDowntimeRemarkRepository,
                 msil_shift_repository:MSILShiftRepository,
                 msil_break_repository:MSILShopBreaksRepository):
        #  self.df_part = read_excel(file_obj, sheet_name='2.PART', engine='openpyxl', skiprows=1)
        #  self.df_recipe = read_excel(file_obj, sheet_name='3.RECIPES', engine='openpyxl', skiprows=1)
        #  self.part_headers = {'Part number', '', 'Part name', 'Variant', 'P.E. Code', 'Model', 'Description','Material Type', 'Supplier', 'Storage Type', 'UoM', 'Supplier', 'Expiry Time', 'ExpiryUoM', 'Origin', 'Grade', 'Thickness nominal', 'Thickness upper', 'Thickness lower', 'Thickness unit', 'Thickness tolerance', 'Width nominal', 'Width upper', 'Width lower', 'Width unit', 'Width tolerance', 'Weight', 'Weight unit'}
        #  recipe_headers = {'PE Code', 'Variant'}
         self.msil_part_repository = msil_part_repository
         self.msil_recipe_repository = msil_recipe_repository
         self.msil_model_repository = msil_model_repository
         self.msil_equipment_repository = msil_equipment_repository
         self.msil_variant_repository = msil_variant_repository
         self.msil_line_repository = msil_line_repository
         self.msil_quality_updation_reason_repository = msil_quality_updation_reason_repository
         self.msil_quality_reason_repository = msil_quality_reason_repository
         self.msil_downtime_reason_repository = msil_downtime_reason_repository
         self.msil_downtime_remark_repository = msil_downtime_remark_repository
         self.msil_shift_repository = msil_shift_repository
         self.msil_break_repository = msil_break_repository
    
    def is_all_null(self, row_data):
        return all(isna(each) for each in row_data)
    
    def get_model_id(self, model_name):
        ## TODO Cache from db
        model_dict = {
            "Y1K" : 1,
            "YCA" : 2,
            "YHB" : 3,
            "YHC" : 4,
            "YL1" : 5,
            "YNC" : 6,
            "YXA" : 7
        }
        return model_dict[model_name]
        
    def parse_sheet(self, shop_id):

        for idx, row in self.df_part.iterrows():
            if self.is_all_null(row):
                continue
            part = MSILPart()
            part.material_code = row['Part number']
            part.part_name = row['Part name']
            part.pe_code = row['P.E. Code']
            part.model_id = self.get_model_id(row['Model'])
            try:
                self.msil_part_repository.add(part)
            except Exception as exception:
                print(str(exception))
            

        self.df_recipe = self.df_recipe.where(self.df_recipe.notnull(), None)
        for idx, row in self.df_recipe.iterrows():
            if self.is_all_null(row):
                continue
            try:
                recipe = MSILRecipe()
                recipe.equipment_id = row['Equipment ID']
                recipe.data_number = row['Data Number']
                recipe.input_1 = row['Input 1']
                recipe.input_2 = row['Input 2']
                recipe.output_1 = row['Output 1']
                recipe.output_2 = row['Output 2']
                recipe.shop_id = shop_id
                self.msil_recipe_repository.add(recipe)
            except Exception as exception:
                print(str(exception))

    def master_parser(self,file_obj,shop_id):
        error_remarks=[]

        lines=[]

        models_to_add=[]
        variants_to_add=[]
        parts_to_add=[]
        equipments_to_add=[]
        recipes_to_add=[]

        part_models={}
        part_variants={}

        recipe_inputs_1={}
        recipe_inputs_2={}
        recipe_outputs_1={}
        recipe_outputs_2={}
        recipe_equipments={}

        me = MasterValidationError()
        try:
            try:
                df_variant = read_excel(file_obj, sheet_name='5.VARIANT', engine='openpyxl')
                df_model = read_excel(file_obj, sheet_name='4.MODEL', engine='openpyxl')
                df_equipment = read_excel(file_obj, sheet_name='1.EQUIPMENT', engine='openpyxl')
                df_part = read_excel(file_obj, sheet_name='2.PART', engine='openpyxl')
                df_recipe = read_excel(file_obj, sheet_name='3.RECIPES', engine='openpyxl')
                df_downtime = read_excel(file_obj, sheet_name='8.DOWNTIME_REASON',engine='openpyxl')
                # df_reason = read_excel(file_obj, sheet_name='Model', engine='openpyxl')
                # df_shift = read_excel(file_obj, sheet_name='Shift', engine='openpyxl')
                # df_break = read_excel(file_obj, sheet_name='Break', engine='openpyxl')
            except:
                me.add_error('One of the Master Sheets is missing')
                raise me
            
            variant_headers = {'#','Variant','Common Name'}
            model_headers = {'#','Model','Description'}
            equipment_headers = {'#','Line','Equipment Id','Equipment Name','Equipment group','Efficiency'}
            part_headers = {'#','Part number','Part name','Variant','P.E. Code','Model','Description','Material Type',
                            'Supplier','Origin','Grade','Thickness nominal','Thickness upper',
                            'Thickness lower','Thickness unit','Thickness tolerance','Width nominal','Width upper','Width lower',
                            'Width unit','Width tolerance','Weight','Weight unit'}
            recipe_headers = {'Equipment ID','Data Number','Data Number Description','Variant','Input 1','Input 1 description','Input 1 Qty',
                              'Input 2','Input 2 description','Input 2 Qty','Output 1','Output 1 description','Output 1 Qty','Output 2','Output 2 description',
                              'Output 2 Qty','Input Storage unit Group','Output Storage unit Group'}
            downtime_headers = {'Reason','Remark','Type','Tag'}
            # reason_headers = {}

            variant_missing = variant_headers - set(df_variant.head())
            model_missing = model_headers - set(df_model.head())
            equipment_missing = equipment_headers - set(df_equipment.head())
            part_missing = part_headers - set(df_part.head())
            recipe_missing = recipe_headers - set(df_recipe.head())
            downtime_headers = downtime_headers - set(df_downtime.head())

            if variant_missing:
                me.add_error(f"Column(s) {variant_missing} in Variant Sheet")
                raise me
            if model_missing:
                me.add_error(f"Column(s) {model_missing} in Model Sheet")
                raise me
            if equipment_missing:
                me.add_error(f"Column(s) {equipment_missing} in Equipment Sheet")
                raise me
            if part_missing:
                me.add_error(f"Column(s) {part_missing} in Part Sheet")
                raise me
            if recipe_missing:
                me.add_error(f"Column(s) {recipe_missing} in Recipe Sheet")
                raise me
            
            model_cache = self.msil_model_repository.model_ids(shop_id=shop_id)
            model_ids = list(set(model_cache.values()))
            equipment_cache = self.msil_equipment_repository.equipment_ids(shop_id=shop_id)
            equipment_ids = list(set(equipment_cache.values()))
            variant_cache = self.msil_variant_repository.variant_ids()
            variant_ids = list(set(variant_cache.values()))
            material_codes = self.msil_part_repository.material_codes()
            recipe_combinations = self.msil_recipe_repository.recipe_combinations(shop_id=shop_id)
                      
            for index, row in df_model.iterrows():
                if self.is_all_null(row):
                    continue
                if notna(row['#']):
                    try:
                        row['#']=int(row['#'])
                    except:
                        error_remarks.append(f"Incorrect # at row {index+2} in Model Sheet")
                else:
                    error_remarks.append(f"Missing # at row {index+2} in Model Sheet")
                if isna(row['Model']):
                    error_remarks.append(f"Missing Model at row {index+2} in Model Sheet")
            
            duplicate_model_ids = df_model[df_model.duplicated(subset='#')].index.tolist()
            if duplicate_model_ids:
                duplicate_model_ids = [i+2 for i in duplicate_model_ids]
                error_remarks.append(f"Duplicate values for # at row(s) {','.join(map(str,duplicate_model_ids))} in Model Sheet")
            
            duplicate_model_names = df_model[df_model.duplicated(subset='Model')].index.tolist()
            if duplicate_model_names:
                duplicate_model_names = [i+2 for i in duplicate_model_names]
                error_remarks.append(f"Duplicate values for Model at row(s) {','.join(map(str,duplicate_model_names))} in Model Sheet")
            
            if not error_remarks:

                for index,row in df_model.iterrows():
                    if self.is_all_null(row):
                        continue
                    model_object = {
                        'id': row['#'],
                        'model_name': row['Model'],
                        'model_description': None if isna(row['Description']) else row['Description'],
                        'shop_id':shop_id
                    }
                    if row['#'] not in model_ids:
                        models_to_add.append(model_object)
                    # else:
                    #     self.msil_model_repository.update(id=row['#'],model=model_object)
                # models_to_add=self.msil_model_repository.bulk_insert_mappings(models_to_add)
                model_cache = self.msil_model_repository.model_ids(shop_id=shop_id)
                model_names = list(set(model_cache.keys()))

            for index, row in df_variant.iterrows():
                if self.is_all_null(row):
                    continue
                if notna(row['#']):
                    try:
                        row['#']=int(row['#'])
                    except:
                        error_remarks.append(f"Incorrect # at row {index+2} in Variant Sheet")
                else:
                    error_remarks.append(f"Missing # at row {index+2} in Variant Sheet")
                if isna(row['Variant']):
                    error_remarks.append(f"Missing Variant at row {index+2} in Variant Sheet")
            
            duplicate_variant_ids = df_variant[df_variant.duplicated(subset='#')].index.tolist()
            if duplicate_variant_ids:
                duplicate_variant_ids = [i+2 for i in duplicate_variant_ids]
                error_remarks.append(f"Duplicate values for # at row(s) {','.join(map(str,duplicate_variant_ids))} in Variant Sheet")
            
            duplicate_variant_names = df_variant[df_variant.duplicated(subset='Variant')].index.tolist()
            if duplicate_variant_names:
                duplicate_variant_names = [i+2 for i in duplicate_variant_ids]
                error_remarks.append(f"Duplicate values for Variant at row(s) {','.join(map(str,duplicate_variant_names))} in Variant Sheet")
            
            if not error_remarks:
                for index,row in df_variant.iterrows():
                    if self.is_all_null(row):
                        continue
                    variant_object = {
                        'id': row['#'],
                        'variant_name': row['Variant'],
                        'common_name': None if isna(row['Common Name']) else row['Common Name']
                    }
                    if row['#'] not in variant_ids:
                        variants_to_add.append(variant_object)
                    # else:
                    #     self.msil_variant_repository.update(id=row['#'],model=variant_object)
                # variants_to_add=self.msil_variant_repository.bulk_insert_mappings(variants_to_add)
                variant_cache = self.msil_variant_repository.variant_ids()
                variant_names = list(set(variant_cache.keys()))
            
            for index, row in df_equipment.iterrows():
                if self.is_all_null(row):
                    continue
                if isna(row['Equipment Id']):
                    error_remarks.append(f"Missing Equipment Id at row {index+2} in Equipment Sheet")
                if isna(row['Line']):
                    error_remarks.append(f"Missing Line at row {index+2} in Equipment Sheet")
                else:
                    lines.append(row['Line'])
                if isna(row['Equipment Name']):
                    error_remarks.append(f"Missing Equipment Name at row {index+2} in Equipment Sheet")
                if isna(row['Equipment group']):
                    error_remarks.append(f"Missing Equipment group at row {index+2} in Equipment Sheet")
                if notna(row['Efficiency']):
                    try:
                        row['Efficiency']=int(row['Efficiency'])
                        if row['Efficiency']<0:
                            error_remarks.append(f"Invalid Efficiency at row {index+2} in Equipment Sheet")
                    except:
                        error_remarks.append(f"Invalid Efficiency at row {index+2} in Equipment Sheet")

            
            duplicate_equipment_ids = df_equipment[df_equipment.duplicated(subset='Equipment Id')].index.tolist()
            if duplicate_equipment_ids:
                duplicate_equipment_ids = [i+2 for i in duplicate_equipment_ids]
                error_remarks.append(f"Duplicate values for Equipment Id at row(s) {','.join(map(str,duplicate_equipment_ids))} in Equipment Sheet")
            
            duplicate_equipment_names = df_equipment[df_equipment.duplicated(subset='Equipment Name')].index.tolist()
            if duplicate_equipment_names:
                duplicate_equipment_names = [i+2 for i in duplicate_equipment_names]
                error_remarks.append(f"Duplicate values for Equipment name at row(s) {','.join(map(str,duplicate_equipment_names))} in Equipment Sheet")
            
            if not error_remarks:

                # line_cache = self.msil_line_repository.check_and_add_lines(line_list=set(lines),shop_id=shop_id)
                line_cache = self.msil_line_repository.line_ids(shop_id=shop_id)

                for index,row in df_equipment.iterrows():
                    if self.is_all_null(row):
                        continue
                    equipment_object = {
                        'id': row['Equipment Id'],
                        'name': row['Equipment Name'],
                        'equipment_group': row['Equipment group'],
                        'efficiency': 0 if isna(row['Efficiency']) else row['Efficiency'],
                        'shop_id':shop_id
                    }
                    if row['Equipment Id'] not in equipment_ids:
                        equipments_to_add.append(equipment_object)
                #     else:
                #         self.msil_equipment_repository.update(id=row['Equipment Id'],model=equipment_object)
                # equipments_to_add=self.msil_equipment_repository.bulk_insert_mappings(equipments_to_add)
                equipment_cache = self.msil_equipment_repository.equipment_ids(shop_id=shop_id)
                equipment_ids = list(set(equipment_cache.values()))

            if not error_remarks:
                for index, row in df_part.iterrows():
                    if self.is_all_null(row):
                        continue
                    if isna(row['Part number']):
                        error_remarks.append(f"Missing Part number at row {index+2} in Part Sheet")
                    if isna(row['Part name']):
                        error_remarks.append(f"Missing Part name at row {index+2} in Part Sheet")
                    if notna(row['Variant']):
                        if part_variants.get(row['Variant'],None)==None:
                            part_variants[row['Variant']]=[index+2]
                        else:
                            part_variants[row['Variant']].append(index+2)
                    if isna(row['P.E. Code']):
                        error_remarks.append(f"Missing P.E. Code at row {index+2} in Part Sheet")
                    if isna(row['Model']):
                        error_remarks.append(f"Missing Model at Row {index+2} in Part Sheet")
                    else:
                        if part_models.get(row['Model'],None) == None:
                            part_models[row['Model']]=[index+2]
                        else:
                            part_models[row['Model']].append(index+2)
                    
                    if notna(row['Thickness nominal']):
                        try:
                            row['Thickness nominal']=float(row['Thickness nominal'])
                            if row['Thickness nominal']<0:
                                error_remarks.append(f"Invalid Thickness nominal at row {index+2} in Part Sheet")
                        except:
                            error_remarks.append(f"Invalid Thickness nominal at row {index+2} in Part Sheet")
                    if notna(row['Thickness upper']):
                        try:
                            row['Thickness upper']=float(row['Thickness upper'])
                            if row['Thickness upper']<0:
                                error_remarks.append(f"Invalid Thickness upper at row {index+2} in Part Sheet")
                        except:
                            error_remarks.append(f"Invalid Thickness upper at row {index+2} in Part Sheet")
                    if notna(row['Thickness lower']):
                        try:
                            row['Thickness lower']=float(row['Thickness lower'])
                            if row['Thickness lower']<0:
                                error_remarks.append(f"Invalid Thickness lower at row {index+2} in Part Sheet")
                        except:
                            error_remarks.append(f"Invalid Thickness lower at row {index+2} in Part Sheet")
                    if notna(row['Thickness tolerance']):
                        if str(row['Thickness tolerance']).strip().upper() not in ('ABSOLUTE','RELATIVE'):
                            error_remarks.append(f"Invalid Thickness tolerance at row {index+2} in Part Sheet")
                    
                    if notna(row['Width nominal']):
                        try:
                            row['Width nominal']=float(row['Width nominal'])
                            if row['Width nominal']<0:
                                error_remarks.append(f"Invalid Width nominal at row {index+2} in Part Sheet")
                        except:
                            error_remarks.append(f"Invalid Width nominal at row {index+2} in Part Sheet")
                    if notna(row['Width upper']):
                        try:
                            row['Width upper']=float(row['Width upper'])
                            if row['Width upper']<0:
                                error_remarks.append(f"Invalid Width upper at row {index+2} in Part Sheet")
                        except:
                            error_remarks.append(f"Invalid Width upper at row {index+2} in Part Sheet")
                    if notna(row['Width lower']):
                        try:
                            row['Width lower']=float(row['Width lower'])
                            if row['Width lower']<0:
                                error_remarks.append(f"Invalid Width lower at row {index+2} in Part Sheet")
                        except:
                            error_remarks.append(f"Invalid Width lower at row {index+2} in Part Sheet")
                    if notna(row['Width tolerance']):
                        if str(row['Width tolerance']).strip().upper() not in ('ABSOLUTE','RELATIVE'):
                            error_remarks.append(f"Invalid Width tolerance at row {index+2} in Part Sheet")
                    
                    if notna(row['Weight']):
                        try:
                            row['Weight']=float(row['Weight'])
                            if row['Weight']<0:
                                error_remarks.append(f"Invalid Weight at row {index+2} in Part Sheet")
                        except:
                            error_remarks.append(f"Invalid Weight at row {index+2} in Part Sheet")
                        
                duplicate_material_codes = df_part[df_part.duplicated(subset='Part number')].index.tolist()
                if duplicate_material_codes:
                    duplicate_material_codes = [i+2 for i in duplicate_material_codes]
                    error_remarks.append(f"Duplicate values for Part number at row(s) {','.join(map(str,duplicate_material_codes))} in Part Sheet")
            
            if not error_remarks:

                models = list(set(part_models.keys()))
                model_details = self.msil_model_repository.check_for_models(shop_id=shop_id,model_names=models)
                model_list = list(set(model_details.keys()))
                if len(model_details)!=len(part_models):
                    for item in models:
                        if item not in model_list:
                            for i in part_models[item]:
                                error_remarks.append(f"Model not present in system for Row {i} in Part Sheet")
                
                variants = list(set(part_variants.keys()))
                variant_details = self.msil_variant_repository.check_for_variants(variant_names=variants)
                variant_list = list(set(variant_details.keys()))
                if len(variant_details)!=len(part_variants):
                    for item in variants:
                        if item not in variant_list:
                            for i in part_variants[item]:
                                error_remarks.append(f"Variant not present in system for Row {i} in Part Sheet")
            
            if not error_remarks:

                for index,row in df_part.iterrows():
                    if self.is_all_null(row):
                        continue
                    part_object = {
                        'material_code': row['Part number'],
                        'part_name': row['Part name'],
                        'variant_id': None if isna(row['Variant']) else variant_cache[row['Variant']],
                        'pe_code': row['P.E. Code'],
                        'model_id': model_cache[row['Model']],
                        'description': None if isna(row['Description']) else row['Description'],
                        'material_type': None if isna(row['Material Type']) else row['Material Type'],
                        'supplier': None if isna(row['Supplier']) else row['Supplier'],
                        'storage_type': None if isna(row['Storage Type']) else row['Storage Type'],
                        'unit': None if isna(row['UoM']) else row['UoM'],
                        'thickness_nominal': 0.0 if isna(row['Thickness nominal']) else row['Thickness nominal'],
                        'thickness_upper':  0.0 if isna(row['Thickness upper']) else row['Thickness upper'],
                        'thickness_lower':  0.0 if isna(row['Thickness lower']) else row['Thickness lower'],
                        'thickness_tolerance_unit': None if isna(row['Thickness tolerance']) else row['Thickness tolerance'],
                        'thickness_unit': None if isna(row['Thickness unit']) else row['Thickness unit'],
                        'width_nominal':  0.0 if isna(row['Width nominal']) else row['Width nominal'],
                        'width_upper': 0.0 if isna(row['Width upper']) else row['Width upper'],
                        'width_lower': 0.0 if isna(row['Width lower']) else row['Width lower'],
                        'width_tolerance_unit': None if isna(row['Width tolerance']) else row['Width tolerance'],
                        'width_unit': None if isna(row['Width unit']) else row['Width unit'],
                        'weight': 0.0 if isna(row['Weight']) else row['Wight'],
                        'weight_unit': None if isna(row['Weight unit']) else row['Weight unit']
                    }
                    if row['Part number'] not in material_codes:
                        parts_to_add.append(part_object)
                #     else:
                #         self.msil_part_repository.update_part(material_code=row['Part number'],model=part_object)
                # parts_to_add=self.msil_part_repository.bulk_insert_mappings(parts_to_add)

            if not error_remarks:
                for index, row in df_recipe.iterrows():
                    if self.is_all_null(row):
                        continue
                    
                    if isna(row['Equipment ID']):
                        error_remarks.append(f"Missing Equipment ID at row {index+2} in Recipe Sheet")
                    else:
                        if recipe_equipments.get(row['Equipment ID'],None) == None:
                            recipe_equipments[row['Equipment ID']]=[index+2]
                        else:
                            recipe_equipments[row['Equipment ID']].append(index+2)

                    if notna(row['Data Number']):
                        try:
                            row['Data Number'] = str(row['Data Number'])
                        except:
                            error_remarks.append(f"Incorrect Data Number at row {index+2} in Recipe Sheet")
                    else:
                        error_remarks.append(f"Missing Data Number at row {index+2} in Recipe Sheet")
                    
                    if isna(row['Input 1']):
                        error_remarks.append(f"Missing Input 1 at Row {index+2} in Recipe Sheet")
                    else:
                        if recipe_inputs_1.get(row['Input 1'],None)==None:
                            recipe_inputs_1[row['Input 1']]=[index+2]
                        else:
                            recipe_inputs_1[row['Input 1']].append(index+2)
                    
                    if notna(row['Input 1 Qty']):
                        try:
                            row['Input 1 Qty']=int(row['Input 1 Qty'])
                            if row['Input 1 Qty']<0:
                                error_remarks.append(f"Incorrect Input 1 Qty at row {index+2} in Recipe Sheet")
                        except:
                            error_remarks.append(f"Incorrect Input 1 Qty at row {index+2} in Recipe Sheet")
                    
                    if notna(row['Input 2']):
                        if recipe_inputs_2.get(row['Input 2'],None)==None:
                            recipe_inputs_2[row['Input 2']]=[index+2]
                        else:
                            recipe_inputs_2[row['Input 2']].append(index+2)
                    
                    if notna(row['Input 2 Qty']):
                        try:
                            row['Input 2 Qty']=int(row['Input 2 Qty'])
                            if row['Input 2 Qty']<0:
                                error_remarks.append(f"Incorrect Input 2 Qty at row {index+2} in Recipe Sheet")
                        except:
                            error_remarks.append(f"Incorrect Input 2 Qty at row {index+2} in Recipe Sheet")
                    
                    if isna(row['Output 1']):
                        error_remarks.append(f"Missing Output 1 at Row {index+2} in Recipe Sheet")
                    else:
                        if recipe_outputs_1.get(row['Output 1'],None)==None:
                            recipe_outputs_1[row['Output 1']]=[index+2]
                        else:
                            recipe_outputs_1[row['Output 1']].append(index+2)
                    
                    if notna(row['Output 1 Qty']):
                        try:
                            row['Output 1 Qty']=int(row['Output 1 Qty'])
                            if row['Output 1 Qty']<0:
                                error_remarks.append(f"Incorrect Output 1 Qty at row {index+2} in Recipe Sheet")
                        except:
                            error_remarks.append(f"Incorrect Output 1 Qty at row {index+2} in Recipe Sheet")
                    
                    if notna(row['Output 2']):
                        if recipe_outputs_2.get(row['Output 2'],None)==None:
                            recipe_outputs_2[row['Output 2']]=[index+2]
                        else:
                            recipe_outputs_2[row['Output 2']].append(index+2)
                    
                    if notna(row['Output 2 Qty']):
                        try:
                            row['Output 2 Qty']=int(row['Output 2 Qty'])
                            if row['Output 2 Qty']<0:
                                error_remarks.append(f"Incorrect Output 2 Qty at row {index+2} in Recipe Sheet")
                        except:
                            error_remarks.append(f"Incorrect Output 2 Qty at row {index+2} in Recipe Sheet")
                    
                    if notna(row['Variant']):
                        if str(row['Variant']).strip().upper() not in ('TRUE','FALSE'):
                            error_remarks.append(f"Incorrect Variant at row {index+2} in Recipe Sheet")
                    
                duplicate_recipe_combinations = df_recipe[df_recipe.duplicated(subset=['Equipment ID','Data Number','Output 1','Output 2'])].index.tolist()
                if duplicate_recipe_combinations:
                    duplicate_recipe_combinations = [i+2 for i in duplicate_recipe_combinations]
                    error_remarks.append(f"Duplicate values for (Equipment ID, Data Number, Output 1, Output 2) at row(s) {','.join(map(str,duplicate_material_codes))} in Recipe Sheet")
            
            if not error_remarks:

                unknown_equipments = set(recipe_equipments.keys()) - set(equipment_ids)
                if unknown_equipments:
                    for item in unknown_equipments:
                        for i in recipe_equipments[item]:
                            error_remarks.append(f"Equipment ID not present in system for Row {i} in Recipe Sheet")
                
                numbers_i_1 = list(set(recipe_inputs_1.keys()))
                number_i_1_details = self.msil_part_repository.check_for_numbers(part_numbers=numbers_i_1)
                number_list_1 = list(item[0] for item in number_i_1_details)
                if len(number_i_1_details)!=len(recipe_inputs_1):
                    for item in numbers_i_1:
                        if item not in number_list_1:
                            for i in recipe_inputs_1[item]:
                                error_remarks.append(f"Input 1 not present in system for Row {i} in Recipe Sheet")
                
                numbers_i_2 = list(set(recipe_inputs_2.keys()))
                number_i_2_details = self.msil_part_repository.check_for_numbers(part_numbers=numbers_i_2)
                number_list_2 = list(item[0] for item in number_i_2_details)
                if len(number_i_2_details)!=len(recipe_inputs_2):
                    for item in numbers_i_2:
                        if item not in number_list_2:
                            for i in recipe_inputs_2[item]:
                                error_remarks.append(f"Input 2 not present in system for Row {i} in Recipe Sheet")
                
                numbers_o_1 = list(set(recipe_outputs_1.keys()))
                number_o_1_details = self.msil_part_repository.check_for_numbers(part_numbers=numbers_o_1)
                number_list_1 = list(item[0] for item in number_o_1_details)
                if len(number_o_1_details)!=len(recipe_outputs_1):
                    for item in numbers_o_1:
                        if item not in number_list_1:
                            for i in recipe_outputs_1[item]:
                                error_remarks.append(f"Output 1 not present in system for Row {i} in Recipe Sheet")
                
                numbers_o_2 = list(set(recipe_outputs_2.keys()))
                number_o_2_details = self.msil_part_repository.check_for_numbers(part_numbers=numbers_o_2)
                number_list_2 = list(item[0] for item in number_o_2_details)
                if len(number_o_2_details)!=len(recipe_outputs_2):
                    for item in numbers_o_2:
                        if item not in number_list_2:
                            for i in recipe_outputs_2[item]:
                                error_remarks.append(f"Output 2 not present in system for Row {i} in Recipe Sheet")
            
            if not error_remarks:
                for index,row in df_recipe.iterrows():
                    if self.is_all_null(row):
                        continue

                    eqp = row['Equipment ID']
                    num = row['Data Number']
                    o_1 = row['Output 1']
                    o_2 = None if isna(row['Output 2']) else row['Output 2']
                    recipe_object = {
                        'equipment_id': eqp,
                        'data_number': num,
                        'data_number_description': None if isna(row['Data Number Description']) else row['Data Number Description'],
                        'input_1': row['Input 1'],
                        'input_1_qty': 0 if isna(row['Input 1 Qty']) else row['Input 1 Qty'],
                        'output_1': o_1,
                        'output_1_qty': 0 if isna(row['Output 1 Qty']) else row['Output 1 Qty'],
                        'input_2': None if isna(row['Input 2']) else row['Input 2'],
                        'input_2_qty': 0 if isna(row['Input 2 Qty']) else row['Input 2 Qty'],
                        'output_2': o_2,
                        'output_2_qty': 0 if isna(row['Output 2 Qty']) else row['Output 2 Qty'],
                        'variant': None if isna(row['Variant']) else row['Variant'],
                        'input_storage_unit_group': None if isna(row['Input Storage unit Group']) else row['Input Storage unit Group'],
                        'output_storage_unit_group': None if isna(row['Output Storage unit Group']) else row['Output Storage unit Group'],
                        'shop_id': shop_id
                        
                    }
                    if [eqp,num,o_1,o_2] not in recipe_combinations:
                        recipes_to_add.append(recipe_object)
                    # else:
                #         self.msil_recipe_repository.update_recipe(shop_id=shop_id,
                #                                                   eqp_id=eqp,
                #                                                   out_1=o_1,
                #                                                   out_2=o_2,
                #                                                   number=num,
                #                                                   model=recipe_object)
                # recipes_to_add=self.msil_recipe_repository.bulk_insert_mappings(recipes_to_add)

                
            

            
            
            
            if not error_remarks:
                return 'Updated Records'
            else:
                for r in error_remarks:
                    me.add_error(r)
                raise me

            
        except MasterValidationError:
            errors = ('; '.join(me.get_error_list()))
            # self.msil_status_repository.new_status(date_cur, PlanFileStatusEnum.FAILED,errors, shop_id)
            # self.plan_alert(errors)
            return errors
        # except Exception as e:
        #     # self.msil_status_repository.new_status(date_cur, PlanFileStatusEnum.FAILED,str(e), shop_id)
        #     # self.plan_alert(str(e))
        #     return str(e)

    def upload_parser(self,file_obj,shop_id):
        lines=[]
        existing_equipments=[]

        models_to_add=[]
        variants_to_add=[]
        parts_to_add=[]
        equipments_to_add=[]
        recipes_to_add=[]

        # part_models={}
        # part_variants={}

        # recipe_inputs_1={}
        # recipe_inputs_2={}
        # recipe_outputs_1={}
        # recipe_outputs_2={}
        # recipe_equipments={}
        df_variant = read_excel(file_obj, sheet_name='5.VARIANT', engine='openpyxl')
        df_model = read_excel(file_obj, sheet_name='4.MODEL', engine='openpyxl')
        df_equipment = read_excel(file_obj, sheet_name='1.EQUIPMENT', engine='openpyxl')
        df_part = read_excel(file_obj, sheet_name='2.PART', engine='openpyxl')
        df_recipe = read_excel(file_obj, sheet_name='3.RECIPES', engine='openpyxl')
        df_downtime = read_excel(file_obj, sheet_name='8.DOWNTIME_REASON',engine='openpyxl')
        df_quality = read_excel(file_obj, sheet_name='9.QUALITY_REASON',engine='openpyxl')
        df_shift = read_excel(file_obj, sheet_name='6.SHIFT',engine='openpyxl')
        df_breaks = read_excel(file_obj,sheet_name='7.BREAKS',engine='openpyxl')

        variant_headers = {'#','Variant','Common Name'}
        model_headers = {'#','Model','Description'}
        equipment_headers = {'#','Line','Equipment Id','Equipment Name','Equipment group','Efficiency'}
        part_headers = {'#','Part number','Part name','Variant','P.E. Code','Model','Description','Material Type',
                        'Supplier','Origin','Grade','Thickness nominal','Thickness upper',
                        'Thickness lower','Thickness unit','Thickness tolerance','Width nominal','Width upper','Width lower',
                        'Width unit','Width tolerance','Weight','Weight unit'}
        recipe_headers = {'Equipment ID','Data Number','Data Number Description','Variant','Input 1','Input 1 description','Input 1 Qty',
                            'Input 2','Input 2 description','Input 2 Qty','Output 1','Output 1 description','Output 1 Qty','Output 2','Output 2 description',
                            'Output 2 Qty','Input Storage unit Group','Output Storage unit Group'}
        downtime_headers = {'Reason','Remark','Type','Tag'}
        
        model_cache = self.msil_model_repository.model_ids(shop_id=shop_id)
        print("initial model cache",model_cache)
        model_ids = list(set(model_cache.values()))
        model_names = list(set(model_cache.keys()))
        equipment_cache = self.msil_equipment_repository.equipment_ids(shop_id=shop_id)
        equipment_ids = list(set(equipment_cache.values()))
        variant_cache = self.msil_variant_repository.variant_ids()
        variant_ids = list(set(variant_cache.values()))
        variant_names = list(set(variant_cache.keys()))
        material_codes = self.msil_part_repository.material_codes()
        recipe_combinations = self.msil_recipe_repository.recipe_combinations(shop_id=shop_id)
                    
        for index,row in df_model.iterrows():
            if self.is_all_null(row):
                continue
            model_object = {
                'model_name': row['Model'],
                'model_description': None if isna(row['Description']) else row['Description'],
                'shop_id':shop_id
            }
            if row['Model'] not in model_names:
                models_to_add.append(model_object)
            else:
                self.msil_model_repository.update(id=model_cache[row['Model']],model=model_object)
        models_to_add=self.msil_model_repository.bulk_insert_mappings(models_to_add)
        model_cache = self.msil_model_repository.model_ids(shop_id=shop_id)
        print("updated model cache",model_cache)
        model_names = list(set(model_cache.keys()))

        for index,row in df_variant.iterrows():
            if self.is_all_null(row):
                continue
            variant_object = {
                'variant_name': row['Variant'],
                'common_name': None if isna(row['Common Name']) else row['Common Name']
            }
            if row['Variant'] not in variant_names:
                variants_to_add.append(variant_object)
            else:
                self.msil_variant_repository.update(id=variant_cache[row['Variant']],model=variant_object)
        variants_to_add=self.msil_variant_repository.bulk_insert_mappings(variants_to_add)
        variant_cache = self.msil_variant_repository.variant_ids()
        print("updated variant cache",variant_cache)
        variant_names = list(set(variant_cache.keys()))

        for index, row in df_equipment.iterrows():
            if self.is_all_null(row):
                continue
            lines.append(row['Line'])

        line_cache = self.msil_line_repository.check_and_add_lines(line_list=set(lines),shop_id=shop_id)
        line_cache = self.msil_line_repository.line_ids(shop_id=shop_id)

        for index,row in df_equipment.iterrows():
            if self.is_all_null(row):
                continue
            equipment_object = {
                'id': str(row['Equipment Id']),
                'name': row['Equipment Name'],
                'equipment_group': row['Equipment group'],
                'efficiency': 0 if isna(row['Efficiency']) else row['Efficiency'],
                'line_id': line_cache[str(row['Line'])],
                'shop_id':shop_id,
                'is_deleted':False
            }
            if str(row['Equipment Id']) not in equipment_ids:
                equipments_to_add.append(equipment_object)
            else:
                self.msil_equipment_repository.update(id=str(row['Equipment Id']),model=equipment_object)
                existing_equipments.append(str(row['Equipment Id']))

        equipments_to_delete = list(set(equipment_ids) - set(existing_equipments))
        self.msil_equipment_repository.soft_delete_equipments(eqp_ids=equipments_to_delete,shop_id=shop_id)
        equipments_to_add=self.msil_equipment_repository.bulk_insert_mappings(equipments_to_add)
        equipment_cache = self.msil_equipment_repository.equipment_ids(shop_id=shop_id)
        equipment_ids = list(set(equipment_cache.values()))

        for index,row in df_part.iterrows():
            if self.is_all_null(row):
                continue
            part_object = {
                'material_code': row['Part number'],
                'part_name': row['Part name'],
                'variant_id': None if isna(row['Variant']) else variant_cache[row['Variant']],
                'pe_code': row['P.E. Code'],
                'model_id': model_cache[row['Model']],
                'description': None if isna(row['Description']) else row['Description'],
                'material_type': None if isna(row['Material Type']) else row['Material Type'],
                'supplier': None if isna(row['Supplier']) else row['Supplier'],
                'storage_type': None if isna(row['Storage Type']) else row['Storage Type'],
                'unit': None if isna(row['UoM']) else row['UoM'],
                'thickness_nominal': 0.0 if isna(row['Thickness nominal']) else row['Thickness nominal'],
                'thickness_upper':  0.0 if isna(row['Thickness upper']) else row['Thickness upper'],
                'thickness_lower':  0.0 if isna(row['Thickness lower']) else row['Thickness lower'],
                'thickness_tolerance_unit': None if isna(row['Thickness tolerance']) else row['Thickness tolerance'],
                'thickness_unit': None if isna(row['Thickness unit']) else row['Thickness unit'],
                'width_nominal':  0.0 if isna(row['Width nominal']) else row['Width nominal'],
                'width_upper': 0.0 if isna(row['Width upper']) else row['Width upper'],
                'width_lower': 0.0 if isna(row['Width lower']) else row['Width lower'],
                'width_tolerance_unit': None if isna(row['Width tolerance']) else row['Width tolerance'],
                'width_unit': None if isna(row['Width unit']) else row['Width unit'],
                'weight': 0.0 if isna(row['Weight']) else row['Wight'],
                'weight_unit': None if isna(row['Weight unit']) else row['Weight unit'],
                'shop_id': shop_id
            }
            if row['Part number'] not in material_codes:
                parts_to_add.append(part_object)
            else:
                print("----------------- update part number",row['Part number'])
                print("----------------- update part name",row['Part name'],model_cache[row['Model']])
                self.msil_part_repository.update_part(material_code=row['Part number'],model=part_object,shop_id=shop_id)
        print("new parts_to_add",parts_to_add)
        parts_to_add=self.msil_part_repository.bulk_insert_mappings(parts_to_add)

        for index,row in df_recipe.iterrows():
            if self.is_all_null(row):
                continue

            eqp = str(row['Equipment ID'])
            num = row['Data Number']
            o_1 = row['Output 1']
            o_2 = None if isna(row['Output 2']) else row['Output 2']
            recipe_object = {
                'equipment_id': eqp,
                'data_number': num,
                'data_number_description': None if isna(row['Data Number Description']) else row['Data Number Description'],
                'input_1': row['Input 1'],
                'input_1_qty': 0 if isna(row['Input 1 Qty']) else row['Input 1 Qty'],
                'output_1': o_1,
                'output_1_qty': 0 if isna(row['Output 1 Qty']) else row['Output 1 Qty'],
                'input_2': None if isna(row['Input 2']) else row['Input 2'],
                'input_2_qty': 0 if isna(row['Input 2 Qty']) else row['Input 2 Qty'],
                'output_2': o_2,
                'output_2_qty': 0 if isna(row['Output 2 Qty']) else row['Output 2 Qty'],
                'input_storage_unit_group': None if isna(row['Input Storage unit Group']) else row['Input Storage unit Group'],
                'output_storage_unit_group': None if isna(row['Output Storage unit Group']) else row['Output Storage unit Group'],
                'shop_id': shop_id

            }
            if [eqp,num,o_1,o_2] not in recipe_combinations:
                recipes_to_add.append(recipe_object)
            else:
                self.msil_recipe_repository.update_recipe(shop_id=shop_id,
                                                            eqp_id=eqp,
                                                            out_1=o_1,
                                                            out_2=o_2,
                                                            number=num,
                                                            model=recipe_object)
        recipes_to_add=self.msil_recipe_repository.bulk_insert_mappings(recipes_to_add)

        reason_combinations = []

        for index, row in df_downtime.iterrows():
            reason_combinations.append((row['Reason'],str(row['Type']).strip().lower(),row['Tag']))

        reason_combinations = list(set(reason_combinations))

        added_reasons = reason_combinations
        # return added_reasons
        reason_combinations = self.msil_downtime_reason_repository.reason_type_update(shop_id=shop_id,combination_list=reason_combinations)

        reason_combinations = self.msil_downtime_reason_repository.id_by_combination(shop_id=shop_id)
        unused_reasons = [reason_combinations[key] for key in reason_combinations.keys() if key not in added_reasons]
        # return unused_reasons
        unused_reasons = self.msil_downtime_reason_repository.delete_reason_tags(shop_id=shop_id,reason_ids=unused_reasons)

        for index,row in df_downtime.iterrows():
            if self.is_all_null(row):
                continue
            type_format = str(row['Type']).strip().lower()
            self.msil_downtime_remark_repository.check_and_add_remark(
                reason=reason_combinations[(row['Reason'],type_format,row['Tag'])],
                remark=row['Remark']
            )
        self.msil_quality_reason_repository.delete_reasons(shop_id=shop_id)
        self.msil_quality_updation_reason_repository.delete_reasons(shop_id=shop_id)
        for index,row in df_quality.iterrows():
            if self.is_all_null(row):
                continue
            reason_type_format = str(row['Reason Type']).strip().upper()
            if reason_type_format == 'PUNCHING':
                self.msil_quality_reason_repository.check_and_add_reason(reason=row['Reason'],
                                                                         type=row['Type'],
                                                                         shop_id=shop_id)
            elif reason_type_format == 'UPDATION':
                self.msil_quality_updation_reason_repository.check_and_add_reason(reason=row['Reason'],
                                                                         type=row['Type'],
                                                                         shop_id=shop_id)
        shifts = []
        for index,row in df_shift.iterrows():
            if self.is_all_null(row):
                continue
            shifts.append({
                'shop_id' : shop_id,
                'shift_name' : row['Shift'],
                'shift_start_timing' : row['Start'],
                'shift_end_timing' : row['End']
            })
        self.msil_shift_repository.update_shifts(shop_id=shop_id,shifts=shifts)

        breaks = []
        for index,row in df_breaks.iterrows():
            if self.is_all_null(row):
                continue
            breaks.append({
                'shop_id' : shop_id,
                'start_time' : row['Start'],
                'end_time' : row['End'],
                'duration_minutes':None
            })
        self.msil_break_repository.update_breaks(breaks=breaks,shop_id=shop_id)

        return None

    
    def validation_parser(self,file_obj,shop_id):
        error_remarks=[]

        sheet_models = []
        sheet_variants = []
        sheet_equipments = []
        sheet_parts = []

        part_models={}
        part_variants={}

        recipe_inputs_1={}
        recipe_inputs_2={}
        recipe_outputs_1={}
        recipe_outputs_2={}
        recipe_equipments={}

        me = MasterValidationError()
        try:
            try:
                df_variant = read_excel(file_obj, sheet_name='5.VARIANT', engine='openpyxl')
                df_model = read_excel(file_obj, sheet_name='4.MODEL', engine='openpyxl')
                df_equipment = read_excel(file_obj, sheet_name='1.EQUIPMENT', engine='openpyxl')
                df_part = read_excel(file_obj, sheet_name='2.PART', engine='openpyxl')
                df_recipe = read_excel(file_obj, sheet_name='3.RECIPES', engine='openpyxl')
                df_downtime = read_excel(file_obj, sheet_name='8.DOWNTIME_REASON',engine='openpyxl')
                df_quality = read_excel(file_obj, sheet_name='9.QUALITY_REASON',engine='openpyxl')
                df_shift = read_excel(file_obj, sheet_name='6.SHIFT',engine='openpyxl')
                df_breaks = read_excel(file_obj,sheet_name='7.BREAKS',engine='openpyxl')
            except:
                me.add_error('One of the Master Sheets is missing')
                raise me
            
            variant_headers = {'#','Variant','Common Name'}
            model_headers = {'#','Model','Description'}
            equipment_headers = {'#','Line','Equipment Id','Equipment Name','Equipment group','Efficiency'}
            part_headers = {'#','Part number','Part name','Variant','P.E. Code','Model','Description','Material Type',
                            'Supplier','Origin','Grade','Thickness nominal','Thickness upper',
                            'Thickness lower','Thickness unit','Thickness tolerance','Width nominal','Width upper','Width lower',
                            'Width unit','Width tolerance','Weight','Weight unit'}
            recipe_headers = {'Equipment ID','Data Number','Data Number Description','Variant','Input 1','Input 1 description','Input 1 Qty',
                              'Input 2','Input 2 description','Input 2 Qty','Output 1','Output 1 description','Output 1 Qty','Output 2','Output 2 description',
                              'Output 2 Qty','Input Storage unit Group','Output Storage unit Group'}
            downtime_headers = {'Reason','Remark','Type','Tag'}
            quality_headers = {'Reason','Type','Reason Type'}
            shift_headers = {'Shift','Start','End'}
            break_headers = {'Start','End'}

            variant_missing = variant_headers - set(df_variant.head())
            model_missing = model_headers - set(df_model.head())
            equipment_missing = equipment_headers - set(df_equipment.head())
            part_missing = part_headers - set(df_part.head())
            recipe_missing = recipe_headers - set(df_recipe.head())
            downtime_missing = downtime_headers - set(df_downtime.head())
            quality_missing = quality_headers - set(df_quality.head())
            shift_missing = shift_headers - set(df_shift.head())
            break_missing = break_headers - set(df_breaks.head())

            if variant_missing:
                me.add_error(f"Column(s) {variant_missing} in Variant Sheet")
                raise me
            if model_missing:
                me.add_error(f"Column(s) {model_missing} in Model Sheet")
                raise me
            if equipment_missing:
                me.add_error(f"Column(s) {equipment_missing} in Equipment Sheet")
                raise me
            if part_missing:
                me.add_error(f"Column(s) {part_missing} in Part Sheet")
                raise me
            if recipe_missing:
                me.add_error(f"Column(s) {recipe_missing} in Recipe Sheet")
                raise me
            if downtime_missing:
                me.add_error(f"Column(s) {downtime_missing} in Downtime Reason Sheet")
                raise me
            if quality_missing:
                me.add_error(f"Column(s) {quality_missing} in Quality Reason Sheet")
                raise me
            if shift_missing:
                me.add_error(f"Column(s) {shift_missing} in Shift Sheet")
                raise me
            if break_missing:
                me.add_error(f"Column(s) {break_missing} in Break Sheet")
                raise me
        
                      
            for index, row in df_model.iterrows():
                if self.is_all_null(row):
                    continue
                if notna(row['#']):
                    try:
                        row['#']=int(row['#'])
                    except:
                        error_remarks.append(f"Incorrect # at row {index+2} in Model Sheet")
                else:
                    error_remarks.append(f"Missing # at row {index+2} in Model Sheet")
                if isna(row['Model']):
                    error_remarks.append(f"Missing Model at row {index+2} in Model Sheet")
                else:
                    sheet_models.append(row['Model'])
            
            duplicate_model_ids = df_model[df_model.duplicated(subset='#')].index.tolist()
            if duplicate_model_ids:
                duplicate_model_ids = [i+2 for i in duplicate_model_ids]
                error_remarks.append(f"Duplicate values for # at row(s) {','.join(map(str,duplicate_model_ids))} in Model Sheet")
            
            duplicate_model_names = df_model[df_model.duplicated(subset='Model')].index.tolist()
            if duplicate_model_names:
                duplicate_model_names = [i+2 for i in duplicate_model_names]
                error_remarks.append(f"Duplicate values for Model at row(s) {','.join(map(str,duplicate_model_names))} in Model Sheet")
            

            for index, row in df_variant.iterrows():
                if self.is_all_null(row):
                    continue
                if notna(row['#']):
                    try:
                        row['#']=int(row['#'])
                    except:
                        error_remarks.append(f"Incorrect # at row {index+2} in Variant Sheet")
                else:
                    error_remarks.append(f"Missing # at row {index+2} in Variant Sheet")
                if isna(row['Variant']):
                    error_remarks.append(f"Missing Variant at row {index+2} in Variant Sheet")
                else:
                    sheet_variants.append(row['Variant'])
            
            duplicate_variant_ids = df_variant[df_variant.duplicated(subset='#')].index.tolist()
            if duplicate_variant_ids:
                duplicate_variant_ids = [i+2 for i in duplicate_variant_ids]
                error_remarks.append(f"Duplicate values for # at row(s) {','.join(map(str,duplicate_variant_ids))} in Variant Sheet")
            
            duplicate_variant_names = df_variant[df_variant.duplicated(subset='Variant')].index.tolist()
            if duplicate_variant_names:
                duplicate_variant_names = [i+2 for i in duplicate_variant_ids]
                error_remarks.append(f"Duplicate values for Variant at row(s) {','.join(map(str,duplicate_variant_names))} in Variant Sheet")
            
            
            
            for index, row in df_equipment.iterrows():
                if self.is_all_null(row):
                    continue
                if isna(row['Equipment Id']):
                    error_remarks.append(f"Missing Equipment Id at row {index+2} in Equipment Sheet")
                else:
                    sheet_equipments.append(row['Equipment Id'])
                if isna(row['Line']):
                    error_remarks.append(f"Missing Line at row {index+2} in Equipment Sheet")
                # else:
                #     lines.append(row['Line'])
                if isna(row['Equipment Name']):
                    error_remarks.append(f"Missing Equipment Name at row {index+2} in Equipment Sheet")
                if isna(row['Equipment group']):
                    error_remarks.append(f"Missing Equipment group at row {index+2} in Equipment Sheet")
                if notna(row['Efficiency']):
                    try:
                        row['Efficiency']=int(row['Efficiency'])
                        if row['Efficiency']<0:
                            error_remarks.append(f"Invalid Efficiency at row {index+2} in Equipment Sheet")
                    except:
                        error_remarks.append(f"Invalid Efficiency at row {index+2} in Equipment Sheet")

            
            duplicate_equipment_ids = df_equipment[df_equipment.duplicated(subset='Equipment Id')].index.tolist()
            if duplicate_equipment_ids:
                duplicate_equipment_ids = [i+2 for i in duplicate_equipment_ids]
                error_remarks.append(f"Duplicate values for Equipment Id at row(s) {','.join(map(str,duplicate_equipment_ids))} in Equipment Sheet")
            
            duplicate_equipment_names = df_equipment[df_equipment.duplicated(subset='Equipment Name')].index.tolist()
            if duplicate_equipment_names:
                duplicate_equipment_names = [i+2 for i in duplicate_equipment_names]
                error_remarks.append(f"Duplicate values for Equipment name at row(s) {','.join(map(str,duplicate_equipment_names))} in Equipment Sheet")
            
            
            part_number = df_part['Part number'].tolist()
            get_existing_part_number = self.msil_part_repository.check_existing_part_for_different_shops(part_numbers=part_number,shop_id= shop_id)
            if get_existing_part_number:
                error_remarks.append(f"Part numbers {get_existing_part_number} already exists in different shops.")
            for index, row in df_part.iterrows():
                if self.is_all_null(row):
                    continue
                if isna(row['Part number']):
                    error_remarks.append(f"Missing Part number at row {index+2} in Part Sheet")
                else:
                    sheet_parts.append(row['Part number'])
                if isna(row['Part name']):
                    error_remarks.append(f"Missing Part name at row {index+2} in Part Sheet")
                if notna(row['Variant']):
                    if part_variants.get(row['Variant'],None)==None:
                        part_variants[row['Variant']]=[index+2]
                    else:
                        part_variants[row['Variant']].append(index+2)
                if isna(row['P.E. Code']):
                    error_remarks.append(f"Missing P.E. Code at row {index+2} in Part Sheet")
                if isna(row['Model']):
                    error_remarks.append(f"Missing Model at Row {index+2} in Part Sheet")
                else:
                    if part_models.get(row['Model'],None) == None:
                        part_models[row['Model']]=[index+2]
                    else:
                        part_models[row['Model']].append(index+2)
                
                if notna(row['Thickness nominal']):
                    try:
                        row['Thickness nominal']=float(row['Thickness nominal'])
                        if row['Thickness nominal']<0:
                            error_remarks.append(f"Invalid Thickness nominal at row {index+2} in Part Sheet")
                    except:
                        error_remarks.append(f"Invalid Thickness nominal at row {index+2} in Part Sheet")
                if notna(row['Thickness upper']):
                    try:
                        row['Thickness upper']=float(row['Thickness upper'])
                        if row['Thickness upper']<0:
                            error_remarks.append(f"Invalid Thickness upper at row {index+2} in Part Sheet")
                    except:
                        error_remarks.append(f"Invalid Thickness upper at row {index+2} in Part Sheet")
                if notna(row['Thickness lower']):
                    try:
                        row['Thickness lower']=float(row['Thickness lower'])
                        if row['Thickness lower']<0:
                            error_remarks.append(f"Invalid Thickness lower at row {index+2} in Part Sheet")
                    except:
                        error_remarks.append(f"Invalid Thickness lower at row {index+2} in Part Sheet")
                if notna(row['Thickness tolerance']):
                    if str(row['Thickness tolerance']).strip().upper() not in ('ABSOLUTE','RELATIVE'):
                        error_remarks.append(f"Invalid Thickness tolerance at row {index+2} in Part Sheet")
                
                if notna(row['Width nominal']):
                    try:
                        row['Width nominal']=float(row['Width nominal'])
                        if row['Width nominal']<0:
                            error_remarks.append(f"Invalid Width nominal at row {index+2} in Part Sheet")
                    except:
                        error_remarks.append(f"Invalid Width nominal at row {index+2} in Part Sheet")
                if notna(row['Width upper']):
                    try:
                        row['Width upper']=float(row['Width upper'])
                        if row['Width upper']<0:
                            error_remarks.append(f"Invalid Width upper at row {index+2} in Part Sheet")
                    except:
                        error_remarks.append(f"Invalid Width upper at row {index+2} in Part Sheet")
                if notna(row['Width lower']):
                    try:
                        row['Width lower']=float(row['Width lower'])
                        if row['Width lower']<0:
                            error_remarks.append(f"Invalid Width lower at row {index+2} in Part Sheet")
                    except:
                        error_remarks.append(f"Invalid Width lower at row {index+2} in Part Sheet")
                if notna(row['Width tolerance']):
                    if str(row['Width tolerance']).strip().upper() not in ('ABSOLUTE','RELATIVE'):
                        error_remarks.append(f"Invalid Width tolerance at row {index+2} in Part Sheet")
                
                if notna(row['Weight']):
                    try:
                        row['Weight']=float(row['Weight'])
                        if row['Weight']<0:
                            error_remarks.append(f"Invalid Weight at row {index+2} in Part Sheet")
                    except:
                        error_remarks.append(f"Invalid Weight at row {index+2} in Part Sheet")
                    
            duplicate_material_codes = df_part[df_part.duplicated(subset='Part number')].index.tolist()
            if duplicate_material_codes:
                duplicate_material_codes = [i+2 for i in duplicate_material_codes]
                error_remarks.append(f"Duplicate values for Part number at row(s) {','.join(map(str,duplicate_material_codes))} in Part Sheet")
        

            unknown_models = set(part_models.keys()) - set(sheet_models)
            for item in unknown_models:
                for i in part_models[item]:
                    error_remarks.append(f"Model not present in Excel for Row {i} in Part Sheet")
            
            unknown_variants = set(part_variants.keys()) - set(sheet_variants)
            for item in unknown_variants:
                for i in part_variants[item]:
                    error_remarks.append(f"Variant not present in Excel for Row {i} in Part Sheet")
            
            
            for index, row in df_recipe.iterrows():
                if self.is_all_null(row):
                    continue
                
                if isna(row['Equipment ID']):
                    error_remarks.append(f"Missing Equipment ID at row {index+2} in Recipe Sheet")
                else:
                    if recipe_equipments.get(row['Equipment ID'],None) == None:
                        recipe_equipments[row['Equipment ID']]=[index+2]
                    else:
                        recipe_equipments[row['Equipment ID']].append(index+2)

                if notna(row['Data Number']):
                    try:
                        row['Data Number']=str(row['Data Number'])
                    except:
                        error_remarks.append(f"Incorrect Data Number at row {index+2} in Recipe Sheet")
                else:
                    error_remarks.append(f"Missing Data Number at row {index+2} in Recipe Sheet")
                
                if isna(row['Input 1']):
                    error_remarks.append(f"Missing Input 1 at Row {index+2} in Recipe Sheet")
                else:
                    if recipe_inputs_1.get(row['Input 1'],None)==None:
                        recipe_inputs_1[row['Input 1']]=[index+2]
                    else:
                        recipe_inputs_1[row['Input 1']].append(index+2)
                
                if notna(row['Input 1 Qty']):
                    try:
                        row['Input 1 Qty']=int(row['Input 1 Qty'])
                        if row['Input 1 Qty']<0:
                            error_remarks.append(f"Incorrect Input 1 Qty at row {index+2} in Recipe Sheet")
                    except:
                        error_remarks.append(f"Incorrect Input 1 Qty at row {index+2} in Recipe Sheet")
                
                if notna(row['Input 2']):
                    if recipe_inputs_2.get(row['Input 2'],None)==None:
                        recipe_inputs_2[row['Input 2']]=[index+2]
                    else:
                        recipe_inputs_2[row['Input 2']].append(index+2)
                
                if notna(row['Input 2 Qty']):
                    try:
                        row['Input 2 Qty']=int(row['Input 2 Qty'])
                        if row['Input 2 Qty']<0:
                            error_remarks.append(f"Incorrect Input 2 Qty at row {index+2} in Recipe Sheet")
                    except:
                        error_remarks.append(f"Incorrect Input 2 Qty at row {index+2} in Recipe Sheet")
                
                if isna(row['Output 1']):
                    error_remarks.append(f"Missing Output 1 at Row {index+2} in Recipe Sheet")
                else:
                    if recipe_outputs_1.get(row['Output 1'],None)==None:
                        recipe_outputs_1[row['Output 1']]=[index+2]
                    else:
                        recipe_outputs_1[row['Output 1']].append(index+2)
                
                if notna(row['Output 1 Qty']):
                    try:
                        row['Output 1 Qty']=int(row['Output 1 Qty'])
                        if row['Output 1 Qty']<0:
                            error_remarks.append(f"Incorrect Output 1 Qty at row {index+2} in Recipe Sheet")
                    except:
                        error_remarks.append(f"Incorrect Output 1 Qty at row {index+2} in Recipe Sheet")
                
                if notna(row['Output 2']):
                    if recipe_outputs_2.get(row['Output 2'],None)==None:
                        recipe_outputs_2[row['Output 2']]=[index+2]
                    else:
                        recipe_outputs_2[row['Output 2']].append(index+2)
                
                if notna(row['Output 2 Qty']):
                    try:
                        row['Output 2 Qty']=int(row['Output 2 Qty'])
                        if row['Output 2 Qty']<0:
                            error_remarks.append(f"Incorrect Output 2 Qty at row {index+2} in Recipe Sheet")
                    except:
                        error_remarks.append(f"Incorrect Output 2 Qty at row {index+2} in Recipe Sheet")
                
                if notna(row['Variant']):
                    if str(row['Variant']).strip().upper() not in ('TRUE','FALSE'):
                        error_remarks.append(f"Incorrect Variant at row {index+2} in Recipe Sheet")
                
            duplicate_recipe_combinations = df_recipe[df_recipe.duplicated(subset=['Equipment ID','Data Number','Output 1','Output 2'])].index.tolist()
            if duplicate_recipe_combinations:
                duplicate_recipe_combinations = [i+2 for i in duplicate_recipe_combinations]
                error_remarks.append(f"Duplicate values for (Equipment ID, Data Number, Output 1, Output 2) at row(s) {','.join(map(str,duplicate_material_codes))} in Recipe Sheet")
            
        
            unknown_equipments = set(recipe_equipments.keys()) - set(sheet_equipments)
            for item in unknown_equipments:
                for i in recipe_equipments[item]:
                    error_remarks.append(f"Equipment ID not present in Excel for Row {i} in Recipe Sheet")
            
            unknown_input_1 = set(recipe_inputs_1.keys()) - set(sheet_parts)
            for item in unknown_input_1:
                for i in recipe_inputs_1[item]:
                    error_remarks.append(f"Input 1 not present in Excel for Row {i} in Recipe Sheet")
            
            unknown_input_2 = set(recipe_inputs_2.keys()) - set(sheet_parts)
            for item in unknown_input_2:
                for i in recipe_inputs_2[item]:
                    error_remarks.append(f"Input 2 not present in Excel for Row {i} in Recipe Sheet")
            
            unknown_output_1 = set(recipe_outputs_1.keys()) - set(sheet_parts)
            for item in unknown_output_1:
                for i in recipe_outputs_1[item]:
                    error_remarks.append(f"Output 1 not present in Excel for Row {i} in Recipe Sheet")
            
            unknown_output_2 = set(recipe_outputs_2.keys()) - set(sheet_parts)
            for item in unknown_output_2:
                for i in recipe_outputs_2[item]:
                    error_remarks.append(f"Output 2 not present in Excel for Row {i} in Recipe Sheet")

            reason_type_combinations = []
            other_combinations = []

            for index, row  in df_downtime.iterrows():
                if self.is_all_null(row):
                    continue
                if isna(row['Reason']):
                    error_remarks.append(f"Missing Reason at Row {index+2} in Downtime Reason Sheet")
                if isna(row['Type']):
                    error_remarks.append(f"Missing Type at Row {index+2} in Downtime Reason Sheet")
                elif str(row['Type']).strip().lower() not in  ('idle','breakdown','scheduled'):
                    error_remarks.append(f"Invalid Type at Row {index+2} in Downtime Reason Sheet")
                elif notna(row['Reason']):
                    reason_type_combinations.append((row['Reason'],row['Type'],row['Tag']))

                if isna(row['Remark']):
                    error_remarks.append(f"Missing Remark at Row {index+2} in Downtime Reason Sheet")
                elif str(row['Remark']).strip().capitalize()=='Other':
                    other_combinations.append((row['Reason'],row['Type'],row['Tag']))

                if isna(row['Tag']):
                    error_remarks.append(f"Missing Tag at Row {index+2} in Downtime Reason Sheet")
            
            if not error_remarks:
                other_missing = set(reason_type_combinations) - set(other_combinations)
                for item in other_missing:
                    error_remarks.append(f"Other Remark missing for Reason: {item[0]} Type: {item[1]} in Downtime Reason Sheet")
            
            duplicate_downtime_combinations = df_downtime[df_downtime.duplicated(subset=['Reason','Remark','Type'])].index.tolist()
            if duplicate_downtime_combinations:
                duplicate_downtime_combinations = [i+2 for i in duplicate_downtime_combinations]
                error_remarks.append(f"Duplicate values for (Reason, Remark, Type) at row(s) {','.join(map(str,duplicate_downtime_combinations))} in Downtime Reason Sheet")
            
            for index, row in df_quality.iterrows():
                if self.is_all_null(row):
                    continue
                if isna(row['Reason']):
                    error_remarks.append(f"Missing Reason at Row {index+2} in Quality Reason Sheet")

                if isna(row['Reason Type']):
                    error_remarks.append(f"Missing Reason Type at Row {index+2} in Quality Reason Sheet")
                elif str(row['Reason Type']).strip().upper() not in ('PUNCHING','UPDATION'):
                    error_remarks.append(f"Invalid Reason Type at Row {index+2} in Quality Reason Sheet")
                
                if isna(row['Type']):
                    error_remarks.append(f"Missing Type at Row {index+2} in Quality Reason Sheet")
                elif str(row['Reason Type']).strip().upper()=='PUNCHING' and str(row['Type']).strip().upper() not in ('REJECT','REWORK'):
                    error_remarks.append(f"Invalid Type at Row {index+2} in Quality Reason Sheet")
                elif str(row['Reason Type']).strip().upper()=='UPDATION' and str(row['Type']).strip().upper() not in ('REJECT','RECYCLE','OK'):
                    error_remarks.append(f"Invalid Type at Row {index+2} in Quality Reason Sheet")

            duplicate_quality_combinations = df_quality[df_quality.duplicated(subset=['Reason','Type','Reason Type'])].index.tolist()
            if duplicate_quality_combinations:
                duplicate_quality_combinations = [i+2 for i in duplicate_quality_combinations]
                error_remarks.append(f"Duplicate values for (Reason, Type, Reason Type) at row(s) {','.join(map(str,duplicate_quality_combinations))} in Quality Reason Sheet")

            for index,row in df_shift.iterrows():
                if self.is_all_null(row):
                    continue
                if isna(row['Shift']):
                    error_remarks.append(f"Missing Shift at Row {index+2} in Shift Sheet")
                
                if isna(row['Start']):
                    error_remarks.append(f"Missing Start at Row {index+2} in Shift Sheet")
                else:
                    try:
                        row['Start'] = datetime.datetime.strptime(str(row['Start']).strip(),'%H:%M:%S').time()
                    except:
                        error_remarks.append(f"Invalid Start at Row {index+2} in Shift Sheet")
                
                if isna(row['End']):
                    error_remarks.append(f"Missing End at Row {index+2} in Shift Sheet")
                else:
                    try:
                        row['End'] = datetime.datetime.strptime(str(row['End']).strip(),'%H:%M:%S').time()
                    except:
                        error_remarks.append(f"Invalid Start at End {index+2} in Shift Sheet")
            
            duplicate_shifts = df_shift[df_shift.duplicated(subset='Shift')].index.tolist()
            if duplicate_shifts:
                duplicate_shifts = [i+2 for i in duplicate_shifts]
                error_remarks.append(f"Duplicate values for Shift at row(s) {','.join(map(str,duplicate_shifts))} in Shift Sheet")
            
            duplicate_shift_start = df_shift[df_shift.duplicated(subset='Start')].index.tolist()
            if duplicate_shift_start:
                duplicate_shift_start = [i+2 for i in duplicate_shift_start]
                error_remarks.append(f"Duplicate values for Start at row(s) {','.join(map(str,duplicate_shift_start))} in Shift Sheet")
            
            duplicate_shift_end = df_shift[df_shift.duplicated(subset='End')].index.tolist()
            if duplicate_shift_end:
                duplicate_shift_end = [i+2 for i in duplicate_shift_end]
                error_remarks.append(f"Duplicate values for End at row(s) {','.join(map(str,duplicate_shift_end))} in Shift Sheet")
            
            for index, row in df_breaks.iterrows():
                if self.is_all_null(row):
                    continue
                if isna(row['Start']):
                    error_remarks.append(f"Missing Start at Row {index+2} in Breaks Sheet")
                else:
                    try:
                        row['Start'] = datetime.datetime.strptime(str(row['Start']).strip(),'%H:%M:%S').time()
                    except:
                        error_remarks.append(f"Invalid Start at Row {index+2} in Breaks Sheet")
                
                if isna(row['End']):
                    error_remarks.append(f"Missing End at Row {index+2} in Breaks Sheet")
                else:
                    try:
                        row['End'] = datetime.datetime.strptime(str(row['End']).strip(),'%H:%M:%S').time()
                    except:
                        error_remarks.append(f"Invalid Start at End {index+2} in Breaks Sheet")
            
            duplicate_breaks_start = df_breaks[df_breaks.duplicated(subset='Start')].index.tolist()
            if duplicate_breaks_start:
                duplicate_breaks_start = [i+2 for i in duplicate_breaks_start]
                error_remarks.append(f"Duplicate values for Start at row(s) {','.join(map(str,duplicate_breaks_start))} in Breaks Sheet")
            
            duplicate_breaks_end = df_breaks[df_breaks.duplicated(subset='End')].index.tolist()
            if duplicate_breaks_end:
                duplicate_breaks_end = [i+2 for i in duplicate_breaks_end]
                error_remarks.append(f"Duplicate values for End at row(s) {','.join(map(str,duplicate_breaks_end))} in Breaks Sheet")

            if not error_remarks:
                return None
            else:
                for r in error_remarks:
                    me.add_error(r)
                raise me

            
        except MasterValidationError:
            errors = ('; '.join(me.get_error_list()))
            # self.msil_status_repository.new_status(date_cur, PlanFileStatusEnum.FAILED,errors, shop_id)
            # self.plan_alert(errors)
            return errors
        # except Exception as e:
        #     return str(e)
    
class MasterValidationError(Exception):
    def __init__(self):
        self.error_list = []
    def add_error(self, error):
        self.error_list.append(error)
    def get_error_list(self):
        return self.error_list
            





